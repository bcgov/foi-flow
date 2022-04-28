import React, { useContext, useState, useRef } from 'react'
import './comments.scss'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faReply, faInfoCircle, faCaretDown, faCaretUp } from '@fortawesome/free-solid-svg-icons'
import {
  modal,
  modalHeader,
  modalContent,
  modalActions,
  modalActionBtn,
  modalDelBtn
} from './ModalStyles'
import { ActionContext } from './ActionContext'
import 'react-quill/dist/quill.snow.css';
import draftToHtml from 'draftjs-to-html';
import { convertToRaw, convertFromRaw, EditorState } from "draft-js";
import Popover from "@material-ui/core/Popover";
import MoreHorizIcon from "@material-ui/icons/MoreHoriz";
import IconButton from "@material-ui/core/IconButton";
import MenuList from "@material-ui/core/MenuList";
import MenuItem from "@material-ui/core/MenuItem";


const CommentStructure = ({ i, reply, parentId, totalcommentCount, currentIndex, isreplysection, bcgovcode, hasAnotherUserComment, fullName }) => {

  const actions = useContext(ActionContext)
  const edit = true
  let needCollapsed = false

  let halfDivclassname = isreplysection ? "halfDiv undermaincomment" : "halfDiv"

  needCollapsed = isreplysection && totalcommentCount > 3 && currentIndex < totalcommentCount - 2 ? true : false


  const [toggleIcon, settoggleIcon] = useState(faCaretDown)

  const ref = useRef();
  const closeTooltip = () => ref.current && ref ? ref.current.close() : {};

  const setInnerText = (e, text) => {
    e.target.innerText = text
  }

  const setnodeDisplay = (commentnode, displaymode) => {
    commentnode.style.display = displaymode
  }

  const toggleCollapse = (e, parentcommentId) => {

    var hiddenreplies = document.getElementsByName(`hiddenreply_${parentcommentId}`)
    hiddenreplies.forEach((commentnode) => {
      commentnode.style.display === 'none' ? setnodeDisplay(commentnode, 'flex') : setnodeDisplay(commentnode, 'none')
    })
    let _toggleIcon = e.target.innerText === "Show more comments" ? faCaretUp : faCaretDown
    settoggleIcon(_toggleIcon)
    e.target.innerText === "Show fewer comments" ? setInnerText(e, "Show more comments") : setInnerText(e, "Show fewer comments")
  }

  const getHtmlfromRawContent = () => {
    let markup = null
    if (i.commentTypeId === 1) {
      const rawContentFromStore = convertFromRaw(JSON.parse(i.text))
      let initialEditorState = EditorState.createWithContent(rawContentFromStore);

      const rawContentState = convertToRaw(initialEditorState.getCurrentContent());
      const entityMap = rawContentState.entityMap;
      markup = draftToHtml(
        rawContentState
      );
      let commentmentions = []
      let updatedMarkup = ''

      Object.values(entityMap).forEach(entity => {
        if (entity.type === 'mention') {
          commentmentions.push(entity.data.mention.name);
        }

      });
      const distinctMentions = [... new Set(commentmentions)]
      distinctMentions.forEach(_mention => {
        updatedMarkup = markup.replaceAll(_mention, `<span class='taggeduser'>${_mention}</span>`)
        markup = updatedMarkup
      })
    }
    else {
      markup = `<p>${i.text}</p>`
    }

    return markup
  }
  const [popoverOpen, setPopoverOpen] = useState(false);
  const [anchorPosition, setAnchorPosition] = useState(null);
  const [deletePopoverOpen, setDeletePopoverOpen] = useState(false);



  const ActionsPopover = () => {
    return (
      <>
      <Popover
        anchorReference="anchorPosition"
        anchorPosition={
          anchorPosition && {
            top: anchorPosition.top,
            left: anchorPosition.left,
          }
        }
        open={popoverOpen}
        anchorOrigin={{
          vertical: "top",
          horizontal: "left",
        }}
        transformOrigin={{
          vertical: "top",
          horizontal: "left",
        }}
        onClose={() => setPopoverOpen(false)}
      >
        <MenuList>
          <MenuItem
            onClick={() => {
                actions.handleAction(i.commentId, edit)
                setPopoverOpen(false);
            }}
          >
            Edit
          </MenuItem>
          <MenuItem
            onClick={() => {
                closeTooltip();
                setDeletePopoverOpen(true);
                setPopoverOpen(false);
            }}
          >
            Delete
            
            
          </MenuItem>          
        </MenuList>
      </Popover>
      <DeleteAction />
      </>
    );
  };



  const DeleteAction = () => {
    console.log(`deletePopoverOpen === ${deletePopoverOpen}`)
    return (
      <>
      {deletePopoverOpen ? 
     
                        
                          <div id="deletemodal" onBlur={closeTooltip} className='modal deletemodal' style={modal}>
  
                            <div className='header' style={modalHeader} >
                              {' '}
                              Delete Comment{' '}
                            </div>
                            <div className='content' style={modalContent}>
                              {hasAnotherUserComment ? <><FontAwesomeIcon icon={faInfoCircle} size='1x' color='darkblue' /><span className="deletevalidationInfo">Parent comments with a reply cannot be deleted. You may edit the comment.</span></> :
                                ' Delete your comment permanently?'}
                            </div>
                            <div className='actions' style={modalActions}>
                              {
                                hasAnotherUserComment ?
                                  <button
                                    className='button'
                                    style={modalActionBtn}
  
                                    disabled
                                  >
                                    Delete
                                  </button>
                                  :
                                  <button
                                    className='button btn-bottom'
                                    style={modalActionBtn}
  
                                    onClick={() => {
                                      actions.onDelete(i.commentId, parentId)
                                      setDeletePopoverOpen(false);
                                      closeTooltip()
                                    }}
                                  >
                                    Delete
                                  </button>
                              }
                              <button
                                className='button btn-bottom'
                                style={modalDelBtn}
                                onClick={() => {
                                  
                                  closeTooltip()
                                  setDeletePopoverOpen(false);
                                }}
                              >
                                Cancel
                              </button>
                            </div>
                          </div>
                       
                        : null }
                        </>
    )
  };

  return (
    <>
      <div name={needCollapsed ? `hiddenreply_${parentId}` : `reply_${parentId}`} className={halfDivclassname} style={needCollapsed ? { display: 'none' } : {}} >
        <div
          className="userInfo"
          style={reply && { marginLeft: 15, marginTop: '6px' }}
        >
          <div className="commentsTwo">

            <div className="fullName">{fullName} </div> |  <div className="commentdate">{i.date} </div>

          </div>
          <div className="commenttext" dangerouslySetInnerHTML={{ __html: getHtmlfromRawContent() }} >

          </div>

            
        </div>
        <div className="userActions">
          <div>
            {i.commentTypeId === 1 && actions.userId === i.userId && actions.user && (
                <>
                    <IconButton
                    aria-label= "actions"
                    id={`ellipse-icon-${currentIndex}`}
                    key={`ellipse-icon-${currentIndex}`}
                    color="primary"
                    onClick={(e) => {
                        setPopoverOpen(true);
                        setAnchorPosition(
                        e.currentTarget.getBoundingClientRect()
                        );
                    }}                      
                    >
                    <MoreHorizIcon />
                    </IconButton>
                    <ActionsPopover />
                </>
            )}
          </div>
          <div>
            <button id={`btncomment${i.commentId}`}
              className={`replyBtn ${totalcommentCount === -100 || (isreplysection && totalcommentCount - 1 > currentIndex) ? " hide" : " show"}`}
              onClick={() => actions.handleAction(i.commentId)}
              disabled={!actions.user}
            >
              {' '}
              <FontAwesomeIcon icon={faReply} size='1x' color='#003366' /> Reply
            </button>
          </div>
        </div>
      </div>
      {
        i.replies && i.replies.length > 3 ? <div className="togglecollapseAll"><FontAwesomeIcon icon={toggleIcon} size='1x' color='#003366' /> <span onClick={(e) => toggleCollapse(e, i.commentId)}>Show more comments</span></div> : ""
      }
    </>
  )
}

export default CommentStructure