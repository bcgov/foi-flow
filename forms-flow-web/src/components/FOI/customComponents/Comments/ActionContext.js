import React, { createContext, useEffect, useState } from 'react'
import uuid from 'react-uuid'
import { saveRawRequestNote, editRawRequestNote, saveMinistryRequestNote, editMinistryRequestNote, deleteMinistryRequestNote, deleteRawRequestNote } from '../../../../apiManager/services/FOI/foiRequestNoteServices'
import { useDispatch } from "react-redux";
import { setFOILoader } from '../../../../actions/FOI/foiRequestActions'
export const ActionContext = createContext()
export const ActionProvider = ({
  children,
  currentUser,
  setComment,
  comments,
  signinUrl,
  signupUrl,
  customInput,
  requestid,
  ministryId
}) => {
  const dispatch = useDispatch();
  const [replies, setReplies] = useState([])
  const [user, setUser] = useState()
  const [editArr, setEdit] = useState([])

  useEffect(() => {
    if (currentUser) {
      setUser(true)
    } else {
      setUser(false)
    }
  })



  const handleAction = (id, edit) => {

    if (edit) {
      setEdit([...editArr, id])
    }
    else {
      let btnreply = document.getElementById(`btncomment${id}`)
      if (btnreply) { btnreply.style.display = 'none' }
      setReplies([...replies, id])
    }

  }
  const handleCancel = (id, edit) => {
    if (edit) {
      const list = [...editArr]
      const newList = list.filter((i) => i !== id)
      setEdit(newList)
    } else if (!edit) {
      let btnreply = document.getElementById(`btncomment${id}`)
      if (btnreply)
        btnreply.style.display = 'block'
      const list = [...replies]
      const newList = list.filter((i) => i !== id)
      setReplies(newList)
    }
  }

  const getmaxcommentid = (_comments) => {
    return _comments?.length > 0 && _comments.reduce(
      (max, comment) => (comment?.commentId > max ? comment.commentId : max),
      comments[0].commentId
    );
  }

  const saverequestcomment = (text,taggedusers, commentTypeId) => {
    if (ministryId) {
      dispatch(saveMinistryRequestNote({ "ministryrequestid": ministryId, "comment": text, "taggedusers": taggedusers, "commenttypeid": commentTypeId }, ministryId));
    }
    else {
      dispatch(saveRawRequestNote({ "requestid": requestid, "comment": text, "taggedusers": taggedusers, "commenttypeid": commentTypeId }, requestid));
    }
  }
  const onSubmit = (text, parentId, child, taggedusers, commentTypeId) => {
    setFOILoader(true)
    if (text.length > 0) {
      if (!parentId && !child) {
        saverequestcomment(text,taggedusers, commentTypeId)
        const maxId = getmaxcommentid(comments)
        comments.push(
          {
            userId: currentUser.userId,
            commentId: maxId + 1,
            commentTypeId: commentTypeId,//1,
            avatarUrl: currentUser.avatarUrl,
            fullName: currentUser.name,
            text: text
          })
        setComment(comments)

      } else if (parentId && child) {
        const newList = [...comments]
        const index = newList.findIndex((x) => x.commentId === parentId)
        newList[index].replies.push({
          userId: currentUser.userId,
          commentId: uuid(),
          commentTypeId: commentTypeId, //1,
          avatarUrl: currentUser.avatarUrl,
          fullName: currentUser.name,
          text: text
        })
        setComment(newList)
      } else if (parentId && !child) {
        const newList = [...comments]
        const index = newList.findIndex((x) => x.commentId === parentId)
        const newReplies =
          newList[index].replies === undefined
            ? []
            : [...newList[index].replies]
        newReplies.push({
          userId: currentUser.userId,
          commentId: uuid(),
          commentTypeId: commentTypeId, //1,
          avatarUrl: currentUser.avatarUrl,
          fullName: currentUser.name,
          text: text
        })
        if (ministryId) {
          const _inputData = { "ministryrequestid": ministryId, "comment": text, "parentcommentid": parentId, "taggedusers": taggedusers, "commenttypeid": commentTypeId }
          dispatch(saveMinistryRequestNote(_inputData, ministryId));
        }
        else {
          const _inputData = { "requestid": requestid, "comment": text, "parentcommentid": parentId, "taggedusers": taggedusers, "commenttypeid": commentTypeId }
          dispatch(saveRawRequestNote(_inputData, requestid));
        }

        newList[index].replies = newReplies
        setComment(newList)
      }
    }
  }

  const editText = (id, text, parentId, taggedusers, commentTypeId) => {
    setFOILoader(true)
    if (parentId === undefined) {

      if (ministryId) {
        const _inputData = { "comment": text, "taggedusers": taggedusers,"commenttypeid":commentTypeId }
        dispatch(editMinistryRequestNote(_inputData, id, ministryId));
      }
      else {
        const _inputData = { "comment": text, "taggedusers": taggedusers ,"commenttypeid":commentTypeId}
        dispatch(editRawRequestNote(_inputData, id, requestid));
      }

      const newList = [...comments]
      const index = newList.findIndex((x) => x.commentId === id)
      newList[index].text = text
      setComment(newList)
    } else if (parentId !== undefined) {
      if (ministryId) {
        const _inputData = { "comment": text, "taggedusers": taggedusers,"commenttypeid":commentTypeId }
        dispatch(editMinistryRequestNote(_inputData, id, ministryId));
      }
      else {
        const _inputData = { "comment": text, "taggedusers": taggedusers,"commenttypeid":commentTypeId }
        dispatch(editRawRequestNote(_inputData, id, requestid));
      }
      const newList = [...comments]
      const index = newList.findIndex((x) => x.commentId === parentId)
      const replyIndex = newList[index].replies.findIndex((i) => i.commentId === id)
      newList[index].replies[replyIndex].text = text
      setComment(newList)
    }
  }

  const deleteText = (id, parentId) => {
    setFOILoader(true)
    if (ministryId) {
      dispatch(deleteMinistryRequestNote({}, id, ministryId));
    }
    else {
      dispatch(deleteRawRequestNote({}, id, requestid));
    }


    if (parentId === undefined) {
      const newList = [...comments]
      const filter = newList.filter((x) => x.commentId !== id)
      setComment(filter)
    } else if (parentId !== undefined) {
      const newList = [...comments]
      const index = newList.findIndex((x) => x.commentId === parentId)
      const filter = newList[index].replies.filter((x) => x.commentId !== id)
      newList[index].replies = filter
      setComment(newList)
    }
  }

  const submit = (cancellor, text, taggedusers, parentId, edit, commentTypeId, child) => {
    if (edit) {
      editText(cancellor, text, parentId, taggedusers, commentTypeId)
      handleCancel(cancellor, edit)

    } else {
      onSubmit(text, parentId, child, taggedusers, commentTypeId)
      handleCancel(cancellor)

    }
  }

  return (
    <ActionContext.Provider
      value={{
        onSubmit: onSubmit,
        userImg: currentUser && currentUser.avatarUrl,
        userId: currentUser && currentUser.userId,
        handleAction: handleAction,
        handleCancel: handleCancel,
        replies: replies,
        setReplies: setReplies,
        editArr: editArr,
        onEdit: editText,
        onDelete: deleteText,
        signinUrl: signinUrl,
        signupUrl: signupUrl,
        user: user,
        customInput: customInput,
        submit: submit
      }}
    >
      {children}
    </ActionContext.Provider>
  )
}
