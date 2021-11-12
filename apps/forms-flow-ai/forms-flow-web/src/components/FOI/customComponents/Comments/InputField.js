import React, { useContext, useState, useEffect } from 'react'
import './comments.scss'
import { ActionContext } from './ActionContext'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faPaperPlane, faTrash } from '@fortawesome/free-solid-svg-icons'
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';



const InputField = ({ cancellor, parentId, child, value, edit, main }) => {

  let maxcharacterlimit = 1000
  const [text, setText] = useState('')
  const [textlength, setTextLength] = useState(maxcharacterlimit)

  const handleQuillChange = (htmlcontent, delta, source, editor) => {
    let _unformattedtext = editor.getText()
    
    if (_unformattedtext && _unformattedtext != "" && _unformattedtext != undefined && textlength <= maxcharacterlimit) {

      if (_unformattedtext.length - 1 <= maxcharacterlimit) {
        setText(htmlcontent)

      }
      else { 
        setText(_unformattedtext.substring(0,maxcharacterlimit-1)) 
      }

      setTextLength(maxcharacterlimit - (_unformattedtext && _unformattedtext != "" && _unformattedtext.length - 1 <= maxcharacterlimit ? _unformattedtext.length - 1 : 0))
    }
  }

  const handlekeydown = (event) => {

    if ((textlength > maxcharacterlimit && event.key !== 'Backspace') || (textlength <= 0 && event.key !== 'Backspace'))
      event.preventDefault();
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

        <ReactQuill theme="snow" value={text || ''} onKeyDown={handlekeydown} onChange={handleQuillChange} placeholder={"Type your comments here"} />

        <div className="inputActions">

          <span className="characterlen">{textlength} characters remaining</span>
          <button
            className="postBtn"
            onClick={post}
            type='button'
            disabled={!text}

          >
            {' '}
            <FontAwesomeIcon icon={faPaperPlane} size='2x' color={!text ? '#a5a5a5' : 'darkblue'} />
          </button>          
        </div>

      </form>

    </>
  )
}

export default InputField
