# Copyright © 2021 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""CLI to backfill the n8n ``foi-payment-sla`` Data Table from Camunda before cutover (G2, G2a, G6).

Dry run is the default and writes nothing. ``--apply`` is required to insert rows.

    python payment_sla_backfill_cli.py                       # dry run, prints the summary
    python payment_sla_backfill_cli.py --apply               # insert the missing ACTIVE rows
    python payment_sla_backfill_cli.py --apply --include-expired

Configuration comes from the environment: BPM_ENGINE_REST_URL, BPM_TOKEN_URL, BPM_CLIENT_ID and
BPM_CLIENT_SECRET (Camunda), the usual DATABASE_* settings (FOI database, read only), and N8N_BASE_URL and
N8N_API_KEY (n8n; N8N_PAYMENT_SLA_TABLE_ID is optional, the table is otherwise found by name).
"""
import argparse
import csv
import json
import sys
from datetime import datetime, timezone

from request_api.services.paymentslabackfillservice import (
    BackfillSourceError, CamundaFeeSource, FoiPaymentSource, N8NPaymentSlaStore, PaymentSlaBackfill,
    format_summary, MANUAL_REVIEW)

EXIT_SOURCE_FAILURE = 1
EXIT_RECORD_ERRORS = 2
EXIT_MANUAL_REVIEW = 3

CSV_COLUMNS = ('process_instance_id', 'ministry_request_id', 'foi_request_id', 'file_number', 'suspended',
               'outcome', 'reason', 'detail', 'expiry_state', 'expires_at', 'sla_row_id')


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--dry-run', action='store_true', help='report only; this is the default')
    mode.add_argument('--apply', action='store_true', help='insert the missing rows into foi-payment-sla')
    parser.add_argument('--include-expired', action='store_true',
                        help='also write EXPIRED rows for payments Camunda has already expired and notified, '
                             'so a late PAID or CANCELLED still finds a row. Never written as ACTIVE.')
    parser.add_argument('--ministry-request-id', type=int, action='append', default=[],
                        help='limit the run to this ministry request (repeatable), e.g. for a canary')
    parser.add_argument('--report-file', help='JSON report path (default: payment_sla_backfill_<mode>_<time>.json)')
    parser.add_argument('--report-csv', help='also write the per-record results as CSV')
    parser.add_argument('--strict', action='store_true',
                        help='exit %d when any record needs manual review' % EXIT_MANUAL_REVIEW)
    return parser.parse_args(argv)


def write_reports(report, json_path, csv_path):
    with open(json_path, 'w', encoding='utf-8') as handle:
        json.dump(report, handle, indent=2, sort_keys=False)
    if csv_path:
        with open(csv_path, 'w', encoding='utf-8', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(report['records'])


def run(args, camunda=None, foi=None, store=None):
    """Run the backfill and return ``(report, exit_code)``. The sources can be injected for tests."""
    backfill = PaymentSlaBackfill(camunda or CamundaFeeSource(), foi or FoiPaymentSource(), store or N8NPaymentSlaStore(),
                                  apply=args.apply, include_expired=args.include_expired,
                                  ministry_request_ids=args.ministry_request_id)
    report = backfill.run()
    review = sum(1 for r in report['records'] if r['outcome'] in MANUAL_REVIEW)
    errors = report['summary']['errors']
    if errors:
        return report, EXIT_RECORD_ERRORS
    return report, EXIT_MANUAL_REVIEW if args.strict and review else 0


def main(argv=None):
    args = parse_args(argv)
    foi = FoiPaymentSource()  # the FOI database is only read, and no Flask app is needed
    try:
        report, code = run(args, foi=foi)
    except BackfillSourceError as exc:
        print('Backfill aborted, rows written before the failure are kept and a rerun is safe: %s' % exc,
              file=sys.stderr)
        return EXIT_SOURCE_FAILURE
    finally:
        foi.close()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    json_path = args.report_file or 'payment_sla_backfill_%s_%s.json' % (report['run']['mode'], stamp)
    write_reports(report, json_path, args.report_csv)
    print(format_summary(report))
    print('Report written to %s' % json_path)
    return code


if __name__ == '__main__':
    sys.exit(main())
