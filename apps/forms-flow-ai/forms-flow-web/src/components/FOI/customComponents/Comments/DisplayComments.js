import React, { useContext, useState, useEffect } from 'react'
import './comments.scss'
import InputField from './InputField'
import { ActionContext } from './ActionContext'
import 'reactjs-popup/dist/index.css'
import CommentStructure from './CommentStructure'
import { addToFullnameList, getFullnameList } from '../../../../helper/FOI/helper'


const DisplayComments = ({ comments, bcgovcode, currentUser, iaoassignedToList, ministryAssignedToList }) => {

  const [fullnameList, setFullnameList] = useState(getFullnameList);

  const getfullName = (userId) => {
    let user;

    if (fullnameList) {
      user = fullnameList.find(u => u.username === userId);
      return user && user.fullname ? user.fullname : userId;
    } else {

      if (iaoassignedToList.length > 0) {
        addToFullnameList(iaoassignedToList, "iao");
        setFullnameList(getFullnameList());
      }

      if (ministryAssignedToList.length > 0) {
        addToFullnameList(iaoassignedToList, bcgovcode);
        setFullnameList(getFullnameList());
      }

      user = fullnameList.find(u => u.username === userId);
      return user && user.fullname ? user.fullname : userId;
    }
  }

  const showhiddencomments = (e, count) => {
    var hiddencomments = document.getElementsByName('commentsectionhidden')
    if (hiddencomments && Array.from(hiddencomments).filter((_c) => _c.style.display === 'none').length > 0) {
      var cnt = 0
      hiddencomments.forEach(_com => {

        if (cnt < count && _com.style.display === 'none') {
          _com.style.display = 'block';
          cnt++;
        }

      })
      hiddencomments = document.getElementsByName('commentsectionhidden')
      if (Array.from(hiddencomments).filter((_c) => _c.style.display === 'none').length === 0) {
        document.getElementById('showMoreParentComments').style.display = 'none'
        setshowmorehidden(true)
      }
    }
    else {
      document.getElementById('showMoreParentComments').style.display = 'none'
    }

  }


  const [showmorehidden, setshowmorehidden] = useState(false)

  const dynamicIndexFinder = () => {
    var _commentscopy = [...comments]
    var returnindex = 3
    var totalcharacterCount = 0
    var reachedLimit = false;

    _commentscopy.forEach((comment, index) => {

      if (!reachedLimit) {
        totalcharacterCount += comment.text.length

        if (comment.replies && comment.replies.length > 0) {
          comment.replies.forEach((reply) => {
            if (!reachedLimit) {
              totalcharacterCount += reply.text.length
              if (totalcharacterCount > 2000 && index > 3) {
                returnindex = index
                reachedLimit = true
              }
            }
          })
        }

        if (totalcharacterCount > 2000 && index > 3) {
          returnindex = index
          reachedLimit = true
        }
      }

    })

    return returnindex;
  }


  let limit = dynamicIndexFinder()

  useEffect(() => {
    // if(!showmorehidden)
    //   {setshowmorehidden(comments.length < 3)}
  }, [comments])

  const actions = useContext(ActionContext)

  return (
    <div style={{ paddingBottom: '2%', marginBottom: '2%' }}>

      {
        comments.length === 0 ? <div className="nofiltermessage">No comments under this filter category</div> :
       fullnameList && fullnameList.length > 0 ?   comments.map((i, index) => (
            <div key={i.commentId} className="commentsection" data-comid={i.commentId} name={index >= limit ? 'commentsectionhidden' : ""} style={index >= limit && !showmorehidden ? { display: 'none' } : { display: 'block' }}>
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
                  <InputField cancellor={i.commentId} value={i.text} edit fullnameList={fullnameList} />
                )
              ) : (

                <CommentStructure i={i} handleEdit={() => actions.handleAction} totalcommentCount={i.replies && i.replies.length > 0 ? -100 : -101} currentIndex={index} c={false} bcgovcode={bcgovcode} hasAnotherUserComment={(i.replies && i.replies.filter(r => r.userId !== currentUser.userId).length > 0)} fullName={i.commentTypeId === 1 ? getfullName(i.userId) : "FOI App"} />

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
                  <InputField cancellor={i.commentId} parentId={i.commentId} fullnameList={fullnameList} />
                ))}
              <div className="replySection">
                {
                  i.replies && i.replies.sort((a, b) => { return a.commentId - b.commentId }) &&
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
                            fullnameList={fullnameList}
                          />
                        )
                      ) : (
                        <CommentStructure
                          i={a}
                          reply
                          parentId={i.commentId}
                          handleEdit={() => actions.handleAction} totalcommentCount={i.replies.length} currentIndex={index} isreplysection={true} bcgovcode={bcgovcode} hasAnotherUserComment={false} fullName={a.commentTypeId === 1 ? getfullName(a.userId) : "FOI App"}
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
                            fullnameList={fullnameList}
                          />
                        ))}
                    </div>
                  ))}
              </div>
            </div>
            )):null}
      <div id="showMoreParentComments" className="showMoreParentComments" style={!showmorehidden && comments.length > 3 ? { display: 'block' } : { display: 'none' }}>
        <button className="btn foi-btn-create btnshowmore" onClick={(e) => showhiddencomments(e, 5)}>Show more comments</button>
      </div>
    </div>
  )
}

export default DisplayComments
