
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.UnopenedReport import UnopenedReport
from request_api.services.email.senderservice import senderservice
from os import getenv
from datetime import timedelta, date
from jaro import jaro_winkler_metric
import json
import logging
from math import inf

class unopenedreportservice:
    """
    This service generates a report of unopened unactioned requests

    """

    dayscutoff = getenv('UNOPENED_REPORT_CUTOFF_DAYS', 10)
    waitdays = getenv('UNOPENED_REPORT_WAIT_DAYS', 5)
    jarocutoff = getenv('UNOPENED_REPORT_JARO_CUTOFF', 0.8)
    reportemail = getenv('UNOPENED_REPORT_EMAIL_RECIPIENT')


    def generateunopenedreport(self):
        startdate = date.today() - timedelta(days=int(self.dayscutoff))
        enddate = date.today() -  timedelta(days=int(self.waitdays))
        requests = FOIRawRequest.getunopenedunactionedrequests(str(startdate), str(enddate))
        alerts = []
        for request in requests:
            potentialmatches = FOIRawRequest.getpotentialactionedmatches(request)
            if len(potentialmatches) == 0:
                alert = UnopenedReport()
                alert.rawrequestid = request['requestid']
                alert.date = date.today()
                alert.rank = 1
                UnopenedReport.insert(alert)
                alerts.append({"request": request, "rank": 1})
            else:
                highscore = 0
                for match in potentialmatches:
                    match['score'] = jaro_winkler_metric(
                        request['requestrawdata']['descriptionTimeframe']['description'].replace('\n', ' ').replace('\t', ' '),
                        match['requestrawdata']['description']
                    )
                    if match['score'] > highscore:
                        highscore = match['score']
                alert = UnopenedReport()
                alert.rawrequestid = request['requestid']
                alert.date = date.today()
                alert.rank = 2
                alert.potentialmatches = {"highscore": round(highscore, 2), "matches": [{
                    "requestid": m["requestrawdata"]['axisRequestId'],
                    "similarity": round(m['score'], 2)
                } for m in potentialmatches]}
                UnopenedReport.insert(alert)
                alerts.append({"request": request, "rank": 2, "potentialmatches": alert.potentialmatches})
        alerts.sort(key=lambda a : a.get('potentialmatches', {'highscore': 0})['highscore'])
        senderservice().send(
            subject="Intake Unopened Request Report: " + date.today(),
            content=self.generateemailhtml(alerts),
            _messageattachmentlist=[],
            requestjson={"email": self.reportemail, "topic": "Unopened Report"}
        )
        return alerts


    def generateemailhtml(self, alerts):
        emailhtml = """
            <h3>Unopened Report - """ + str(date.today()) + """</h3>

            <p>This is a report for unopened requests in the past """ + self.dayscutoff + """ days that have not yet been actioned.</p>
            <p><b>Rank 1:</b> Very likely to be unactioned — unable to find a request with any matching applicant info</p>
            <table border='1' style='border-collapse:collapse'>
            <tr>
                <th>Unopened ID</th>
                <th>Date Received</th>
                <th>Ministry Selected</th>
                <th>Applicant First Name</th>
                <th>Applicant Last Name</th>
                <th>Payment Status</th>
                <th>Receipt Number</th>
                <th>Amount Paid</th>
                <th>Description</th>
            </tr>
        """
        firstrank2 = True
        print(alerts)
        for alert in alerts:
            if alert.get('potentialmatches') == None:
                emailhtml += '''
                    <tr>
                        <td>U-000''' + str(alert['request']['requestid']) + '''</td>
                        <td>''' + alert['request']['requestrawdata']['receivedDate'] + '''</td>
                        <td>'''
                for m in alert['request']['requestrawdata']['ministry']['selectedMinistry']:
                    emailhtml += (m['code'] + ' ')
                emailhtml += '''</td>
                        <td>''' + alert['request']['requestrawdata']['contactInfo']['firstName'] + '''</td>
                        <td>''' + alert['request']['requestrawdata']['contactInfo']['lastName'] + '''</td>
                        <td>''' + alert['request']['paymentstatus'] + '''</td>
                        <td>''' + alert['request']['txnno'] + '''</td>
                        <td>''' + str(alert['request']['amountpaid']) + '''</td>
                        <td>''' + alert['request']['requestrawdata']['descriptionTimeframe']['description'][0:99] + '''...</td>
                    </tr>
                '''
            else:
                if firstrank2:
                    emailhtml += """</table>
                        <p><b>Rank 2:</b> Possibly unactioned — requests found but some applicant info is mismatching — please double check</p>
                        <table border='1' style='border-collapse:collapse'>
                        <tr>
                            <th>Unopened ID</th>
                            <th>Date Received</th>
                            <th>Ministry Selected</th>
                            <th>Applicant First Name</th>
                            <th>Applicant Last Name</th>
                            <th>Payment Status</th>
                            <th>Receipt Number</th>
                            <th>Amount Paid</th>
                            <th>Potential Matches</th>
                            <th>Description</th>
                        </tr>
                    """
                    firstrank2 = False
                print(alert)
                if alert['potentialmatches']['highscore'] > float(self.jarocutoff):
                    break
                emailhtml += '''
                    <tr>
                        <td>U-000''' + str(alert['request']['requestid']) + '''</td>
                        <td>''' + alert['request']['requestrawdata']['receivedDate'] + '''</td>
                        <td>'''
                for m in alert['request']['requestrawdata']['ministry']['selectedMinistry']:
                    emailhtml += (m['code'] + ' ')
                emailhtml += '''</td>
                        <td>''' + alert['request']['requestrawdata']['contactInfo']['firstName'] + '''</td>
                        <td>''' + alert['request']['requestrawdata']['contactInfo']['lastName'] + '''</td>
                        <td>''' + alert['request']['paymentstatus'] + '''</td>
                        <td>''' + alert['request']['txnno'] + '''</td>
                        <td>''' + str(alert['request']['amountpaid']) + '''</td>
                        <td>
                    '''
                for m in alert['potentialmatches']['matches']:
                    emailhtml += (m['requestid'] + " - similarity: " + str(m['similarity']*100) + "%<br>")
                emailhtml = emailhtml[:-4]
                emailhtml += '''</td>
                        <td>''' + alert['request']['requestrawdata']['descriptionTimeframe']['description'][0:99] + '''...</td>
                    </tr>
                '''
        return emailhtml


    # def isrank2match(self, request, match):
    #     diff = 0
    #     for k, v in request['requestrawdata']['contactInfo'].items():
    #         if v and match['requestrawdata'].get(k, False) != v:
    #             diff += 1
    #             if diff > self.diffcutoff:
    #                 return False
    #     for k, v in request['requestrawdata']['contactInfoOptions'].items():
    #         if v and match['requestrawdata'].get(k, False) != v:
    #             diff += 1
    #             if diff > self.diffcutoff:
    #                 return False
    #     print("rank 2 match")
    #     return True

    # def isrank1match(self, request, match):
    #     print(request['requestrawdata']['receivedDateUF'][0:10])
    #     print(match['requestrawdata']['receivedDateUF'][0:10])
    #     match = (((request['requestrawdata']['contactInfo']['firstName'] == match['requestrawdata']['firstName']
    #               and request['requestrawdata']['contactInfo']['lastName'] == match['requestrawdata']['lastName'])
    #              or request['requestrawdata']['contactInfoOptions']['email'] == match['requestrawdata']['email']
    #              or request['requestrawdata']['contactInfoOptions']['phonePrimary'] == match['requestrawdata']['phonePrimary']
    #              or request['requestrawdata']['contactInfoOptions']['postal'] == match['requestrawdata']['postal']
    #              )
    #         and request['requestrawdata']['receivedDateUF'][0:10] == match['requestrawdata']['receivedDateUF'][0:10])
    #     if match:
    #         print("rank 1 match")
    #     return match
