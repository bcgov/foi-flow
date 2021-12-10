import React, { useContext, useState, useEffect, useRef } from 'react'
import './comments.scss'
import { ActionContext } from './ActionContext'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faPaperPlane, faTimes } from '@fortawesome/free-solid-svg-icons'
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import { setFOILoader } from '../../../../actions/FOI/foiRequestActions'
import Editor, { createEditorStateWithText } from '@draft-js-plugins/editor';
import createToolbarPlugin from '@draft-js-plugins/static-toolbar';
import draftToHtml from 'draftjs-to-html';
import {
  ItalicButton,
  BoldButton,
  UnderlineButton,
  CodeButton,
  HeadlineOneButton,
  HeadlineTwoButton,
  HeadlineThreeButton,
  UnorderedListButton,
  OrderedListButton,
  BlockquoteButton,
  CodeBlockButton,
} from '@draft-js-plugins/buttons';

import { convertToRaw, convertFromHTML, ContentState, EditorState } from "draft-js";

const staticToolbarPlugin = createToolbarPlugin();
const { Toolbar } = staticToolbarPlugin;
const plugins = [staticToolbarPlugin];

const InputField = ({ cancellor, parentId, child, value, edit, main, add }) => {
  const editor = React.useRef(null)
  let maxcharacterlimit = 1000
  const [text, setText] = useState('')
  const [uftext, setuftext] = useState('')
  const [textlength, setTextLength] = useState(1000)



  const [editorState, setEditorState] = useState(() => createEditorStateWithText(''))


  const _handleChange = (editorState) => {
    const rawContentState = convertToRaw(editorState.getCurrentContent());
    const markup = draftToHtml(
      rawContentState
    );
    setText(markup)
    setEditorState(editorState);
  }

  const _getLengthOfSelectedText = () => {
    const currentSelection = editorState.getSelection();
    const isCollapsed = currentSelection.isCollapsed();

    let length = 0;

    if (!isCollapsed) {
      const currentContent = editorState.getCurrentContent();
      const startKey = currentSelection.getStartKey();
      const endKey = currentSelection.getEndKey();
      const startBlock = currentContent.getBlockForKey(startKey);
      const isStartAndEndBlockAreTheSame = startKey === endKey;
      const startBlockTextLength = startBlock.getLength();
      const startSelectedTextLength = startBlockTextLength - currentSelection.getStartOffset();
      const endSelectedTextLength = currentSelection.getEndOffset();
      const keyAfterEnd = currentContent.getKeyAfter(endKey);

      if (isStartAndEndBlockAreTheSame) {
        length += currentSelection.getEndOffset() - currentSelection.getStartOffset();
      } else {
        let currentKey = startKey;

        while (currentKey && currentKey !== keyAfterEnd) {
          if (currentKey === startKey) {
            length += startSelectedTextLength + 1;
          } else if (currentKey === endKey) {
            length += endSelectedTextLength;
          } else {
            length += currentContent.getBlockForKey(currentKey).getLength() + 1;
          }

          currentKey = currentContent.getKeyAfter(currentKey);
        };
      }
    }

    return length;
  }

  const _handleKeyCommand = (e) => {

    const currentContent = editorState.getCurrentContent();
    const currentContentLength = currentContent.getPlainText('').length;
    const selectedTextLength = _getLengthOfSelectedText();
    console.log(`_handleKeyCommand : e ${e} | currentContentLength:${currentContentLength} | selectedTextLength${selectedTextLength} `)
    if ((e === 'backspace' || e === 'delete') && currentContentLength - 1 >= 0) {

      setTextLength((maxcharacterlimit) - (currentContentLength - 1))
    }

    if ((e === 'backspace' || e === 'delete') && selectedTextLength > 0) {

      console.log(`maxcharacterlimit - selectedTextLength is ${maxcharacterlimit - selectedTextLength}`)
      setTextLength(maxcharacterlimit - (currentContentLength - selectedTextLength))
    }
  }

  const _handleBeforeInput = () => {
    const currentContent = editorState.getCurrentContent();
    const currentContentLength = currentContent.getPlainText('').length;
    const selectedTextLength = _getLengthOfSelectedText();
    if (currentContentLength - selectedTextLength > maxcharacterlimit - 1) {
      return 'handled';
    }
    else {
      setTextLength((maxcharacterlimit - 1) - (currentContentLength - selectedTextLength))
    }
  }

  const _handlePastedText = (pastedText) => {
    const currentContent = editorState.getCurrentContent();
    const currentContentLength = currentContent.getPlainText('').length;
    const selectedTextLength = _getLengthOfSelectedText();
    if (currentContentLength + pastedText.length - selectedTextLength > maxcharacterlimit) {
      return 'handled';
    }
    else {
      setTextLength((maxcharacterlimit) - (currentContentLength + pastedText.length - selectedTextLength))
    }
  }
    ;

  useEffect(() => {

    if (value !== undefined) {      
      focusEditor()
      const blocksFromHTML = convertFromHTML(value);
      const state = ContentState.createFromBlockArray(
        blocksFromHTML.contentBlocks,
        blocksFromHTML.entityMap,
      );
      const contentstate = EditorState.createWithContent(state)
      const currentContent = contentstate.getCurrentContent();      
      setEditorState(contentstate)
      setText(value)
      setuftext(value)
      setTextLength(maxcharacterlimit - currentContent.getPlainText('').length)

    }
    else {

      focusEditor()
    }


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

    setEditorState(createEditorStateWithText(''))
    setTextLength(1000);
    if (text !== '<p></p>') {
      setFOILoader(true)
      edit === true
        ? actions.submit(cancellor, text, parentId, true, setText)
        : actions.submit(cancellor, text, parentId, false, setText)
    }

  }

  let formclass = !parentId ? "parentform form" : "form"
  formclass = add ? `${formclass} addform` : formclass

  formclass = (add === undefined && main === undefined && edit === undefined) ? `${formclass} addform newreply` : formclass

  const actions = useContext(ActionContext)

  function focusEditor() {
    if (editor !== undefined && editor.current !== null) { editor.current.focus() }
  }

 
  return (
    <>
      <form
        className={formclass}
      >
        <div className="row cancelrow">
          <div className="col-lg-12" style={{ height: '0px' }}>
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
        <Toolbar>
            {             
              (externalProps) => (
                <div>
                  <BoldButton {...externalProps} />
                  <ItalicButton {...externalProps} />
                  <UnderlineButton {...externalProps} />                                 
                  <UnorderedListButton {...externalProps} />
                  <OrderedListButton {...externalProps} />                                    
                </div>
              )
            }
          </Toolbar>
        <Editor
          ref={editor}
          editorState={editorState}
          onChange={_handleChange}
          handleBeforeInput={_handleBeforeInput}
          handlePastedText={_handlePastedText}
          handleKeyCommand={_handleKeyCommand}
          plugins={plugins}
        />
        
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
            disabled={text === '<p></p>'}
          >
            {' '}
            <FontAwesomeIcon disabled={textlength === 0 || text === "<p></p>"} icon={faPaperPlane} size='2x' color={text === undefined || text.length === 0 || textlength === maxcharacterlimit || text === "<p></p>" ? '#a5a5a5' : 'darkblue'} />
          </button>
        </div>
      </div>

    </>
  )
}

export default InputField
