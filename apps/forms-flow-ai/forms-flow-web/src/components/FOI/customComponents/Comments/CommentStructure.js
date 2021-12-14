import React, { useContext, useEffect, useState, useRef } from 'react'
import { useDispatch, useSelector } from "react-redux";
import './comments.scss'
import Popup from 'reactjs-popup'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faReply, faEllipsisH, faInfoCircle, faCaretDown, faCaretUp } from '@fortawesome/free-solid-svg-icons'
import {
  modal,
  modalClose,
  modalHeader,
  modalContent,
  modalActions,
  modalActionBtn,
  modalDelBtn
} from './ModalStyles'
import { ActionContext } from './ActionContext'
import 'react-quill/dist/quill.snow.css';
import draftToHtml from 'draftjs-to-html';
import { convertToRaw,convertFromRaw,  EditorState } from "draft-js";


const CommentStructure = ({ i, reply, parentId, totalcommentCount, currentIndex, isreplysection, bcgovcode, hasAnotherUserComment, fullName }) => {

  const actions = useContext(ActionContext)
  const edit = true
  let needCollapsed = false

  let halfDivclassname = isreplysection ? "halfDiv undermaincomment" : "halfDiv"

  needCollapsed = isreplysection && totalcommentCount > 3 && currentIndex < totalcommentCount - 2 ? true : false


  const [toggleIcon, settoggleIcon] = useState(faCaretDown)

  const ref = useRef();
  const closeTooltip = () => ref.current && ref ? ref.current.close():{};

  const toggleCollapse = (e, parentId) => {

    var hiddenreplies = document.getElementsByName(`hiddenreply_${parentId}`)
    hiddenreplies.forEach((commentnode) => {
      commentnode.style.display === 'none' ? commentnode.style.display = 'flex' : commentnode.style.display = 'none'
    })
    let _toggleIcon = e.target.innerText === "Show more comments" ? faCaretUp : faCaretDown
    settoggleIcon(_toggleIcon)
    e.target.innerText === "See few comments" ? e.target.innerText = "Show more comments" : e.target.innerText = "See few comments"

  }

  const getHtmlfromRawContent =()=>{

    const rawContentFromStore = convertFromRaw(JSON.parse(i.text))
    let initialEditorState = EditorState.createWithContent(rawContentFromStore);
    
    const rawContentState = convertToRaw(initialEditorState.getCurrentContent());
    let markup = draftToHtml(
      rawContentState
    );  

    return markup
  }

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
          <div className="commenttext" dangerouslySetInnerHTML={{__html:getHtmlfromRawContent()}} >
          
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
        <div className="userActions">
          {actions.userId === i.userId && actions.user && (
            <Popup
              ref={ref}
              role='tooltip'
              trigger={
                i.commentTypeId === 1 ?
                <button className="actionsBtn">
                  <FontAwesomeIcon icon={faEllipsisH} size='1x' color='#003366' />
                </button> :
                <button className="actionsBtn" disabled>
                <FontAwesomeIcon icon={faEllipsisH} size='1x' color='grey' />
              </button>
              }
              position='right center'
              nested
              closeOnDocumentClick
            >
              <div className="actionDiv">
                <div>
                  <button
                    className="editBtn"
                    onClick={() => actions.handleAction(i.commentId, edit)}
                  >
                    {' '}
                    edit
                  </button>
                </div>
                <div>
                  <Popup
                    trigger={
                      <button className="deleteBtn" onClick={closeTooltip}> delete</button>
                    }
                    modal
                    nested
                    closeOnDocumentClick
                  >
                    {(close) => (
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
                                  close()
                                }}
                              >
                                Delete
                              </button>
                          }
                          <button
                            className='button btn-bottom'
                            style={modalDelBtn}
                            onClick={() => {
                              close(); closeTooltip()
                            }}
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    )}
                  </Popup>
                </div>
              </div>
            </Popup>
          )}
        </div>
      </div>
      {
        i.replies && i.replies.length > 3 ? <div className="togglecollapseAll"><FontAwesomeIcon icon={toggleIcon} size='1x' color='#003366' /> <span onClick={(e) => toggleCollapse(e, i.commentId)}>Show more comments</span></div> : ""
      }
    </>
  )
}

export default CommentStructure
