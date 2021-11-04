import React, { useContext, useState, useEffect } from 'react'
import './comments.scss'
import { ActionContext } from './ActionContext'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faPaperPlane } from '@fortawesome/free-solid-svg-icons'

const InputField = ({ cancellor, parentId, child, value, edit, main }) => {
  const [text, setText] = useState('')

  const handleChange = (e) => {
    setText(e.target.value)
  }

  useEffect(() => {
    setText(value)
  }, [value])


  const cancel = () => {
    setText("")
    edit
      ? actions.handleCancel(cancellor, edit)
      : actions.handleCancel(cancellor)
  }

  const actions = useContext(ActionContext)
  return (
    <form
      className="form"
      style={
        !child && !edit && main === undefined
          ? { marginLeft: 36 }
          : { marginLeft: 8 }
      }
    >

      <input
        className="postComment"
        type='text'
        placeholder='Type your reply here.'
        component='input'
        value={text}
        onChange={handleChange}
      />
      <div className="inputActions">
        <button
          className="postBtn"
          onClick={() =>
            edit === true
              ? actions.submit(cancellor, text, parentId, true, setText)
              : actions.submit(cancellor, text, parentId, false, setText)
          }
          type='button'
          disabled={!text}
          style={
            !text
              ? { backgroundColor: '#84dcff' }
              : { backgroundColor: '#30c3fd' }
          }
        >
          {' '}
          <FontAwesomeIcon icon={faPaperPlane} size='2x' color='#a5a5a5' />
        </button>
        {(text || parentId) && (
          <button
            className="cancelBtn"
            onClick={cancel}
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  )
}

export default InputField
