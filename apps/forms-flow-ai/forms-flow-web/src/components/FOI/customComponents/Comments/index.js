import React, { useEffect, useState } from 'react'
import './comments.scss'
import DisplayComments from './DisplayComments'
import { ActionProvider } from './ActionContext'
import SignField from './SignField'
import Input from './Input'

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
  requestNumber
}) => {
  const [showaddbox, setshowaddbox] = useState(false)

  return (
    <ActionProvider
      currentUser={currentUser}
      setComment={setComment}
      comments={commentsArray}
      signinUrl={signinUrl}
      signupUrl={signupUrl}
      customInput={customInput}
      requestid={requestid}
      ministryId={ministryId}
    >
      <div className="section">
        <div className="foi-request-number-header">
          <h1 className="foi-review-request-text foi-ministry-requestheadertext">{`Request #${requestNumber ? requestNumber :`U-00${requestid}`}`}</h1>
        </div>
        <div className="addcommentBox">
            <button type="button" style={ {display: !showaddbox ? 'block':'none'}} className="btn foi-btn-create addcomment" onClick={()=>{!showaddbox ? setshowaddbox(true):setshowaddbox(false); }}>+ Add Comment</button>
        </div>

        <div className="inputBox" style={ {display: showaddbox ? 'block':'none'}}>
          {<Input add="add" />}
        </div>
        <div className="displayComments">
          <DisplayComments comments={commentsArray} bcgovcode={bcgovcode} currentUser={currentUser} iaoassignedToList={iaoassignedToList} ministryAssignedToList={ministryAssignedToList} />
        </div>

      </div>
    </ActionProvider>
  )
}

export default CommentSection