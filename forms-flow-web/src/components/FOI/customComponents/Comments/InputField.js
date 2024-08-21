import React, { useContext, useState, useEffect} from 'react'
import { useSelector } from "react-redux"
import './comments.scss'
import { ActionContext } from './ActionContext'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faTimes } from '@fortawesome/free-solid-svg-icons'
import { setFOILoader } from '../../../../actions/FOI/foiRequestActions'
import Editor, { createEditorStateWithText } from '@draft-js-plugins/editor';
import { convertToRaw, convertFromRaw, EditorState } from "draft-js";
import createMentionPlugin, {
  defaultSuggestionsFilter
} from '@draft-js-plugins/mention';
import {namesort,suggestionList } from './commentutils'
import createToolbarPlugin from '@draft-js-plugins/static-toolbar';
import {
  ItalicButton,
  BoldButton,
  UnderlineButton,
  UnorderedListButton,
  OrderedListButton,

} from '@draft-js-plugins/buttons';
import { getFullnameList, getCommentTypeIdByName, getIAOTagList, getAssignToList } from '../../../../helper/FOI/helper'
import Grid from "@material-ui/core/Grid";
import Radio from "@material-ui/core/Radio";
import RadioGroup from "@material-ui/core/RadioGroup";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import FormControl from "@material-ui/core/FormControl";


