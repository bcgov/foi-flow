
from os import stat
from re import VERBOSE
from operator import itemgetter
from request_api.models.FOIRequestComments import FOIRequestComment
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRawRequestComments import FOIRawRequestComment
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.services.assigneeservice import assigneeservice
from request_api.services.watcherservice import watcherservice
import json
from dateutil.parser import parse
import datetime 

from dateutil import parser
from dateutil import tz
from pytz import timezone
import pytz
import maya



class commentservice:
    """ FOI comment management service
    Supports creation, update and delete of comments for both unopened(raw) and opened(ministry) request
    """
    
    def createministryrequestcomment(self, data, userid, type=1):
        version = FOIMinistryRequest.getversionforrequest(data["ministryrequestid"])
        return FOIRequestComment.savecomment(type, data, version, userid) 

    def createrawrequestcomment(self, data, userid, type=1):
        version = FOIRawRequest.getversionforrequest(data["requestid"])    
        return FOIRawRequestComment.savecomment(type, data, version, userid) 
    
    def createcomments(self, data, userid, type=2):
        return FOIRequestComment.savecomment(type, data, data['version'], userid) 
    
    def disableministryrequestcomment(self, commentid, userid):
        return FOIRequestComment.disablecomment(commentid, userid) 

    def disablerawrequestcomment(self, commentid, userid):
        return FOIRawRequestComment.disablecomment(commentid, userid)     
        
    def updateministryrequestcomment(self, commentid, data, userid):
        FOIRequestComment.disablecomment(commentid, userid, "edit")
        return FOIRequestComment.updatecomment(commentid, data, userid) 

    def updaterawrequestcomment(self, commentid, data, userid):
        FOIRawRequestComment.disablecomment(commentid, userid)
        return FOIRawRequestComment.updatecomment(commentid, data, userid)          
        
    def getministryrequestcomments(self, ministryrequestid):
        data = FOIRequestComment.getcomments(ministryrequestid)
        return self.__preparecomments(data)
    
    def getrawrequestcomments(self, requestid):
        data = FOIRawRequestComment.getcomments(requestid)
        return self.__preparecomments(data)        

    def copyrequestcomment(self, ministryrequestid, comments, userid):
        _comments = []        
        for comment in comments:
            commentresponse=FOIRequestComment.savecomment(comment['commentTypeId'], self.__copyparentcomment(ministryrequestid, comment), 1, userid,comment['dateUF']) 
            _comments.append({"ministrycommentid":commentresponse.identifier,"rawcommentid":comment['commentId']})
            if comment['replies']:
                for reply in comment['replies']:
                    response=FOIRequestComment.savecomment(reply['commentTypeId'], self.__copyreplycomment(ministryrequestid, reply, commentresponse.identifier), 1, userid,reply['dateUF'])      
                    _comments.append({"ministrycommentid":response.identifier,"rawcommentid":comment['commentId']})        
        return _comments
    
    def __copyparentcomment(self, ministryrequestid, entry):
        return {
            "ministryrequestid": ministryrequestid,
            "comment": entry['text'],
            "taggedusers": entry['taggedusers']
            }
    
    def __copyreplycomment(self, ministryrequestid, entry, parentcommentid):
        return {
            "ministryrequestid": ministryrequestid,
            "comment": entry['text'],
            "taggedusers": entry['taggedusers'],
            "parentcommentid":parentcommentid
        }
    
    def __preparecomments(self, data):
        comments=[]
        comments = self.__parentcomments(data)
        for entry in data:
            if entry['parentcommentid'] is not None:
                for _comment in comments:
                    if entry['parentcommentid'] == _comment['commentId']:
                        _comment['replies'].append(self.__comment(entry))            
        return comments        
    
    def __parentcomments(self, data):
        parentcomments = []
        for entry in data:
            if entry['parentcommentid'] is None:
                _comment = self.__comment(entry)
                _comment['replies'] = []
                parentcomments.append(_comment)        
        return parentcomments
          
        
    def __comment(self, comment):
        commentcreateddate = maya.parse(comment["created_at"]).datetime(to_timezone='America/Vancouver', naive=False)
        return {
                "userId": comment['createdby'],
                "commentId": comment['commentid'],
                "text": comment['comment'],
                "dateUF":comment["created_at"],
                "date":  commentcreateddate.strftime('%Y %b %d | %I:%M %p'),
                "parentCommentId":comment['parentcommentid'],
                "commentTypeId":comment['commenttypeid'],
                "taggedusers" : comment['taggedusers']
        }     

    def createcommenttagginguserlist(self,type,requestid):
        if type == "ministryrequest":
            watchers = watcherservice().getallministryrequestwatchers(requestid)
            baserequestinfo = FOIMinistryRequest.getmetadata(requestid)
        else:
            watchers = watcherservice().getrawrequestwatchers(requestid)
            baserequestinfo = FOIRawRequest.getmetadata(requestid)
        userlist = []
        watcherteams= []
        if baserequestinfo is not None:
            user= self.__formatuserlist(baserequestinfo['assignedTo'], baserequestinfo['assignedToFirstName'], baserequestinfo['assignedToLastName'])
            userlist.append(user)
            if 'bcgovcode' in baserequestinfo:
                teamname = baserequestinfo['bcgovcode'].lower()+"ministryteam"
            else:
                teamname = baserequestinfo['selectedMinistries'][0]['code'].lower()+"ministryteam"
            ministryteam = assigneeservice().getmembersbygroupname(teamname) 
            for ministry in ministryteam:
                for member in ministry['members']:
                    user= self.__formatuserlist(member['username'], member['firstname'], member['lastname'])
                    userlist.append(user)
            if watchers is not None:
                self.__getwatchernames(watchers,watcherteams, userlist)
        return userlist

    def __getwatchernames(self, watchers, watcherteams, userlist):
        watchergrouplist= list(map(itemgetter('watchedbygroup'), watchers))
        watchergroups = set(watchergrouplist)
        for group in watchergroups:
            watcherteams.append(assigneeservice().getmembersbygroupname(group)) 
        for watcher in watchers:
            #check if user already in list
            existingusernames = list(map(itemgetter('username'), userlist))
            if watcher['watchedby'] not in existingusernames:
                for team in watcherteams:
                    member= list(filter(lambda x: x['username'] == watcher['watchedby'], team[0]['members']))
                    if len(member) > 0:
                        user= self.__formatuserlist(watcher['watchedby'], member[0]['firstname'], member[0]['lastname'])
                        userlist.append(user)
                        break

    def __formatuserlist(self, username, firstname, lastname):
        user={}
        user['username'] = username
        user['firstname'] = firstname
        user['lastname'] = lastname
        user['fullname'] = lastname+", "+firstname
        user['name'] = lastname+", "+firstname
        return user