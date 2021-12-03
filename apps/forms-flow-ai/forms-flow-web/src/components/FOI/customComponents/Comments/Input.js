import React, { useContext } from 'react'
import InputField from './InputField'
import { ActionContext } from './ActionContext'

const Input = ({add, setQuillChange, removeComment, setRemoveComment}) => {
  
  const action = useContext(ActionContext)
  return action.customInput ? (
    action.customInput({
      authorImg: action.userImg,
      main: true,
      handleCancel: action.handleCancel,
      submit: action.submit
    })
  ) : (
    <InputField authorImg={action.userImg} main add={add} setQuillChange={setQuillChange} removeComment={removeComment} setRemoveComment={setRemoveComment} />
  )
}

export default Input
