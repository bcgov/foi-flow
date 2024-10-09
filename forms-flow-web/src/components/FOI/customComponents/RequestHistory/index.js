import React, { useEffect, useState } from 'react'
import './requesthistory.scss'
import { getCommentTypeIdByName, getCommentTypeFromId } from "../../../../helper/FOI/helper";
import { ActionProvider } from '../Comments/ActionContext'
import RequestFilter from './RequestFilter';
import DisplayHistory from './DisplayHistory'

export const RequestHistorySection = ({
  requestHistoryArray,
  currentUser,
  bcgovcode,
  requestid,
  iaoassignedToList,
  ministryAssignedToList,
  requestNumber,
  commentTypes,
  ministryId,
  applicantCorrespondenceTemplates
}) => {
  const [requesthistory, sethistory] = useState([])
  const [filterkeyValue, setfilterkeyValue] = useState("")

  const getTemplateName = (templateId) =>
    applicantCorrespondenceTemplates.find((obj) => obj.templateid === templateId)?.description;
  
  useEffect(() => {
    const _historybyCategory = filterHistory(); 
    
    const _filteredHistory = filterkeyValue
      ? _historybyCategory.filter((c) => {
          const textMatches = c.text?.toLowerCase().includes(filterkeyValue.toLowerCase());
          const typeMatches = getCommentTypeFromId(commentTypes, c.commentTypeId)
            ?.toLowerCase()
            .includes(filterkeyValue.toLowerCase());
          
          const templateName = c.type === 'message' ? getTemplateName(c.templateid) : null;
          const templateMatches = templateName
            ?.toLowerCase()
            .includes(filterkeyValue.toLowerCase());
  
          const responseMatches = c.category === 'response' &&
            "applicant response".includes(filterkeyValue.toLowerCase());
  
          return textMatches || typeMatches || templateMatches || responseMatches;
        })
      : _historybyCategory;
  
    const filteredhistory = filterkeyinCommentsandReplies(_historybyCategory, _filteredHistory);
    sethistory(filteredhistory);
  }, [requestHistoryArray, filterkeyValue]);
  
  const filterHistory = () => {
    return requestHistoryArray.filter(c => c.commentTypeId !== getCommentTypeIdByName(commentTypes,"Ministry Internal") && 
      c.commentTypeId !== getCommentTypeIdByName(commentTypes, "Ministry Peer Review"))
  };

  const filterkeyinCommentsandReplies = (_comments,filtercomments)=>{
      _comments.forEach(_comment=>{
            if(_comment.replies!=undefined && _comment.replies.length > 0 )
            {
                        let _filteredreply = _comment.replies.filter(c => c.text.toLowerCase().indexOf(filterkeyValue.toLowerCase()) > -1)
                        let _parentcomments = filtercomments.filter(fp => fp.commentId == _comment.commentId)

                        if(_filteredreply!=undefined && _filteredreply.length > 0 && _parentcomments.length === 0)
                        {
                          filtercomments.push(_comment)
                        }
                }
          });

    return filtercomments;
  }

  const getRequestNumber = ()=>{
    let requestHeaderString = 'Request #'
    if(requestNumber)
      {
        return requestHeaderString+requestNumber
      }else
      {
        return requestHeaderString+`U-00${requestid}`
      }  
  }

  return (
    <>
    <ActionProvider>
      <div className="section">
        <div className="foi-request-review-header-row1">
          <div className="col-9 foi-request-number-header">
            <h1 className="foi-review-request-text foi-ministry-requestheadertext">{getRequestNumber()}</h1>
          </div>
        </div>
        <div className="displayComments">
          <div className="filterComments" >
            <RequestFilter oncommentfilterkeychange={(k)=>{setfilterkeyValue(k)}} />
          </div>
          <DisplayHistory requesthistory={requesthistory} bcgovcode={bcgovcode} currentUser={currentUser}
            iaoassignedToList={iaoassignedToList} ministryAssignedToList={ministryAssignedToList} 
            commentTypes={commentTypes} ministryId={ministryId} applicantCorrespondenceTemplates={applicantCorrespondenceTemplates}
          />
        </div>
      </div>
    </ActionProvider>
    </>
  )
}

export default RequestHistorySection;
