import React, { useContext, useEffect, useState,useRef  } from 'react'
import { useDispatch, useSelector } from "react-redux";
import './comments.scss'
import Popup from 'reactjs-popup'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faReply, faEllipsisH, faInfoCircle } from '@fortawesome/free-solid-svg-icons'
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
import { fetchFOIFullAssignedToList, fetchFOIMinistryAssignedToList } from '../../../../apiManager/services/FOI/foiRequestServices'
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';


const CommentStructure = ({ i, reply, parentId, totalcommentCount, currentIndex, isreplysection, bcgovcode, hasAnotherUserComment, fullName }) => {

  const actions = useContext(ActionContext)
  const edit = true

  let halfDivclassname = isreplysection ? "halfDiv undermaincomment" : "halfDiv"

  const ref = useRef();  
  const closeTooltip = () => ref.current.close();

  return (

    <div className={halfDivclassname} >
      <div
        className="userInfo"
        style={reply && { marginLeft: 15, marginTop: '6px' }}
      >
        <div className="commentsTwo">

          <div className="fullName">{fullName} </div> |  <div className="commentdate">{i.date} </div>

        </div>
        <div className="commenttext">

          <ReactQuill  value={i.text} readOnly={true} theme={"bubble"} />
        </div>

        <div>
          <button
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
              <button className="actionsBtn">
                <FontAwesomeIcon icon={faEllipsisH} size='1x' color='#003366' />
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

                      <div className='header' style={modalHeader}>
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
                            close();closeTooltip()
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
  )
}

export default CommentStructure
