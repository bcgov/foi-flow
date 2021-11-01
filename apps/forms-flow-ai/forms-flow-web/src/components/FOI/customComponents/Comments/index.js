import React, { useEffect, useState } from 'react'
import  './comments.scss'
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
  customInput
}) => {
  const [comments, setComments] = useState(commentsArray)
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
    >
      <div className="section">
        <div className="inputBox">
          {signupUrl && !currentUser ? <SignField /> : <Input />}
        </div>
        <div className="displayComments">
          <DisplayComments comments={comments} />
        </div>
      </div>
    </ActionProvider>
  )
}

export default CommentSection