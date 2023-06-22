import React, { useEffect, useState } from 'react'
import { useDispatch, useSelector } from "react-redux"
import './comments.scss'
import DisplayComments from './DisplayComments'
import { ActionProvider } from './ActionContext'
import Input from './Input'
import CommentFilter from './CommentFilter'
import { getMinistryRestrictedTagList } from "../../../../helper/FOI/helper";
import { fetchFOIRequestNotesList } from '../../../../apiManager/services/FOI/foiRequestNoteServices'
import Loading from "../../../../containers/Loading";


export const CommentSection = ({
  commentsArray,
  currentUser,
  setComment,
  signinUrl,
  signupUrl,
  customInput,
  requestid,
  ministryId,
  bcgovcode,
  iaoassignedToList,
  ministryAssignedToList,
  requestNumber,
  //Handles Navigate Away
  setEditorChange,
  removeComment,
  setRemoveComment,
  restrictionType,
  isRestricted
}) => {
  const requestWatchers = useSelector((state) => state.foiRequests.foiWatcherList);
  const [showaddbox, setshowaddbox] = useState(false)
  const [comments, setcomments] = useState([])
  let _commentcategory = sessionStorage.getItem('foicommentcategory')
  const [filterValue, setfilterValue] = useState(_commentcategory === '' || _commentcategory === undefined || _commentcategory === null  ? 1 : parseInt(_commentcategory))
  const [filterkeyValue, setfilterkeyValue] = useState("")
  const dispatch = useDispatch();
  useEffect(() => {
    if(commentsArray) {
    let _commentsbyCategory = parseInt(filterValue) === -1 ? commentsArray :  commentsArray.filter(c => c.commentTypeId === parseInt(filterValue))
    let _filteredcomments = filterkeyValue === "" ? _commentsbyCategory : _commentsbyCategory.filter(c => c.text.toLowerCase().indexOf(filterkeyValue.toLowerCase()) > -1)
    let filteredcomments = filterkeyinCommentsandReplies(_commentsbyCategory,_filteredcomments)        
    setcomments(filteredcomments)
    } else {
      dispatch(fetchFOIRequestNotesList(requestid, ministryId));
    }      
  }, [filterValue,commentsArray ,filterkeyValue])
  let restrictedReqTaglist = useSelector((state) => state.foiRequests.restrictedReqTaglist);

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
          restrictedReqTaglist={restrictionType == "ministry"?getMinistryRestrictedTagList():restrictedReqTaglist} isRestricted={isRestricted} />}
        </div> :null}
        <div className="displayComments">
          <div className="filterComments" >
            <CommentFilter oncommentfilterchange={onfilterchange} filterValue={filterValue === null ? 1 : filterValue} oncommentfilterkeychange={(k)=>{setfilterkeyValue(k)}}/>
          </div>
          <DisplayComments comments={comments} bcgovcode={bcgovcode} currentUser={currentUser} iaoassignedToList={iaoassignedToList} ministryAssignedToList={ministryAssignedToList} 
           restrictedReqTaglist={restrictionType == "ministry"?getMinistryRestrictedTagList():restrictedReqTaglist} isRestricted={isRestricted}
          //Handles Navigate Away
          setEditorChange={setEditorChange} removeComment={removeComment} setRemoveComment={setRemoveComment} />
        </div>

      </div>
    </ActionProvider>
    </>
  )
}

export default CommentSection