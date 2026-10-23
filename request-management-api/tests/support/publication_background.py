"""Bounded Eventlet/DB/Redis exercise; invoked only by the isolated test suite."""

import eventlet
eventlet.monkey_patch()

from datetime import datetime, timedelta
import json
import os
import time
import uuid

import redis
from sqlalchemy import text

from wsgi import APP
from request_api.models import db
from request_api.models.FOIRequests import FOIRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIOpenInformationRequests import FOIOpenInformationRequests
from request_api.services.publication_events.consumer import OpenInfoPublicationCompletedConsumer
from request_api.services.publication_events.completed_stream_consumer import PublicationCompletedStreamConsumer
from request_api.services.publication_events.scheduler import PublicationPrePublishingScheduler


class SectionUpdater:
    """Isolate the workflow/API leaf while retaining its real DB section effect.

    The production completion handler and publication version writer are real.
    API/email/workflow orchestration is outside this background driver check.
    """
    def update_section(self, requestid, ministryid, section, data, *args):
        assert section == 'oistatusid'
        ministry = db.session.query(FOIMinistryRequest).filter_by(
            foiministryrequestid=ministryid, foirequest_id=requestid, version=1,
        ).one()
        ministry.oistatus_id = data['oistatusid']
        db.session.commit()
        return {'success': True}, 200


def main():
    suffix = uuid.uuid4().hex
    identifier = 900000000 + int(suffix[:7], 16)
    requested = 'upgrade-background-requested-' + suffix
    completed = 'upgrade-background-completed-' + suffix
    unpublished = 'upgrade-background-unpublished-' + suffix
    group = 'upgrade-background-' + suffix
    os.environ.update({
        'PUBLICATION_PUBLISH_STREAM_NAME': requested,
        'PUBLICATION_PUBLISH_COMPLETED_STREAM_NAME': completed,
        'PUBLICATION_UNPUBLISH_COMPLETED_STREAM_NAME': unpublished,
        'PUBLICATION_COMPLETED_CONSUMER_GROUP': group,
        'PUBLICATION_COMPLETED_CONSUMER_BLOCK_MS': '100',
        'PUBLICATION_COMPLETED_CONSUMER_SLEEP_SECONDS': '0.01',
        'PUBLICATION_PREPUBLISHING_INTERVAL_SECONDS': '1',
        'PUBLICATION_WINDOW_START': '00:00',
        'PUBLICATION_WINDOW_END': '23:59:59.999999',
    })
    broker = redis.Redis.from_url(os.environ['REDIS_URL'], decode_responses=True)
    worker = PublicationCompletedStreamConsumer.from_env(app=APP)
    worker.handlers['openinfo'] = OpenInfoPublicationCompletedConsumer(section_updater=SectionUpdater())
    scheduler = PublicationPrePublishingScheduler.from_env(app=APP)
    try:
        with APP.app_context():
            area = db.session.execute(text('SELECT programareaid FROM "ProgramAreas" WHERE isactive=true LIMIT 1')).scalar_one()
            category = db.session.execute(text('SELECT applicantcategoryid FROM "ApplicantCategories" LIMIT 1')).scalar_one()
            publication_status = db.session.execute(text('SELECT oipublicationstatusid FROM "OpenInfoPublicationStatuses" WHERE name=\'Publish\'')).scalar_one()
            db.session.add(FOIRequest(foirequestid=identifier, version=1, requesttype='general', applicantcategoryid=category))
            db.session.flush()
            db.session.add(FOIMinistryRequest(
                foiministryrequestid=identifier, version=1, filenumber='UPGRADE-' + suffix[:8],
                axisrequestid='UPGRADE-' + suffix[:8], description='Synthetic publication check',
                duedate=datetime.now() + timedelta(days=30), requeststatuslabel='closed',
                requeststatusid=3, programareaid=area, foirequest_id=identifier,
                foirequestversion_id=1, oistatus_id=3, isconsultflag=False,
            ))
            db.session.flush()
            db.session.add(FOIOpenInformationRequests(
                foiopeninforequestid=identifier, version=1, foiministryrequest_id=identifier,
                foiministryrequestversion_id=1, oipublicationstatus_id=publication_status,
                isactive=True, createdby='upgrade-background',
                publicationdate=datetime.now() - timedelta(days=1),
            ))
            db.session.commit()
        worker.start()
        scheduler.start()
        assert worker.thread.is_alive() and scheduler.thread.is_alive()
        deadline = time.monotonic() + 10
        events = []
        while time.monotonic() < deadline:
            events = broker.xrange(requested)
            if events:
                break
            time.sleep(0.02)
        assert events, 'Background scheduler did not publish the due DB record'
        request_event = json.loads(events[0][1]['payload'])
        assert request_event['payload']['foiministryrequest_id'] == identifier
        broker.xadd(completed, {'payload': json.dumps({
            'event_id': str(uuid.uuid4()), 'event_type': 'publication.publish.completed',
            'correlation_id': request_event['correlation_id'],
            'payload': {
                'kind': 'openinfo', 'tenant_id': request_event['payload']['tenant_id'],
                'request_event_id': request_event['event_id'], 'foirequest_id': identifier,
                'foiministryrequest_id': identifier, 'sitemap_page_key': 'sitemaps/upgrade.xml',
            },
        })})
        progressed = False
        while time.monotonic() < deadline:
            with APP.app_context():
                latest = db.session.query(FOIOpenInformationRequests).filter_by(
                    foiopeninforequestid=identifier, isactive=True,
                ).one()
                progressed = latest.version == 2 and latest.processingmessage == 'Published'
                if progressed:
                    assert latest.sitemap_pages == 'upgrade.xml'
                    ministry = db.session.query(FOIMinistryRequest).filter_by(foiministryrequestid=identifier, version=1).one()
                    assert ministry.oistatus_id == 4
            if progressed and broker.xpending(completed, group)['pending'] == 0:
                break
            time.sleep(0.02)
        assert progressed, 'Background consumer did not persist the publication version'
        assert broker.xpending(completed, group)['pending'] == 0
        print('Background scheduler, real publication handler/model, DB effects and Redis acknowledgement passed')
    finally:
        scheduler.stop()
        worker.stop()
        with APP.app_context():
            db.session.rollback()
            db.session.query(FOIOpenInformationRequests).filter_by(foiopeninforequestid=identifier).delete()
            db.session.query(FOIMinistryRequest).filter_by(foiministryrequestid=identifier).delete()
            db.session.query(FOIRequest).filter_by(foirequestid=identifier).delete()
            db.session.commit()
        broker.delete(requested, completed, unpublished)
        broker.close()


if __name__ == '__main__':
    main()
