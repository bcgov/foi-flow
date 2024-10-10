import React, { useContext, useState, useEffect } from 'react'
import { useSelector } from "react-redux"
import './comments.scss'
import { ActionContext } from './ActionContext'
import { setFOILoader } from '../../../../actions/FOI/foiRequestActions'
import Editor, { createEditorStateWithText } from '@draft-js-plugins/editor';
import { convertToRaw, EditorState, RichUtils } from "draft-js";
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
//import createLinkPlugin from '@draft-js-plugins/anchor';
import {namesort,suggestionList } from './commentutils'

import { getFullnameList, getCommentTypeIdByName } from '../../../../helper/FOI/helper'
import Grid from "@material-ui/core/Grid";
import Radio from "@material-ui/core/Radio";
import RadioGroup from "@material-ui/core/RadioGroup";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import FormControl from "@material-ui/core/FormControl";
import Confirm from '../../../../containers/Confirm'
import CustomizedTooltip from '../Tooltip/MuiTooltip/Tooltip';


const staticToolbarPlugin = createToolbarPlugin();
const mentionPlugin = createMentionPlugin();
const { Toolbar } = staticToolbarPlugin;
const { MentionSuggestions } = mentionPlugin
const plugins = [staticToolbarPlugin, mentionPlugin];
const AddCommentField = ({ cancellor, parentId, add, fullnameList , restrictedReqTaglist,  //setEditorChange, removeComment and setRemoveComment added to handle Navigate away from Comments tabs 
  setEditorChange, removeComment, setRemoveComment, isRestricted, isMinistry, setshowaddbox, commentTypes, commentTypeId, setCommentTypeId }) => {
  let maxcharacterlimit = 1000  
  const [uftext, setuftext] = useState('')
  const [textlength, setTextLength] = useState(1000)
  const [open, setOpen] = useState(false);

  const isCommentTagListLoading = useSelector((state) => state.foiRequests.isCommentTagListLoading);
  let fulluserlist = suggestionList([...fullnameList]).sort(namesort)


  const [mentionList, setMentionList] = useState(isCommentTagListLoading ? [{name: 'Loading...'}] : isRestricted ? restrictedReqTaglist :fulluserlist);
  const [suggestions, setSuggestions] = useState(mentionList);
  const [editorState, setEditorState] = useState(EditorState.createEmpty())
  
  const [confirmModalOpen, setConfirmModalOpen] = useState(false);
  
  useEffect(() => {
    setMentionList(isCommentTagListLoading ? [{name: 'Loading...'}] : isRestricted ? restrictedReqTaglist :suggestionList([...fulluserlist]).sort(namesort));
    setSuggestions(isCommentTagListLoading ? [{name: 'Loading...'}] : isRestricted ? restrictedReqTaglist :suggestionList([...fulluserlist]).sort(namesort));
  }, [fullnameList])


  const onOpenChange = (_open) => {
    setOpen(_open);
  }

  // Check editor text for mentions
  const onSearchChange = ({ value }) => {
    let filterlist = isCommentTagListLoading ? mentionList : mentionList.filter(function(item){
      return (item.firstname?.toLowerCase()?.indexOf(value.toLowerCase()) === 0 || item.lastname?.toLowerCase()?.indexOf(value.toLowerCase()) === 0)
    }).sort(namesort)  
    setSuggestions(defaultSuggestionsFilter(value, filterlist))
  }

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
    if(_textLength > 0)
      {setTextLength(maxcharacterlimit - (currentContentLength - selectedTextLength))}
  
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
    //For enabling keyboard shortcuts 
    const newState = RichUtils.handleKeyCommand(editorState, e);
    if (newState) {
      setEditorState(newState);
      return 'handled';
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


  const post = () => {
    if (uftext !== '' && uftext.trim().length > 0) {
      setshowaddbox(false)
      const _mentions = getMentionsOnComment()
      const _editorstateinJSON = JSON.stringify(convertToRaw(editorState.getCurrentContent()))
      setFOILoader(true)    
      actions.submit(cancellor, _editorstateinJSON, JSON.stringify(_mentions), parentId, false, commentTypeId)
      setEditorState(createEditorStateWithText(''))
      setEditorChange(false)
      setTextLength(1000);
    }

  }


  //Handles Navigate Away
  useEffect(() => {
    if (removeComment) {
      if (add) {
        setEditorState(EditorState.createEmpty())
        setuftext('')
      }    
      setRemoveComment(false);
    }
  })

  useEffect(() => {
    setMentionList(isCommentTagListLoading ? [{name: 'Loading...'}] : isRestricted ? restrictedReqTaglist :suggestionList([...fulluserlist]).sort(namesort));
    setSuggestions(isCommentTagListLoading ? [{name: 'Loading...'}] : isRestricted ? restrictedReqTaglist :suggestionList([...fulluserlist]).sort(namesort));
  }, [isCommentTagListLoading, restrictedReqTaglist])

  let formclass = !parentId ? "parentform form" : "form"
  formclass = add ? `${formclass} addform` : formclass

  const actions = useContext(ActionContext)

  const cancelComment = () => {
    setshowaddbox(false)
    setEditorState(createEditorStateWithText(''))
  }

  const openConfirmModal = () =>{
    setConfirmModalOpen(true)
  }

  const closeConfirmModal = () => {
    setConfirmModalOpen(false);
  };

  const tooltipPreview = {
    "title": "Comment Types",
    "content": [
      <div className="toolTipContent">
        <p>Internal and Peer Review comments are only visible to your team.</p>
      </div>]
  };

  //const isActive = editorState.getCurrentInlineStyle().has('BOLD');
 
 
  return (
    <>
      <form className={formclass}>
        <Grid item xs={10} lg={5} style={{ position: 'relative' }}>
          <FormControl component="fieldset">
            <RadioGroup
              id="status-options"
              row
              name="controlled-radio-buttons-group"
              value={commentTypeId}
              onChange={(e) => {
                setCommentTypeId(Number(e.target.value));
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
          <div className="commentToolTip">
              <CustomizedTooltip content={tooltipPreview} position={""} style={{width: '70px'}} />
              <p className="hideContent" id="commenttype-info">CommentTypeInfo</p>
          </div>
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
        <div style={{ display: 'flex', alignItems: 'center', position: 'sticky' }}>
          <Toolbar>
            {
              (externalProps) => {
                return(
                <>
                <div>
                  <BoldButton {...externalProps} />
                  <ItalicButton {...externalProps} />
                  <UnderlineButton {...externalProps} />
                  <UnorderedListButton {...externalProps} />
                  <OrderedListButton {...externalProps} />
                </div>
              </>
                )
              }
            }
          </Toolbar>
          <div className={'col-lg-9'} style={{ marginLeft: '10px' }}>
            <span className={textlength > 25 ? "characterlen" : "characterlen textred"}>
              {textlength} characters remaining
            </span>
          </div>
        </div>
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
      <div className="newCommentInputActions">
        {/* <div className={'col-lg-9'}>
          <span className={textlength > 25 ? "characterlen" : "characterlen textred"}>{textlength} characters remaining</span>
        </div> */}
        <button
            className="btnCancel"
            onClick={() => openConfirmModal() }
          >
            Cancel
          </button>
        <div> 
          {/* paperplanecontainer */}
          <button
            className= "btn-bottom btn btn-save" //"postBtn"
            style={{width:'200px', marginLeft:'10px', marginRight:'0px'}}
            onClick={post}
            type='button'
            disabled={uftext.trim().length === 0}
          >
            {'Post Comment'}
            <svg aria-hidden="true" role="img" aria-describedby="addComment" focusable="false" data-prefix="fas" data-icon="paper-plane" 
              class="svg-inline--fa fa-paper-plane fa-w-16 fa-1x post-comment-btn" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" 
              disabled={uftext.trim().length === 0} color={ uftext.trim().length === 0 ? '#a5a5a5' : 'darkblue'}>
                <title id="addComment" style={{display: 'none'}}>Add Comment</title>
                <path fill="currentColor" d="M476 3.2L12.5 270.6c-18.1 10.4-15.8 35.6 2.2 43.2L121 358.4l287.3-253.2c5.5-4.9 13.3 2.6 8.6 8.3L176 407v80.5c0 23.6 28.5 32.9 42.5 15.8L282 426l124.6 52.2c14.2 6 30.4-2.9 33-18.2l72-432C515 7.8 493.3-6.8 476 3.2z"></path>
            </svg>
          </button>
        </div>
      </div>
      {confirmModalOpen &&
          <Confirm
            modalOpen={confirmModalOpen} 
            onYes={closeConfirmModal} 
            onNo={cancelComment }
            message={"Are you sure you want to cancel? You will lose anything you have entered."} 
            yesText = 'Continue Comment'
            noText = 'Cancel'
          />
      }
    </>
  )
}

export default AddCommentField
