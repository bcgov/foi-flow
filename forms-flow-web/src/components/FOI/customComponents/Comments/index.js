import React, { useEffect, useState } from 'react'
import { useDispatch, useSelector } from "react-redux"
import './comments.scss'
import DisplayComments from './DisplayComments'
import { ActionProvider } from './ActionContext'
import Input from './Input'
import CommentFilter from './CommentFilter'
import { getMinistryRestrictedTagList, getCommentTypeIdByName, getCommentTypeFromId } from "../../../../helper/FOI/helper";
import Loading from "../../../../containers/Loading";
//import { CommentTypes } from '../../../../constants/FOI/enum' 
import {fetchFOICommentTypes} from "../../../../apiManager/services/FOI/foiMasterDataServices";



export const CommentSection = ({
  commentsArray,
  currentUser,
  setComment,
  signinUrl,
  signupUrl,
  bcgovcode,
  customInput,
  requestid,
  ministryId,
  iaoassignedToList,
  ministryAssignedToList,
  requestNumber,
  //Handles Navigate Away
  setEditorChange,
  removeComment,
  setRemoveComment,
  restrictionType,
  isRestricted,
  isMinistry,
  commentTypes
}) => {
  const requestWatchers = useSelector((state) => state.foiRequests.foiWatcherList);
  const [showaddbox, setshowaddbox] = useState(false)
  const [comments, setcomments] = useState([])
  const [commentTypeId, setCommentTypeId] = useState(1);
  
  let _commentcategory = sessionStorage.getItem('foicommentcategory')
  const [filterValue, setfilterValue] = useState(_commentcategory === '' || _commentcategory === undefined || _commentcategory === null  ? 1 : parseInt(_commentcategory))
  const [filterkeyValue, setfilterkeyValue] = useState("")

  // useEffect(() => {
  //   console.log("setTeamTagList useeffect")
  //   setTeamTagList()
  // }, [])

  useEffect(() => {
    let _commentsbyCategory = filterCommentFn() 
    let _filteredcomments = filterkeyValue === "" ? _commentsbyCategory : (_commentsbyCategory.filter(c => c.text.toLowerCase().indexOf(filterkeyValue.toLowerCase()) > -1
    || getCommentTypeFromId(commentTypes, c.commentTypeId)?.indexOf(filterkeyValue.toLowerCase()) > -1))
    let filteredcomments = filterkeyinCommentsandReplies(_commentsbyCategory,_filteredcomments)        
    setcomments(filteredcomments)
  }, [filterValue,commentsArray ,filterkeyValue])
  let restrictedReqTaglist = useSelector((state) => state.foiRequests.restrictedReqTaglist);


  const filterCommentFn = () => {
    if(parseInt(filterValue) === -1){
      if(isMinistry)
        return commentsArray.filter(c => c.commentTypeId !== getCommentTypeIdByName(commentTypes, "IAO Internal") && 
            c.commentTypeId !== getCommentTypeIdByName(commentTypes, "IAO Peer Review") )
      else
        return commentsArray.filter(c => c.commentTypeId !== getCommentTypeIdByName(commentTypes,"Ministry Internal") && 
            c.commentTypeId !== getCommentTypeIdByName(commentTypes, "Ministry Peer Review"))
      //return commentsArray;
    }    
    else{
      if(parseInt(filterValue) === 1){
        if(isMinistry)
          return commentsArray.filter(c => c.commentTypeId === parseInt(filterValue) || 
            c.commentTypeId === getCommentTypeIdByName(commentTypes, "Ministry Internal") || 
              c.commentTypeId === getCommentTypeIdByName(commentTypes, "Ministry Peer Review") )
        else
          return commentsArray.filter(c => c.commentTypeId === parseInt(filterValue) || 
            c.commentTypeId === getCommentTypeIdByName(commentTypes,"IAO Internal") || 
              c.commentTypeId === getCommentTypeIdByName(commentTypes, "IAO Peer Review"))
      }
      else
        return commentsArray.filter(c => c.commentTypeId === parseInt(filterValue))
    }
  }

  const onfilterchange = (_filterValue) => { 
    sessionStorage.setItem('foicommentcategory',_filterValue)   
    setfilterValue(_filterValue)       
    setcomments([])
  }

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
    <ActionProvider
      currentUser={currentUser}
      setComment={setComment}
      comments={comments}
      signinUrl={signinUrl}
      signupUrl={signupUrl}
      customInput={customInput}
      requestid={requestid}
      ministryId={ministryId}
      //Handles Navigate Away
      setEditorChange={setEditorChange}
      removeComment={removeComment}
      setRemoveComment={setRemoveComment}
    >
      <div className="section">
        <div className="foi-request-review-header-row1">
          <div className="col-9 foi-request-number-header">
            <h1 className="foi-review-request-text foi-ministry-requestheadertext">{getRequestNumber()}</h1>
          </div>
          <div className="col-3 addcommentBox">
            <button type="button" style={{ display: !showaddbox ? 'block' : 'none' }} className="btn foi-btn-create addcomment" onClick={() => { !showaddbox ? setshowaddbox(true) : setshowaddbox(false); }}>+ Add Comment</button>
          </div>
        </div>
{ showaddbox ?
        <div className="inputBox" style={{ display: showaddbox ? 'block' : 'none' }}>
          {<Input add="add"  bcgovcode={bcgovcode} iaoassignedToList={iaoassignedToList} ministryAssignedToList={ministryAssignedToList} //Handles Navigate Away
          setEditorChange={setEditorChange} removeComment={removeComment} setRemoveComment={setRemoveComment} 
          restrictedReqTaglist={restrictionType == "ministry"?getMinistryRestrictedTagList():restrictedReqTaglist} 
          isRestricted={isRestricted} isMinistry={isMinistry} setshowaddbox={setshowaddbox} commentTypes={commentTypes} 
          commentTypeId={commentTypeId} setCommentTypeId={setCommentTypeId} />}
        </div> :null}
        <div className="displayComments">
          <div className="filterComments" >
            <CommentFilter oncommentfilterchange={onfilterchange} filterValue={filterValue === null ? 1 : filterValue} 
              oncommentfilterkeychange={(k)=>{setfilterkeyValue(k)}} isMinistry={isMinistry} />
          </div>
          <DisplayComments comments={comments} bcgovcode={bcgovcode} currentUser={currentUser} iaoassignedToList={iaoassignedToList} ministryAssignedToList={ministryAssignedToList} 
           restrictedReqTaglist={restrictionType == "ministry"?getMinistryRestrictedTagList():restrictedReqTaglist} isRestricted={isRestricted}
          //Handles Navigate Away
          setEditorChange={setEditorChange} removeComment={removeComment} setRemoveComment={setRemoveComment}  
          commentTypes={commentTypes} commentTypeId={commentTypeId} setCommentTypeId={setCommentTypeId} isMinistry={isMinistry}/>
        </div>

      </div>
    </ActionProvider>
    </>
  )
}

export default CommentSection