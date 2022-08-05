import React, { useEffect, useState } from 'react'
import './comments.scss'
import DisplayComments from './DisplayComments'
import { ActionProvider } from './ActionContext'
import Input from './Input'
import CommentFilter from './CommentFilter'


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
  setRemoveComment
}) => {
  const [showaddbox, setshowaddbox] = useState(false)
  const [comments, setcomments] = useState([])
  const [filterValue, setfilterValue] = useState(-1)
  useEffect(() => {
    let _comments = parseInt(filterValue) === -1 ? commentsArray : commentsArray.filter(c => c.commentTypeId === parseInt(filterValue))
    setcomments(_comments)  
  }, [filterValue,commentsArray])

  
 
  const onfilterchange = (e) => {
    let _filterValue = parseInt(e.target.value) 
    setfilterValue(_filterValue)       
    setcomments([])
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
          setEditorChange={setEditorChange} removeComment={removeComment} setRemoveComment={setRemoveComment}/>}
        </div> :null}
        <div className="displayComments">
          <div className="filterComments" >
            <CommentFilter oncommentfilterchange={onfilterchange} filterValue={filterValue}/>
          </div>
          <DisplayComments comments={comments} bcgovcode={bcgovcode} currentUser={currentUser} iaoassignedToList={iaoassignedToList} ministryAssignedToList={ministryAssignedToList} 
          //Handles Navigate Away
          setEditorChange={setEditorChange} removeComment={removeComment} setRemoveComment={setRemoveComment} />
        </div>

      </div>
    </ActionProvider>
  )
}

export default CommentSection