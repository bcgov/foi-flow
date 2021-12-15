import React, { useContext, useState, useEffect, useRef, useMemo, useCallback } from 'react'
import './comments.scss'
import { ActionContext } from './ActionContext'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faPaperPlane, faTimes } from '@fortawesome/free-solid-svg-icons'
import { setFOILoader } from '../../../../actions/FOI/foiRequestActions'
import Editor, { createEditorStateWithText } from '@draft-js-plugins/editor';
import { convertToRaw, convertFromRaw, convertFromHTML, ContentState, EditorState } from "draft-js";
import createMentionPlugin, {
  defaultSuggestionsFilter
} from '@draft-js-plugins/mention';
import createToolbarPlugin from '@draft-js-plugins/static-toolbar';
import {
  ItalicButton,
  BoldButton,
  UnderlineButton,
  UnorderedListButton,
  OrderedListButton,

} from '@draft-js-plugins/buttons';

const staticToolbarPlugin = createToolbarPlugin();
const mentionPlugin = createMentionPlugin();
const { Toolbar } = staticToolbarPlugin;
const { MentionSuggestions } = mentionPlugin
const plugins = [staticToolbarPlugin, mentionPlugin];
const InputField = ({ cancellor, parentId, child, value, edit, main, add, fullnameList,
  //setEditorChange, removeComment and setRemoveComment added to handle Navigate away from Comments tabs 
  setEditorChange, removeComment, setRemoveComment
}) => {
  let maxcharacterlimit = 1000
  const [uftext, setuftext] = useState('')
  const [textlength, setTextLength] = useState(1000)
  const [open, setOpen] = useState(false);

  let fulluserlist = [...fullnameList]
  fulluserlist.forEach(ful => {
    ful.name = ful.fullname;
  })

  const mentionList = fulluserlist.sort()

  const [suggestions, setSuggestions] = useState(mentionList);

  const onOpenChange = (_open) => {
    setOpen(_open);
  }

  // Check editor text for mentions
  const onSearchChange = ({ value }) => {
    setSuggestions(defaultSuggestionsFilter(value, mentionList))
  }

  const getEditorState = (value) => {
    const rawContentFromStore = convertFromRaw(JSON.parse(value))
    let initialEditorState = EditorState.createWithContent(rawContentFromStore);
    return initialEditorState
  }
  const [editorState, setEditorState] = useState(value === '' || value === undefined ? EditorState.createEmpty() : getEditorState(value))

  const getMentionsOnComment = () => {
    const rawContentState = convertToRaw(editorState.getCurrentContent());
    const commentmentions = [];
    const entityMap = rawContentState.entityMap;
    Object.values(entityMap).forEach(entity => {

      if (entity.type === 'mention') {
        commentmentions.push({ username: entity.data.mention.username, name: entity.data.mention.name });
      }
    });

    return commentmentions;
  }

  const _handleChange = (editorState) => {
    const currentContent = editorState.getCurrentContent();
    const rawContentState = convertToRaw(currentContent);
    const currentContentLength = currentContent.getPlainText('').length;
    const selectedTextLength = _getLengthOfSelectedText();
    let _textLength = maxcharacterlimit - (currentContentLength - selectedTextLength)
    if (_textLength > 0) 
    { 
      setTextLength(maxcharacterlimit - (currentContentLength - selectedTextLength))
       
    }
    

    setuftext(currentContent.getPlainText(''))
    setEditorState(editorState);
    setEditorChange(currentContentLength > 0)
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
    if ((e === 'backspace' || e === 'delete') && currentContentLength - 1 >= 0) {
      setTextLength((maxcharacterlimit) - (currentContentLength - 1))
    }

    if ((e === 'backspace' || e === 'delete') && selectedTextLength > 0) {
      setTextLength(maxcharacterlimit - (currentContentLength - selectedTextLength))
    }
    setuftext(currentContent.getPlainText(''))
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
    setuftext(currentContent.getPlainText(''))
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
    setuftext(currentContent.getPlainText(''))
  }



  useEffect(() => {
    if (value !== undefined) {
      const contentstate = getEditorState(value)
      const currentContent = contentstate.getCurrentContent();
      setuftext(currentContent.getPlainText(''))
      setTextLength(maxcharacterlimit - currentContent.getPlainText('').length)
    }

  }, [value])

  //Handles Navigate Away
  const closeX = () => {
    setEditorState(EditorState.createEmpty())
    setuftext('')
    edit
      ? actions.handleCancel(cancellor, edit)
      : actions.handleCancel(cancellor)
  }

  //Handles Navigate Away
  useEffect(() => {
    if (removeComment) {
      if (add) {
        setEditorState(EditorState.createEmpty())
        setuftext('')
      }
      else {
        closeX();
      }
      setRemoveComment(false);
    }
  })

  

  const cancel = (e) => {
    if (uftext) {
      if (window.confirm("Are you sure you want to leave? Your changes will be lost.")) {
        closeX();
        setEditorChange(false);
      }
    }
    else {
      closeX();
    }
    e.preventDefault();
  }

  const post = () => {
    if (uftext !== '' && uftext.trim().length > 0) {
      const _mentions = getMentionsOnComment()
      const _editorstateinJSON = JSON.stringify(convertToRaw(editorState.getCurrentContent()))
      setFOILoader(true)
      edit === true
        ? actions.submit(cancellor, _editorstateinJSON, JSON.stringify(_mentions), parentId, true)
        : actions.submit(cancellor, _editorstateinJSON, JSON.stringify(_mentions), parentId, false)

      setEditorState(createEditorStateWithText(''))
      setEditorChange(false)
      setTextLength(1000);
    }

  }

  let formclass = !parentId ? "parentform form" : "form"
  formclass = add ? `${formclass} addform` : formclass

  formclass = (add === undefined && main === undefined && edit === undefined) ? `${formclass} addform newreply` : formclass

  const actions = useContext(ActionContext)

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
          editorState={editorState}
          onChange={_handleChange}
          handleBeforeInput={_handleBeforeInput}
          handlePastedText={_handlePastedText}
          handleKeyCommand={_handleKeyCommand}
          plugins={plugins}
        />
        <MentionSuggestions
          open={open}
          onOpenChange={onOpenChange}
          suggestions={suggestions}
          onSearchChange={onSearchChange}
          onAddMention={(_mentions) => {
            console.log('onAddMention')
            // get the mention object selected
          }}
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
            disabled={uftext.trim().length === 0}
          >
            {' '}
            <FontAwesomeIcon disabled={uftext.trim().length === 0} icon={faPaperPlane} size='2x' color={uftext.trim().length === 0 ? '#a5a5a5' : 'darkblue'} />
          </button>
        </div>
      </div>

    </>
  )
}

export default InputField
