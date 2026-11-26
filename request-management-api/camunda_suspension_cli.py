"""CLI to suspend and reactivate Camunda process instances for the Camunda to n8n migration.

Dry run is the default and changes nothing. ``--apply`` is required to suspend or reactivate, and it must quote the
plan hash printed by the dry run you reviewed (``--confirm-plan``): if the instances to change are no longer the ones
that dry run planned, nothing is changed.

    python camunda_suspension_cli.py preview --report-csv preview.csv                  # read only, every candidate
    python camunda_suspension_cli.py suspend                                           # dry run, prints the plan hash
    python camunda_suspension_cli.py suspend --apply --confirm-plan <hash> --reason CCP-5801
    python camunda_suspension_cli.py suspend --apply --confirm-plan <hash> --reason CCP-5801 --ministry-request-id 1234
    python camunda_suspension_cli.py status                                            # what this tool holds suspended
    python camunda_suspension_cli.py reactivate                                        # dry run
    python camunda_suspension_cli.py reactivate --apply --confirm-plan <hash>

Default scope is foi-fee-processing only. ``--definition foi-request`` / ``foi-request-processing`` add the lifecycle
instances (optional: they do nothing on their own). Only instances this tool suspended (they carry the
``foiMigrationSuspension`` variable) are ever reactivated.

Configuration comes from the environment, the same variables the API already uses: BPM_ENGINE_REST_URL, BPM_TOKEN_URL,
BPM_CLIENT_ID and BPM_CLIENT_SECRET (Camunda), and N8N_BASE_URL and N8N_API_KEY (n8n, read only, for the ownership
check; N8N_PAYMENT_SLA_TABLE_ID is optional). They are not needed with ``--n8n-check skip`` or for lifecycle-only runs.
The FOI database is not used.
"""
import argparse
import csv
import json
import sys
from datetime import datetime, timezone

from request_api.services.camundasuspensionservice import (
    CamundaClient, CamundaSuspension, Ledger, PlanChangedError, PlanTooLargeError, SuspensionSourceError,
    CSV_COLUMNS, DENIED_KEYS, DENIED_REASON, MANUAL_REVIEW, OPTIONAL_KEYS, PLAN_HASH, format_summary)
from request_api.services.paymentslabackfillservice import BackfillSourceError, N8NPaymentSlaStore

EXIT_SOURCE_FAILURE = 1
EXIT_RECORD_ERRORS = 2
EXIT_MANUAL_REVIEW = 3
EXIT_PLAN_CHANGED = 4
EXIT_PLAN_TOO_LARGE = 5


def _add_report_arguments(parser):
    parser.add_argument('--report-file', help='JSON report path (default: camunda_suspension_<command>_<mode>_<time>.json)')
    parser.add_argument('--report-csv', help='also write the per-instance results as CSV')
    parser.add_argument('--strict', action='store_true',
                        help='exit %d when any instance needs manual review' % EXIT_MANUAL_REVIEW)


def _add_selection_arguments(parser):
    parser.add_argument('--ministry-request-id', type=int, action='append', default=[],
                        help='limit the run to this ministry request (repeatable), e.g. for a canary. '
                             'Lifecycle instances carry no ministry request id, so use --process-instance-id for them')
    parser.add_argument('--process-instance-id', action='append', default=[],
                        help='limit the run to this Camunda process instance (repeatable)')
    parser.add_argument('--n8n-check', choices=('on', 'skip'), default='on',
                        help='"skip" does not read n8n (n8n down, or a local Camunda with no n8n). Record why')


def _add_apply_arguments(parser):
    parser.add_argument('--apply', action='store_true', help='make the changes; without it nothing is changed')
    parser.add_argument('--confirm-plan', metavar='PLAN_HASH',
                        help='required with --apply: the plan hash a reviewed dry run printed. Nothing is changed '
                             'if the instances to change are no longer the ones that dry run planned')
    parser.add_argument('--ledger-dir', default='.', help='where the JSONL ledger is written (default: here)')
    parser.add_argument('--pace-ms', type=int, default=50, help='pause between instances when applying (default 50)')
    parser.add_argument('--max-failures', type=int, default=3,
                        help='stop applying after this many instances fail in a row (default 3; 0 = never stop)')
    parser.add_argument('--max-instances', type=int,
                        help='refuse a plan with more instances than this (exit %d)' % EXIT_PLAN_TOO_LARGE)


def _add_suspend_parsers(commands):
    """``preview`` (read only) and ``suspend`` choose instances the same way."""
    for name, text in (('preview', 'list every candidate and the decision for it; read only'),
                       ('suspend', 'suspend the planned instances (dry run unless --apply)')):
        parser = commands.add_parser(name, help=text)
        _add_selection_arguments(parser)
        _add_report_arguments(parser)
        parser.add_argument('--definition', action='append', default=[], metavar='KEY',
                            help='add an optional definition (%s); default is foi-fee-processing only'
                                 % ', '.join(OPTIONAL_KEYS))
        parser.add_argument('--allow-no-n8n-row', action='store_true',
                            help='also suspend fee instances that have no n8n payment row (for example a payment the '
                                 'backfill skipped). Without it they are left alone')
        if name == 'suspend':
            _add_apply_arguments(parser)
            parser.add_argument('--reason',
                                help='required with --apply (for example the change ticket); stored in the marker')


