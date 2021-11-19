import React, { useContext, useState, useEffect } from 'react'
import './comments.scss'
import { ActionContext } from './ActionContext'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faPaperPlane, faTimes } from '@fortawesome/free-solid-svg-icons'
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import {setFOILoader} from '../../../../actions/FOI/foiRequestActions'


const InputField = ({ cancellor, parentId, child, value, edit, main }) => {

  let maxcharacterlimit = 1000
  const [text, setText] = useState('')
  const [uftext, setuftext] = useState('')
  const [textlength, setTextLength] = useState(maxcharacterlimit)

  const handleQuillChange = (htmlcontent, delta, source, editor) => {
    let _unformattedtext = editor.getText()
    if (_unformattedtext && _unformattedtext.trim() != "" && _unformattedtext != undefined && textlength <= maxcharacterlimit) {

      if (_unformattedtext.trim().length - 1 <= maxcharacterlimit) {
        setText(htmlcontent)

      }
      else {
        setText(_unformattedtext.trim().substring(0, maxcharacterlimit - 1))
      }
      setuftext(_unformattedtext.trim())
      if (_unformattedtext.length - 1 <= maxcharacterlimit)
        setTextLength(maxcharacterlimit - (_unformattedtext && _unformattedtext != "" && _unformattedtext.trim().length - 1 <= maxcharacterlimit ? _unformattedtext.trim().length - 1 : 0))
    }
  }

  const handlekeydown = (event) => {

    if ((textlength > maxcharacterlimit && event.key !== 'Backspace') || (textlength <= 0 && event.key !== 'Backspace'))
      event.preventDefault();
  }

  useEffect(() => {
    setText(value)
    setuftext(value)
  }, [value])


  const cancel = (e) => {
    setText('')
    setuftext('')
    edit
      ? actions.handleCancel(cancellor, edit)
      : actions.handleCancel(cancellor)

    e.preventDefault()
  }

  const post = () => {

    setTextLength(1000);
    if (text !== '<p><br></p>') {
      setFOILoader(true)
      edit === true
        ? actions.submit(cancellor, text, parentId, true, setText)
        : actions.submit(cancellor, text, parentId, false, setText)
    }

  }

  const actions = useContext(ActionContext)
  return (
    <>
      <form
        className="form"        
      >
        <div className="row">
          <div className="col-lg-12">
            {(!main) ? (
              <button
                className="cancelBtn"
                onClick={cancel}
              >
                <FontAwesomeIcon icon={faTimes} size='2x' color={'#a5a5a5'} />
              </button>
            ) : null}
          </div>
        </div>

        <ReactQuill theme="snow" value={text || ''} onKeyDown={handlekeydown} onChange={handleQuillChange} placeholder={"Add a new note"} />

        

      </form>
      <div className="inputActions">
          <div className={'col-lg-11'}>
            <span className={textlength > 25 ? "characterlen" : "characterlen textred"}>{textlength} characters remaining</span>
          </div>
          <div className="col-lg-1 paperplanecontainer">
            <button
              className="postBtn"
              onClick={post}
              type='button'
              disabled={!uftext}

            >
              {' '}
              <FontAwesomeIcon disabled={text === undefined || textlength === 0} icon={faPaperPlane} size='2x' color={text === undefined || text.length === 0 || textlength === maxcharacterlimit ? '#a5a5a5' : 'darkblue'} />
            </button>
          </div>
        </div>

    </>
  )
}

export default InputField
