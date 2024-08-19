import React, { useContext, useEffect, useState } from 'react'
import './comments.scss'
import InputField from './InputField'
import { ActionContext } from './ActionContext'
import 'reactjs-popup/dist/index.css'
import CommentStructure from './CommentStructure'
import { addToFullnameList, getFullnameList, getCommentTypeIdByName, getIAOTagList, getAssignToList, setTeamTagList } from '../../../../helper/FOI/helper'


const DisplayComments = ({ comments, bcgovcode, currentUser, iaoassignedToList, ministryAssignedToList, restrictedReqTaglist, isRestricted,
  setEditorChange, removeComment, setRemoveComment, commentTypes,commentTypeId, setCommentTypeId, isMinistry}) => {

  const [fullnameList, setFullnameList] = useState(getFullnameList);


  console.log("fullnameList:",fullnameList)

  useEffect(() => {
    console.log("setTeamTagList useeffect", bcgovcode)
    setTeamTagList(bcgovcode)
  }, [fullnameList])

  const finduserbyuserid = (userId) => {
    let user = fullnameList.find(u => u.username === userId);
    return user && user.fullname ? user.fullname : userId;
  }

  const getfullName = (commenttypeid, userId) => {
    if (commenttypeid !== 2 && commenttypeid !== 3) {
      if (fullnameList) {
        return finduserbyuserid(userId)
      } else {

        if (iaoassignedToList.length > 0) {
          addToFullnameList(iaoassignedToList, "iao");
          setFullnameList(getFullnameList());
        }

        if (ministryAssignedToList.length > 0) {
          addToFullnameList(iaoassignedToList, bcgovcode);
          setFullnameList(getFullnameList());
        }

        return finduserbyuserid(userId)
      }
    } else {
      return "Request History"
    }
  }

  const showhiddencomments = (_e, count) => {
    let hiddencomments = document.getElementsByName('commentsectionhidden')
    if (hiddencomments && Array.from(hiddencomments).filter((_c) => _c.style.display === 'none').length > 0) {
      let cnt = 0
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

  const checkcommentlengthforindex = (comment, index) => {
    let commentlenghchecker = new Object()

    commentlenghchecker.totalcharacterCount = comment?.text?.length
    commentlenghchecker.reachedLimit = false
    commentlenghchecker.returnindex = 10
    
    if (commentlenghchecker.totalcharacterCount > 2000 && index > 10) {
      commentlenghchecker.returnindex = index
      commentlenghchecker.reachedLimit = true
      return commentlenghchecker
    }

    if (comment.replies && comment.replies.length > 0) {
      comment.replies.forEach((reply) => {
        if (!commentlenghchecker.reachedLimit) {
          commentlenghchecker.totalcharacterCount += reply.text?.length
          if (commentlenghchecker.totalcharacterCount > 2000 && index > 10) {
            commentlenghchecker.returnindex = index
            commentlenghchecker.reachedLimit = true
            return commentlenghchecker
          }
        }
      })
    }

    return commentlenghchecker
  }

  const dynamicIndexFinder = () => {
    let _commentscopy = [...comments]
    let returnindex = 10
    let totalcharacterCount = 0
    let reachedLimit = false;

    _commentscopy.forEach((comment, index) => {

      if (!reachedLimit) {
        let commentlenghchecker = checkcommentlengthforindex(comment, index)
        totalcharacterCount += commentlenghchecker.totalcharacterCount
        reachedLimit = commentlenghchecker.reachedLimit
        returnindex = commentlenghchecker.returnindex
      }

    })

    return returnindex;
  }


  let limit = dynamicIndexFinder()

  const gettotalcommentflag = (i) => {
    return i.replies?.length > 0 ? -100 : -101
  }

  

  const renderreplies = (i) => {

    return (i.replies && i.replies.sort((a, b) => { return a.commentId - b.commentId }) &&
      i.replies.map((a, replyindex) => (
        <div key={a.commentId}>
          { fullnameList?.length > 0 && actions.editArr.filter((id) => id === a.commentId).length !==
            0 ? (
            <InputField
              cancellor={a.commentId}
              inputvalue={a.text}
              edit
              parentId={i.commentId}
              fullnameList={fullnameList}
              restrictedReqTaglist={restrictedReqTaglist}
              isRestricted = {isRestricted}
              //Handles Navigate Away
              setEditorChange={setEditorChange} removeComment={removeComment} setRemoveComment={setRemoveComment}
              commentTypeId={i.commentTypeId}
              newCommentTypeId={commentTypeId}
              setCommentTypeId={setCommentTypeId}
              commentTypes={commentTypes}
              isMinistry={isMinistry}
              bcgovcode={bcgovcode}
            />
          ) : (
            <CommentStructure
              i={a}
              reply
              parentId={i.commentId}
              handleEdit={() => actions.handleAction} totalcommentCount={i.replies.length} currentIndex={replyindex} isreplysection={true} hasAnotherUserComment={false} 
              fullName={getfullName(a.commentTypeId, a.userId)}
              commentTypes={commentTypes}
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
              fullnameList?.length > 0 &&
              <InputField
                cancellor={a.commentId}
                parentId={i.commentId}
                child
                fullnameList={fullnameList}
                restrictedReqTaglist={restrictedReqTaglist}
                isRestricted={isRestricted}
                //Handles Navigate Away
                setEditorChange={setEditorChange} removeComment={removeComment} setRemoveComment={setRemoveComment}
                commentTypeId={i.commentTypeId}
                newCommentTypeId={commentTypeId}
                setCommentTypeId={setCommentTypeId}
                commentTypes={commentTypes}
                isMinistry={isMinistry}
                bcgovcode={bcgovcode}
              />           
            ))}
        </div>
      )))

  }

  const rendercomments = () =>{
    if(fullnameList?.length > 0)
    {
        return (
          comments.map((i, index) => (
            <>
            <div key={i.commentId} className="commentsection" data-comid={i.commentId} name={index >= limit ? 'commentsectionhidden' : ""} style={index >= limit && !showmorehidden ? { display: 'none' } : { display: 'block' }}>
              {fullnameList?.length > 0 && actions.editArr.filter((id) => id === i.commentId).length !== 0 ? (
                <InputField cancellor={i.commentId} inputvalue={i.text} edit fullnameList={fullnameList} restrictedReqTaglist={restrictedReqTaglist} isRestricted={isRestricted} //Handles Navigate Away
                  setEditorChange={setEditorChange} removeComment={removeComment} setRemoveComment={setRemoveComment} 
                  commentTypeId={i.commentTypeId} newCommentTypeId={commentTypeId} setCommentTypeId={setCommentTypeId} 
                  commentTypes={commentTypes} isMinistry={isMinistry} bcgovcode={bcgovcode}/>
              ) : (
                <CommentStructure i={i} handleEdit={() => actions.handleAction} totalcommentCount={gettotalcommentflag(i)} currentIndex={index} c={false} 
                  hasAnotherUserComment={(i.replies && i.replies.filter(r => r.userId !== currentUser.userId).length > 0)} 
                  fullName={getfullName(i.commentTypeId, i.userId)} commentTypes={commentTypes} />
              )}
              {
                fullnameList?.length > 0 && actions.replies.filter((id) => id === i.commentId).length !== 0 &&
                (
                  <InputField cancellor={i.commentId} parentId={i.commentId} fullnameList={fullnameList} restrictedReqTaglist={restrictedReqTaglist} isRestricted={isRestricted} //Handles Navigate Away
                    setEditorChange={setEditorChange} removeComment={removeComment} setRemoveComment={setRemoveComment} 
                    commentTypeId={i.commentTypeId} newCommentTypeId={commentTypeId} setCommentTypeId={setCommentTypeId} 
                    commentTypes={commentTypes} isMinistry={isMinistry} bcgovcode={bcgovcode}/>
                )
              }
              <div className="replySection">
                {
                  renderreplies(i)
                }
              </div>
            </div>
            </>
          ))



        )
    }
  }


  const actions = useContext(ActionContext)

  return (
    <div style={{ paddingBottom: '2%', marginBottom: '2%' }}>

      {
        comments.length === 0 ? <div className="nofiltermessage">No comments under this filter category</div> :
          rendercomments()          
          }
      <div id="showMoreParentComments" className="showMoreParentComments" style={!showmorehidden && comments.length > 10 ? { display: 'block' } : { display: 'none' }}>
        <button className="btn foi-btn-create btnshowmore" onClick={(e) => showhiddencomments(e, 5)}>Show more comments</button>
      </div>
    </div>
  )
}

export default DisplayComments
