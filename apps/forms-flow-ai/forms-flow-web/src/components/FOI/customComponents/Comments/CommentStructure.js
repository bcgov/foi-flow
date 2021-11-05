import React, { useContext } from 'react'
import './comments.scss'
import Popup from 'reactjs-popup'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faReply, faEllipsisH } from '@fortawesome/free-solid-svg-icons'
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

const CommentStructure = ({ i, reply, parentId,totalcommentCount,currentIndex, isreplysection }) => {
  const actions = useContext(ActionContext)
  const edit = true

  let halfDivclassname = isreplysection ? "halfDiv undermaincomment" : "halfDiv"

  return (
    <div className={halfDivclassname} >
      <div
        className="userInfo"
        style={reply && { marginLeft: 15, marginTop: '6px' }}
      >
        <div className="commentsTwo">
          
          <div className="fullName">{i.fullName} </div> |  <div className="fullName">{i.date} </div>
         
        </div>
        <div className="commenttext">{i.text}</div>
        
        <div>
            <button
              className={`replyBtn ${ totalcommentCount-1 > currentIndex || totalcommentCount == -100 ? " hide" : " show" }`}
              onClick={() => actions.handleAction(i.comId)}
              disabled={!actions.user}
            >
              {' '}
              <FontAwesomeIcon icon={faReply} size='1x' color='#a5a5a5' /> Reply
            </button>
          </div>
      </div>
      <div className="userActions">
        {actions.userId === i.userId && actions.user && (
          <Popup
            role='tooltip'
            trigger={
              <button className="actionsBtn">
                <FontAwesomeIcon icon={faEllipsisH} size='1x' color='darkblue' />
              </button>
            }
            position='right center'
            nested
          >
            <div className="actionDiv">
              <div>
                <button
                  className="editBtn"
                  onClick={() => actions.handleAction(i.comId, edit)}
                >
                  {' '}
                  edit
                </button>
              </div>
              <div>
                <Popup
                  trigger={
                    <button className="deleteBtn"> delete</button>
                  }
                  modal
                  nested
                >
                  {(close) => (
                    <div className='modal' style={modal}>
                      <button
                        className='close'
                        onClick={close}
                        style={modalClose}
                      >
                        &times;
                      </button>
                      <div className='header' style={modalHeader}>
                        {' '}
                        Delete Comment{' '}
                      </div>
                      <div className='content' style={modalContent}>
                        {' '}
                        Delete your comment permanently?
                      </div>
                      <div className='actions' style={modalActions}>
                        <button
                          className='button'
                          style={modalActionBtn}
                          onClick={() => {
                            actions.onDelete(i.comId, parentId)
                            close()
                          }}
                        >
                          Delete
                        </button>
                        <button
                          className='button'
                          style={modalDelBtn}
                          onClick={() => {
                            close()
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
