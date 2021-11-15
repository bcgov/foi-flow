import React, { useContext } from 'react'
import  './comments.scss'
import InputField from './InputField'
import { ActionContext } from './ActionContext'
import 'reactjs-popup/dist/index.css'
import CommentStructure from './CommentStructure'

const DisplayComments = ({ comments, bcgovcode,currentUser }) => {
   
  comments =  comments.sort(function(a, b) { 
      return b.commentId - a.commentId;
    });

  const actions = useContext(ActionContext)
  return (
    <div>
      {comments.map((i, index) => (
       

        <div key={i.commentId} className="commentsection" data-comid={i.commentId}>
          {actions.editArr.filter((id) => id === i.commentId).length !== 0 ? (
            actions.customInput ? (
              actions.customInput({
                cancellor: i.commentId,
                value: i.text,
                handleCancel: actions.handleCancel,
                submit: actions.submit,
                edit: true
              })
            ) : (
              <InputField cancellor={i.commentId} value={i.text} edit />
            )
          ) : (
           
            <CommentStructure i={i} handleEdit={() => actions.handleAction} totalcommentCount ={ i.replies && i.replies.length > 0 ? -100 : -101 } currentIndex={index} c={false}  bcgovcode={bcgovcode} hasAnotherUserComment={(i.replies.filter(r=>r.userId !== currentUser.userId).length > 0)}/>
          )}
          {actions.replies.filter((id) => id === i.commentId).length !== 0 &&
            (actions.customInput ? (
              actions.customInput({
                cancellor: i.commentId,
                parentId: i.commentId,
                submit: actions.submit,
                handleCancel: actions.handleCancel,
                edit: false
              })
            ) : (
              <InputField cancellor={i.commentId} parentId={i.commentId} />
            ))}
          <div className="replySection">
            {
           i.replies && i.replies.sort((a,b)=>{return a.commentId - b.commentId}) &&
              i.replies.map((a, index) => (
                <div key={a.commentId}>
                  {actions.editArr.filter((id) => id === a.commentId).length !==
                  0 ? (
                    actions.customInput ? (
                      actions.customInput({
                        cancellor: a.commentId,
                        value: a.text,
                        handleCancel: actions.handleCancel,
                        edit: true,
                        parentId: i.commentId,
                        submit: actions.submit
                      })
                    ) : (
                      <InputField
                        cancellor={a.commentId}
                        value={a.text}
                        edit
                        parentId={i.commentId}
                      />
                    )
                  ) : (
                    <CommentStructure
                      i={a}
                      reply
                      parentId={i.commentId}
                      handleEdit={() => actions.handleAction} totalcommentCount ={i.replies.length} currentIndex={index} isreplysection={true} bcgovcode={bcgovcode} hasAnotherUserComment={false}
                    />
                  )}
                  {actions.replies.filter((id) => id === a.commentId).length !==
                    0 &&
                    (actions.customInput ? (
                      actions.customInput({
                        cancellor: a.commentId,
                        parentId: i.commentId,
                        child: true,
                        submit: actions.submit,
                        handleCancel: actions.handleCancel,
                        edit: false
                      })
                    ) : (
                      <InputField
                        cancellor={a.commentId}
                        parentId={i.commentId}
                        child
                      />
                    ))}
                </div>
              ))}
          </div>
        </div>
      ))}
    </div>
  )
}

export default DisplayComments
