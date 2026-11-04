"""Request handling for the payment SLA backfill endpoints, kept free of Flask so it can be tested directly.

Two steps, like the CLI: a dry run returns the report and a plan hash, and an apply must quote that hash. The
apply refuses (409) and writes nothing when the plan has changed since the dry run.
"""
import os

from request_api.services.paymentslabackfillservice import (
    BackfillSourceError, CamundaFeeSource, FoiPaymentSource, N8NPaymentSlaStore, PaymentSlaBackfill, PlanChangedError,
    PLAN_HASH)

ENABLED_VARIABLE = 'PAYMENT_SLA_BACKFILL_ENABLED'
MAX_MINISTRY_REQUESTS = 500
DRY_RUN_FIELDS = ('include_expired', 'ministry_request_ids')


def enabled():
    """The endpoints exist only while this one-time tool is switched on (off by default)."""
    return (os.getenv(ENABLED_VARIABLE) or '').strip().lower() == 'true'


def parse_options(body, apply):
    """Validate the JSON body. Returns ``(options, None)`` or ``(None, message)``."""
    body = {} if body is None else body
    if not isinstance(body, dict):
        return None, 'The body must be a JSON object'
    allowed = DRY_RUN_FIELDS + (('plan_hash',) if apply else ())
    unknown = sorted(set(body) - set(allowed))
    if unknown:
        return None, 'Unknown field(s): %s' % ', '.join(unknown)
    include_expired = body.get('include_expired', False)
    if not isinstance(include_expired, bool):
        return None, 'include_expired must be true or false'
    ids = body.get('ministry_request_ids', [])
    if (not isinstance(ids, list) or len(ids) > MAX_MINISTRY_REQUESTS
            or any(isinstance(i, bool) or not isinstance(i, int) or i <= 0 for i in ids)):
        return None, 'ministry_request_ids must be a list of up to %d positive integers' % MAX_MINISTRY_REQUESTS
    options = {'include_expired': include_expired, 'ministry_request_ids': sorted(set(ids))}
    if apply:
        plan_hash = body.get('plan_hash')
        if not isinstance(plan_hash, str) or not PLAN_HASH.match(plan_hash.strip().lower()):
            return None, 'plan_hash from the reviewed dry run is required to apply'
        options['plan_hash'] = plan_hash.strip().lower()
    return options, None


def execute(options, apply, operator, camunda=None, foi=None, store=None):
    """Run the backfill. Returns ``(http_status, payload, report)``; ``report`` is None when there is none."""
    own_foi = foi is None
    foi = foi or FoiPaymentSource()
    try:
        backfill = PaymentSlaBackfill(
            camunda or CamundaFeeSource(), foi, store or N8NPaymentSlaStore(), apply=apply,
            include_expired=options['include_expired'], ministry_request_ids=options['ministry_request_ids'],
            operator=operator, confirm_plan=options.get('plan_hash'))
        report = backfill.run()
    except PlanChangedError as exc:
        payload = {'status': False, 'message': 'The plan changed since the dry run; nothing was written. '
                                               'Review the new dry run and confirm its plan_hash.',
                   'expected_plan_hash': exc.expected, 'plan_hash': exc.report['run']['plan_hash'],
                   'summary': exc.report['summary']}
        return 409, payload, exc.report
    except BackfillSourceError as exc:
        return 502, {'status': False, 'message': 'Backfill aborted, rows written before the failure are kept and '
                                                 'a rerun is safe: %s' % exc}, None
    finally:
        if own_foi:
            foi.close()
    payload = {'status': report['summary']['errors'] == 0, 'plan_hash': report['run']['plan_hash'],
               'applied': apply, 'manual_review_required': report['manual_review_required'], 'report': report}
    return 200, payload, report
