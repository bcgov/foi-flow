from jira import JIRA
import requests
import json
import time



startissueid = 1 #github isssue here start #
endissueid = 4000 #github isssue here END  #
GITHUB_USER = 'abin-aot'
GITHUB_PASSWORD = '<GITHUB PASSOWRD HERE>'
AUTH = (GITHUB_USER, GITHUB_PASSWORD)
gittoken = '---- <github PAT token here> ----'
headers = {'Authorization': 'token ' + gittoken}

jira_connection = JIRA(
    basic_auth=('abin.antony@gov.bc.ca', '----< JIRA TOKEN HERE >-------'),
    server="https://citz-imb.atlassian.net/"
)

ZENHUB_AUTHENTICATION_TOKEN = '---<ZENHUB TOKEN HERE>----'
ZENHUB_REPO_ID = '358004325'# ZEN HUB REPO ID, have to use GITHUB API CURL TO GENERATE - use below curl command
## curl -L -H "Accept: application/vnd.github+json" -H "Authorization: Bearer <token here> https://api.github.com/repos/bcgov/foi-flow
ZENHUB_HEADERS = {
    'X-Authentication-Token': ZENHUB_AUTHENTICATION_TOKEN,
}
REPO = 'bcgov/foi-flow'  # format is username/repo

for issueid in range(startissueid,endissueid):
    try:
        issuetitle = None
        issuebody = None
        zenhubstate =None
        jirastate = None
        estimate = 0
        time.sleep(1)
        print("Fetching issue # {0}".format(issueid))
        issues = 'https://api.github.com/repos/{}/issues/{}'.format("bcgov/foi-flow", issueid)
        #issuerequest = requests.get(issues, auth=AUTH)
        issuerequest = requests.get(issues, headers=headers)
        issuejson = issuerequest.json()
        #print(issuejson['labels'])
        issuelabels = []
        for label in issuejson['labels']:
            #print("Label is {}".format(label['name']))
            issuelabels.append(str(label['name']).replace(" ", ""))
        #print(issuejson['body']) 
        if 'title' in issuejson:
            issuetitle ="{} - {}".format(issueid,issuejson['title']) 
            #print("Issue title is {0}".format(issuejson['title']))

        if 'body' in issuejson:
            issuebody = issuejson['body']

        #print(issuelabels)

        if 'state' in issuejson:
            zenhubstate = issuejson['state']

       
             

        issuetype = 'Task' 

        if  'Story' in issuelabels:
            issuetype = 'Story'
        elif 'Bug' in issuelabels or 'bug' in issuelabels :
            issuetype ='Bug'
        elif 'Epic' in issuelabels:
            issuetype ='Epic'

        #print("Type of issue {0} is {1}".format(issueid,issuetype))
       
        if issuetitle is not None and issuebody is not None and len(issuelabels) > 0:

            zenhub_request = requests.get(
                    'https://api.zenhub.com/p1/repositories/{}/issues/{}'.format(ZENHUB_REPO_ID, issueid),
                    headers=ZENHUB_HEADERS)

            zenhub_json_object = zenhub_request.json()
            if zenhubstate == 'open':

                if zenhub_json_object['pipeline']['name'] == "New Issues" :
                    jirastate = "new issues"
                elif zenhub_json_object['pipeline']['name'] == "Icebox" :
                    jirastate = "icebox"
                elif zenhub_json_object['pipeline']['name'] == "Epics" :
                    jirastate = "epics"    
                elif zenhub_json_object['pipeline']['name'] == "Retrospective Items" :
                    jirastate = "retrospective Items" 
                elif zenhub_json_object['pipeline']['name'] == "Bugs" :
                    jirastate = "bugs/enhancements"  
                elif zenhub_json_object['pipeline']['name'] == "Product Backlog" :
                    jirastate = "product backlog" 
                elif zenhub_json_object['pipeline']['name'] == "Needs Release Label" :
                    jirastate = "needs release label"
                elif zenhub_json_object['pipeline']['name'] == "In Progress" :
                    jirastate = "in progress" 
                elif zenhub_json_object['pipeline']['name'] == "Waiting for dev release" :
                    jirastate = "waiting for dev release"
                elif zenhub_json_object['pipeline']['name'] == "Review" :
                    jirastate = "review" 
                elif zenhub_json_object['pipeline']['name'] == "UX Assurance" :
                    jirastate = "ux assurance"
                elif zenhub_json_object['pipeline']['name'] == "Ready for QA" :
                    jirastate = "ready for qa"  
                elif zenhub_json_object['pipeline']['name'] == "QA In Progress" :
                    jirastate = "qa in progress"
                else:
                    jirastate = "new issues"      
            elif zenhubstate == "closed"  :
                jirastate = "closed"
            else:
                jirastate = "new issues"  
            #print(zenhub_json_object)
            if 'estimate' in zenhub_json_object:
                estimate = 0 if zenhub_json_object['estimate']['value'] is None else zenhub_json_object['estimate']['value']
                #print(zenhub_json_object['estimate']['value'])
                


            issue_dict = {
                'project': {'key': 'FOIMOD'},
                'summary': issuetitle,
                'description': issuebody,
                'issuetype': {'name': issuetype},
                'customfield_10171':issueid,
                'customfield_10172':estimate,
                "customfield_10173": issuelabels,
                
            }

            new_issue = jira_connection.create_issue(fields=issue_dict) 
            jira_connection.transition_issue(new_issue, transition=jirastate)       
            time.sleep(1)
            
            comments = 'https://api.github.com/repos/{}/issues/{}/comments'.format("bcgov/foi-flow", issueid)
            #commentrequest = requests.get(comments, auth=AUTH)
            commentrequest = requests.get(comments, headers=headers)
            commentsjson = commentrequest.json()
            
            for comment in commentsjson:
                githubcomment = "Actually commented by {} on github as follows. \n {}".format(comment['user']['login'],comment['body'])
                jira_connection.add_comment(new_issue,githubcomment)
                #print(comment['body'])
        else:
            print("No title, body found for {0}".format(issueid))
    except  Exception as e:
        print("An exception occurred while processing issue # {} , {}".format(issueid,str(e)))
    print('################## loop completed for {} #################### \n'.format(issueid))
    