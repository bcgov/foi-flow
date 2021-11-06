import React, { useContext, useState, useEffect } from 'react'
import './comments.scss'
import { ActionContext } from './ActionContext'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faPaperPlane, faTrash } from '@fortawesome/free-solid-svg-icons'
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';



const InputField = ({ cancellor, parentId, child, value, edit, main }) => {
  const [text, setText] = useState('')
  const [textlength, setTextLength] = useState(1000)
 
  // const handleChange = (e) => {   
  //   setTextLength(1000 - e.target.value.length)
  //   setText(e.target.value)
  // }

  const handleQuillChange = (htmlcontent, delta, source, editor)=>{    
    let _text = editor.getText()   
    setText(htmlcontent)
    setTextLength(1000 - _text.length)
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

  const post = () => {
    
    setTextLength(1000);

    edit === true
      ? actions.submit(cancellor, text, parentId, true, setText)
      : actions.submit(cancellor, text, parentId, false, setText)
  }
 
  const actions = useContext(ActionContext)
  return (
    <>
    <form
      className="form"
      style={
        !child && !edit && main === undefined
          ? { marginLeft: 36 }
          : { marginLeft: 8 }
      }
    >

      <ReactQuill theme="snow"  value={text || ''} onChange={handleQuillChange} placeholder={"Type your comments here"} />
     
      <div className="inputActions">
      
      <span className="characterlen">{textlength} characters remaining</span>
        <button
          className="postBtn"
          onClick={post}
          type='button'
          disabled={!text}
         
        >
          {' '}
          <FontAwesomeIcon icon={faPaperPlane} size='2x' color={!text ? '#a5a5a5':'darkblue'} />
        </button>
        {(text || parentId) && (
          <button
            className="cancelBtn"
            onClick={cancel}
          >
            <FontAwesomeIcon icon={faTrash} size='2x' color={!text ? '#a5a5a5':'darkblue'} />
          </button>
        )}
      </div>
      
    </form>
    
    </>
  )
}

export default InputField