const staticToolbarPlugin = createToolbarPlugin();
const mentionPlugin = createMentionPlugin();
const { Toolbar } = staticToolbarPlugin;
const { MentionSuggestions } = mentionPlugin
const plugins = [staticToolbarPlugin, mentionPlugin];
const InputField = ({ cancellor, parentId, child, inputvalue, edit, main, add, fullnameList, restrictedReqTaglist,
  //setEditorChange, removeComment and setRemoveComment added to handle Navigate away from Comments tabs 
  isRestricted, setEditorChange, removeComment, setRemoveComment, commentTypeId, newCommentTypeId, setCommentTypeId,commentTypes, isMinistry, bcgovcode
}) => {
  let maxcharacterlimit = 1000
  const [uftext, setuftext] = useState('')
  const [textlength, setTextLength] = useState(1000)
  const [open, setOpen] = useState(false);
  const isCommentTagListLoading = useSelector((state) => state.foiRequests.isCommentTagListLoading);
 
  const [editCommentTypeId, setEditCommentTypeId]= useState(commentTypeId)
  
  
  const filterTagList = (id) => {
    let tagList= fullnameList;
    if(id == getCommentTypeIdByName(commentTypes, "IAO Internal") || 
      id == getCommentTypeIdByName(commentTypes,"IAO Peer Review") )
      tagList= getIAOTagList("iao");//getAssignToList('iao')?.filter((e) => e.type === 'iao');
    else if(id == getCommentTypeIdByName(commentTypes, "Ministry Internal") || 
      id == getCommentTypeIdByName(commentTypes,"Ministry Peer Review")){
        tagList = getIAOTagList(bcgovcode);
    }
    //console.log("tagList:", tagList)
    return [...tagList];
  }

  let fulluserlist = suggestionList(filterTagList(editCommentTypeId)).sort(namesort) //suggestionList([...fullnameList]).sort(namesort)
  const [mentionList, setMentionList] = useState(isCommentTagListLoading ? [{name: 'Loading...'}] : isRestricted ? restrictedReqTaglist :fulluserlist)
  const [suggestions, setSuggestions] = useState(mentionList);

  //console.log("Inputfield-fulluserlist:",fulluserlist)

  useEffect(() => {
    console.log("Use effect : editCommentTypeId",editCommentTypeId)
    setMentionList(isCommentTagListLoading ? [{name: 'Loading...'}] : isRestricted ? restrictedReqTaglist :suggestionList(filterTagList(editCommentTypeId)).sort(namesort));
    setSuggestions(isCommentTagListLoading ? [{name: 'Loading...'}] : isRestricted ? restrictedReqTaglist :mentionList);
  }, [editCommentTypeId])
  
  const onOpenChange = (_open) => {
    setOpen(_open);
  }

  useEffect(() => {
    //console.log("isCommentTagListLoading - Use effect")
    setMentionList(isCommentTagListLoading ? [{name: 'Loading...'}] : isRestricted ? restrictedReqTaglist :suggestionList(filterTagList(editCommentTypeId)).sort(namesort));
    setSuggestions(isCommentTagListLoading ? [{name: 'Loading...'}] : isRestricted ? restrictedReqTaglist : mentionList)//suggestionList(filterTagList(editCommentTypeId)).sort(namesort));
  }, [isCommentTagListLoading, restrictedReqTaglist])

  // Check editor text for mentions
  const onSearchChange = ({ value }) => {      
    let filterlist = isCommentTagListLoading ? mentionList : mentionList.filter(function(item){
      return (item.firstname?.toLowerCase()?.indexOf(value?.toLowerCase()) === 0 || item.lastname?.toLowerCase()?.indexOf(value?.toLowerCase()) === 0)
    }).sort(namesort)        
    if(filterlist?.length >0 )    
      setSuggestions(defaultSuggestionsFilter(value, filterlist))
  }

  const getEditorState = (_value) => {
    const rawContentFromStore = convertFromRaw(JSON.parse(_value))
    return EditorState.createWithContent(rawContentFromStore);
    
  }
  const [editorState, setEditorState] = useState(inputvalue === '' || inputvalue === undefined ? EditorState.createEmpty() : getEditorState(inputvalue))

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

  const _handleChange = (_editorState) => {
    const currentContent = _editorState.getCurrentContent();    
    const currentContentLength = currentContent.getPlainText('').length;
    const selectedTextLength = _getLengthOfSelectedText();
    let _textLength = maxcharacterlimit - (currentContentLength - selectedTextLength)
    if (_textLength > 0) 
    { 
      setTextLength(maxcharacterlimit - (currentContentLength - selectedTextLength))
       
    }    
    setuftext(currentContent.getPlainText(''))
    setEditorState(_editorState);
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
        }
      }
    }

    return length
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
    if (inputvalue !== undefined) {
      const contentstate = getEditorState(inputvalue)
      const currentContent = contentstate.getCurrentContent();
      setuftext(currentContent.getPlainText(''))
      setTextLength(maxcharacterlimit - currentContent.getPlainText('').length)
    }

  }, [inputvalue])

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
        ? actions.submit(cancellor, _editorstateinJSON, JSON.stringify(_mentions), parentId, true,editCommentTypeId)
        : actions.submit(cancellor, _editorstateinJSON, JSON.stringify(_mentions), parentId, false,commentTypeId)

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
        <Grid item xs={12} lg={6}>
          <FormControl component="fieldset">
            <RadioGroup
              id="status-options"
              row
              name="controlled-radio-buttons-group"
              value={editCommentTypeId}
              onChange={(e) => {
                setEditCommentTypeId(Number(e.target.value));
              }}
            >
            <FormControlLabel 
              value={getCommentTypeIdByName(commentTypes, "User submitted")}
              control={<Radio color="default" id="rbextpending" />}
              label="General"
            />
            <FormControlLabel
              value={isMinistry ? getCommentTypeIdByName(commentTypes, "Ministry Internal"):getCommentTypeIdByName(commentTypes, "IAO Internal") }
              control={<Radio color="default" id="rbextapproved" />}
              label="Internal"
            />
            <FormControlLabel
              value={isMinistry ? getCommentTypeIdByName(commentTypes,"Ministry Peer Review"): getCommentTypeIdByName(commentTypes, "IAO Peer Review")}
              control={<Radio color="default" id="rbextdenied" />}
              label="Peer Review"
            />
            </RadioGroup>
          </FormControl>
        </Grid>
        <Editor
          editorState={editorState}
          onChange={_handleChange}
          handleBeforeInput={_handleBeforeInput}
          handlePastedText={_handlePastedText}
          handleKeyCommand={_handleKeyCommand}
          plugins={plugins}
          spellCheck={true}
        />
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
        <MentionSuggestions
          open={open}
          onOpenChange={onOpenChange}
          suggestions={suggestions}
          onSearchChange={(v)=>onSearchChange(v)}
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
            <svg aria-hidden="true" aria-describedby="postComment" focusable="false" data-prefix="fas" data-icon="paper-plane" class="svg-inline--fa fa-paper-plane fa-w-16 fa-2x " role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" disabled={uftext.trim().length === 0} color={uftext.trim().length === 0 ? '#a5a5a5' : 'darkblue'}>
              <title id="postComment" style={{display: 'none'}}>Post Comment</title>
              <path fill="currentColor" d="M476 3.2L12.5 270.6c-18.1 10.4-15.8 35.6 2.2 43.2L121 358.4l287.3-253.2c5.5-4.9 13.3 2.6 8.6 8.3L176 407v80.5c0 23.6 28.5 32.9 42.5 15.8L282 426l124.6 52.2c14.2 6 30.4-2.9 33-18.2l72-432C515 7.8 493.3-6.8 476 3.2z"></path>
            </svg>
          </button>
        </div>
      </div>

    </>
  )
}

export default InputField
