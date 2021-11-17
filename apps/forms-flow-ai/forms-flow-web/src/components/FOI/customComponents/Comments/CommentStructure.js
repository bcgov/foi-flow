import React, { useContext, useEffect, useState } from 'react'
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


const CommentStructure = ({ i, reply, parentId, totalcommentCount, currentIndex, isreplysection, bcgovcode, hasAnotherUserComment }) => {




  const actions = useContext(ActionContext)
  const edit = true

  let halfDivclassname = isreplysection ? "halfDiv undermaincomment" : "halfDiv"

  const dispatch = useDispatch();
  useEffect(() => {
    dispatch(fetchFOIFullAssignedToList());
    if (bcgovcode)
      dispatch(fetchFOIMinistryAssignedToList(bcgovcode));
  }, [dispatch]);

  let iaoassignedToList = useSelector((state) => state.foiRequests.foiFullAssignedToList);
  let ministryAssignedToList = useSelector(state => state.foiRequests.foiMinistryAssignedToList);
  let fullName = ''

  var _sessionuser = localStorage.getItem(i.userId)
  
  if (_sessionuser === undefined || _sessionuser === '' || _sessionuser === null) {
    
    iaoassignedToList.forEach(function (obj) {
      var groupmembers = obj.members
      var user = groupmembers.find(m => m["username"] === i.userId)
      if (user && user != undefined) {
        fullName = `${user["lastname"]}, ${user["firstname"]}`       
        localStorage.setItem(i.userId, fullName)
        return true;
      }
    })

    if (fullName === '') {     
      ministryAssignedToList.forEach(function (obj) {
        var groupmembers = obj.members
        var user = groupmembers.find(m => m["username"] === i.userId)
        if (user && user != undefined) {          
          fullName = `${user["lastname"]}, ${user["firstname"]}`          
          localStorage.setItem(i.userId, fullName)
          return true;
        }
      })
    }

  }
  else {
    console.log(`ELse condition for full name ${fullName}`)
    fullName = _sessionuser
  }

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

          <ReactQuill value={i.text} readOnly={true} theme={"bubble"} />
        </div>

        <div>
          <button
            className={`replyBtn ${totalcommentCount === -100 || (isreplysection && totalcommentCount - 1 > currentIndex) ? " hide" : " show"}`}
            onClick={() => actions.handleAction(i.commentId)}
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
                  onClick={() => actions.handleAction(i.commentId, edit)}
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
                    <div className='modal deletemodal' style={modal}>

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
