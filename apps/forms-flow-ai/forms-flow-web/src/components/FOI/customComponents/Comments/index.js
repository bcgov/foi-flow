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
  bcgovcode
}) => {
  const [comments, setComments] = useState(commentsArray)
  const [showaddbox, setshowaddbox] = useState(false)
  
  useEffect(() => {
    setComments(commentsArray)
  }, [commentsArray])
  

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
    >
      <div className="section">
        <div className="addcommentBox">
            <button type="button" style={ {display: !showaddbox ? 'block':'none'}} className="btn foi-btn-create addcomment" onClick={()=>{!showaddbox ? setshowaddbox(true):setshowaddbox(false); }}>+ Add Comment</button>
        </div>

        <div className="inputBox" style={ {display: showaddbox ? 'block':'none'}}>
          {<Input />}
        </div>
        <div className="displayComments">
          <DisplayComments comments={comments} bcgovcode={bcgovcode} currentUser={currentUser} />
        </div>

      </div>
    </ActionProvider>
  )
}

export default CommentSection