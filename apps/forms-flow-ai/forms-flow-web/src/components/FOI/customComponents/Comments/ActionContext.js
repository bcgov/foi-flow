import React, { createContext, useEffect, useState } from 'react'
import uuid from 'react-uuid'
import {fetchFOIRawRequestDetails, fetchFOIRequestNotesList,saveRawRequestNote,editRawRequestNote} from '../../../../apiManager/services/FOI/foiRequestServices'
import { useDispatch, useSelector } from "react-redux";

export const ActionContext = createContext()
export const ActionProvider = ({
  children,
  currentUser,
  setComment,
  comments,
  signinUrl,
  signupUrl,
  customInput,
  requestid
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
    edit ? setEdit([...editArr, id]) : setReplies([...replies, id])
  }
  const handleCancel = (id, edit) => {
    if (edit) {
      const list = [...editArr]
      const newList = list.filter((i) => i !== id)
      setEdit(newList)
    } else if (!edit) {
      const list = [...replies]
      const newList = list.filter((i) => i !== id)
      setReplies(newList)
    }
  }
  
  const onSubmit = (text, parentId, child) => {   
    if (text.length > 0) {
      if (!parentId && !child) {       
        const _inputData = {"requestid" : requestid,"comment":text}        
        dispatch(saveRawRequestNote(_inputData));          
        const maxId = comments && comments.length > 0 && comments.reduce(
          (max, comment) => ( comment && comment.commentId > max ? comment.commentId : max),
          comments[0].commentId
        );                
        comments.push(        
          {
            userId: currentUser.userId,
            commentId: maxId+1,
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
          avatarUrl: currentUser.avatarUrl,
          fullName: currentUser.name,
          text: text
        })
        const _inputData = {"requestid" : requestid,"comment":text,"parentcommentid":parentId}        
        dispatch(saveRawRequestNote(_inputData));
        newList[index].replies = newReplies
        setComment(newList)
      }
    }
  }

  const editText = (id, text, parentId) => {
    if (parentId === undefined) {
      const _inputData = {"comment":text}        
      dispatch(editRawRequestNote(_inputData,id));
      const newList = [...comments]
      const index = newList.findIndex((x) => x.commentId === id)
      newList[index].text = text
      setComment(newList)
    } else if (parentId !== undefined) {
      const _inputData = {"comment":text}        
      dispatch(editRawRequestNote(_inputData,id));
      const newList = [...comments]
      const index = newList.findIndex((x) => x.commentId === parentId)
      const replyIndex = newList[index].replies.findIndex((i) => i.commentId === id)
      newList[index].replies[replyIndex].text = text
      setComment(newList)
    }
  }

  const deleteText = (id, parentId) => {
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

  const submit = (cancellor, text, parentId, edit, setText, child) => {
    if (edit) {
      editText(cancellor, text, parentId)
      handleCancel(cancellor, edit)
      setText('')
    } else {
      onSubmit(text, parentId, child)
      handleCancel(cancellor)
      setText('')
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