def _build_parser():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    commands = parser.add_subparsers(dest='command', required=True)
    _add_suspend_parsers(commands)

    status = commands.add_parser('status', help='what this tool holds suspended now; read only')
    _add_report_arguments(status)

    reactivate = commands.add_parser('reactivate', help='reactivate what this tool suspended (dry run unless --apply)')
    _add_selection_arguments(reactivate)
    _add_report_arguments(reactivate)
    _add_apply_arguments(reactivate)

    for with_run_id in (status, reactivate):
        with_run_id.add_argument('--run-id', help='only the instances tagged by this run')
    return parser


def _check_definitions(parser, args):
    for key in getattr(args, 'definition', []):
        if key in DENIED_KEYS:
            parser.error('%s cannot be selected: %s' % (key, DENIED_REASON[key]))
        if key not in OPTIONAL_KEYS:
            parser.error('--definition must be one of: %s' % ', '.join(OPTIONAL_KEYS))


def _check_apply(parser, args):
    applying = getattr(args, 'apply', False)
    confirm_plan = getattr(args, 'confirm_plan', None)
    if applying and not confirm_plan:
        parser.error('--apply requires --confirm-plan <plan hash> from a reviewed dry run')
    if applying and args.command == 'suspend' and not (args.reason or '').strip():
        parser.error('--apply requires --reason (for example the change ticket)')
    if confirm_plan and not applying:
        parser.error('--confirm-plan only applies with --apply')
    if confirm_plan and not PLAN_HASH.match(confirm_plan.strip().lower()):
        parser.error('--confirm-plan must be the 16 character plan hash printed by the dry run')


def parse_args(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)
    _check_definitions(parser, args)
    _check_apply(parser, args)
    return args


def write_reports(report, json_path, csv_path):
    with open(json_path, 'w', encoding='utf-8') as handle:
        json.dump(report, handle, indent=2, sort_keys=False)
    if csv_path:
        with open(csv_path, 'w', encoding='utf-8-sig', newline='') as handle:  # BOM: Excel reads it as UTF-8
            writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(report['records'])


def build_tool(args, camunda=None, store_factory=None):
    """The configured tool. The sources can be injected for tests."""
    applying = getattr(args, 'apply', False)
    tool = CamundaSuspension(
        camunda or CamundaClient(),
        store_factory=store_factory or N8NPaymentSlaStore,
        definitions=getattr(args, 'definition', []),
        ministry_request_ids=getattr(args, 'ministry_request_id', []),
        process_instance_ids=getattr(args, 'process_instance_id', []),
        apply=applying, confirm_plan=getattr(args, 'confirm_plan', None), reason=getattr(args, 'reason', None),
        max_instances=getattr(args, 'max_instances', None),
        allow_no_n8n_row=getattr(args, 'allow_no_n8n_row', False),
        n8n_check=getattr(args, 'n8n_check', 'on') != 'skip',
        only_run_id=getattr(args, 'run_id', None), command=args.command,
        max_consecutive_failures=getattr(args, 'max_failures', 3),
        pace_seconds=getattr(args, 'pace_ms', 0) / 1000.0 if applying else 0.0)
    if applying:
        tool.ledger = Ledger(getattr(args, 'ledger_dir', '.'), tool.run_id, args.command)
    return tool


def run(args, camunda=None, store_factory=None):
    """Run the command and return ``(report, exit_code)``."""
    tool = build_tool(args, camunda, store_factory)
    try:
        if args.command in ('preview', 'suspend'):
            report = tool.suspend()
        elif args.command == 'reactivate':
            report = tool.reactivate()
        else:
            report = tool.status()
    finally:
        tool.ledger.close()
    review = sum(1 for r in report['records'] if r['outcome'] in MANUAL_REVIEW)
    if report['summary']['errors']:
        return report, EXIT_RECORD_ERRORS
    return report, EXIT_MANUAL_REVIEW if getattr(args, 'strict', False) and review else 0


def main(argv=None):
    args = parse_args(argv)
    changed = None
    try:
        report, code = run(args)
    except PlanChangedError as exc:
        report, code, changed = exc.report, EXIT_PLAN_CHANGED, exc
    except PlanTooLargeError as exc:
        report, code, changed = exc.report, EXIT_PLAN_TOO_LARGE, exc
    except (SuspensionSourceError, BackfillSourceError) as exc:
        print('Aborted, instances changed before the failure stay changed and a rerun is safe: %s' % exc,
              file=sys.stderr)
        return EXIT_SOURCE_FAILURE
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    json_path = args.report_file or 'camunda_suspension_%s_%s_%s.json' % (args.command, report['run']['mode'], stamp)
    write_reports(report, json_path, args.report_csv)
    print(format_summary(report))
    print('Report written to %s' % json_path)
    if changed:
        print('Nothing was changed: %s. The report above is the new plan; review it and confirm its plan hash.'
              % changed, file=sys.stderr)
    return code


if __name__ == '__main__':
    sys.exit(main())
