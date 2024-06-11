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
import Dialog from '@material-ui/core/Dialog';
import Popover from "@material-ui/core/Popover";
import MoreHorizIcon from "@material-ui/icons/MoreHoriz";
import IconButton from "@material-ui/core/IconButton";
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import MenuList from "@material-ui/core/MenuList";
import MenuItem from "@material-ui/core/MenuItem";
import { getOSSHeaderDetails, getFileFromS3 } from "../../../../apiManager/services/FOI/foiOSSServices";
import { saveAs } from "file-saver";
import { downloadZip } from "client-zip";
import { useDispatch } from "react-redux";
import * as html2pdf from 'html-to-pdf-js';
import NewCommentIndicator from './NewCommentIndicator';
import CommunicationUploadModal from './CommunicationUploadModal';


const CommentStructure = ({ i, reply, parentId, totalcommentCount, currentIndex, isreplysection, hasAnotherUserComment, fullName, isEmail=false, ministryId=null}) => {

  const actions = useContext(ActionContext)
  const edit = true
  let needCollapsed = false

  let halfDivclassname = isreplysection ? "halfDiv undermaincomment" : "halfDiv"

  needCollapsed = isreplysection && totalcommentCount > 3 && currentIndex < totalcommentCount - 2 ? true : false


  const dispatch = useDispatch();

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

    let hiddenreplies = document.getElementsByName(`hiddenreply_${parentcommentId}`)
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
  const [communicationUploadModalOpen, setCommunicationUploadModalOpen] = useState(false);
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
        {isEmail ?
          <MenuList>
            <MenuItem
              onClick={(e) => {
                  e.stopPropagation();
                  download();
                  setPopoverOpen(false);
              }}
            >
              Download
            </MenuItem>
            <MenuItem
              onClick={(e) => {
                  e.stopPropagation();
                  setPopoverOpen(false);
                  setCommunicationUploadModalOpen(true);
              }}
            >
              Add Response
            </MenuItem>
          </MenuList> :
          <MenuList>
            <MenuItem
              onClick={(e) => {
                  e.stopPropagation();
                  actions.handleAction(i.commentId, edit)
                  setPopoverOpen(false);
              }}
            >
              Edit
            </MenuItem>
            <MenuItem
              onClick={(e) => {
                  e.stopPropagation();
                  closeTooltip();
                  setDeletePopoverOpen(true);
                  setPopoverOpen(false);
              }}
            >
              Delete
            </MenuItem>
          </MenuList>
        }
      </Popover>
      <DeleteAction />
      <CommunicationUploadModal 
        openModal={communicationUploadModalOpen} 
        setOpenModal={setCommunicationUploadModalOpen}
        message={ { body: "", title: "Add Response" }}
        ministryId={ministryId}
      />
      </>
    );
  };

  const handleDialogClose = () => {
    closeTooltip()
    setDeletePopoverOpen(false);
  }

  const download = async () => {
    let fileInfoList = i.attachments.map(attachment => {
      return  {
        filename: attachment.filename,
        s3sourceuri: attachment.documenturipath
      }
    })
    let blobs = [];
    try {
      const response = await getOSSHeaderDetails(fileInfoList, dispatch);
      for (let header of response.data) {
        await getFileFromS3(header, (_err, res) => {
          let blob = new Blob([res.data], {type: "application/octet-stream"});
          blobs.push({name: header.filename, lastModified: res.headers['last-modified'], input: blob})
        });
      }
    } catch (error) {
      console.log(error)
    }
    const element = document.querySelector(`[data-msg-halfdiv-id="${currentIndex}"]`);
    html2pdf().from(element).outputPdf('blob').then(async (blob) => {
      blobs.push({name: "Email Body.pdf", lastModified: new Date(), input: blob})
      const zipfile = await downloadZip(blobs).blob()
      saveAs(zipfile, fullName + " " + i.date.replace("|", "") + ".zip");
    });
  }

  const DeleteAction = () => {
    return (
        <Dialog
          open={deletePopoverOpen}
          onClose={handleDialogClose}
          aria-label="Delete Comment"
          aria-description="Delete Comment"
          maxWidth={'md'}
          fullWidth={true}
        >
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
                                onClick={handleDialogClose}
                              >
                                Cancel
                              </button>
                            </div>
                          </div>
      </Dialog>
    )
  };

  return (
    <>
      <div className="comment-accordion">
        <Accordion>
          <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            aria-controls="comment-accordion-summary"
            id={`comment-accordion-${currentIndex}`}
          >
              <div {...(isEmail ? {"data-msg-halfdiv-id":`${currentIndex}`} : {})} name={needCollapsed ? `hiddenreply_${parentId}` : `reply_${parentId}`} className={halfDivclassname} style={needCollapsed ? { display: 'none' } : {}} >
                <div
                  className="userInfo"
                  style={reply ? { marginLeft: 15, marginTop: '6px' }: {}}
                >
                  <NewCommentIndicator commentdate={i.dateUF}/>
                  <div className="commentsTwo">
                    <div className="fullName">{fullName} </div> |  <div className="commentdate">{i.date} </div>  <div className="commentdate">{i.edited ? "Edited": ""} </div>
                  </div>
                </div>
              </div>
              <div className="userActions">
                <div>
                  {(isEmail || (i.commentTypeId === 1 && actions.userId === i.userId && actions.user)) && (
                      <>
                          <IconButton
                          aria-label= "actions"
                          id={`ellipse-icon-${currentIndex}`}
                          key={`ellipse-icon-${currentIndex}`}
                          color="primary"
                          onClick={(e) => {
                              e.stopPropagation();
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
                {!isEmail &&
                <div>
                  <button id={`btncomment${i.commentId}`}
                    className={`replyBtn ${(totalcommentCount === -100 || (isreplysection && totalcommentCount - 1 > currentIndex)) ? " hide" : " show"}`}
                    onClick={() => actions.handleAction(i.commentId)}
                    disabled={!actions.user}
                  >
                    {' '}
                    <FontAwesomeIcon icon={faReply} size='1x' color='#003366' /> Reply
                  </button>
                </div>
                }
              </div>
          </AccordionSummary>
          <AccordionDetails>
            <div className="commenttext" dangerouslySetInnerHTML={{ __html: getHtmlfromRawContent() }} >
            </div>
            {isEmail && i.attachments?.map((attachment) => (
            <div className="email-attachment-item" key={attachment.filename}>
              <a href={`/foidocument?id=${ministryId}&filepath=${attachment.documenturipath.split('/').slice(4).join('/')}`} target="_blank">{attachment.filename}</a>
            </div>
            ))}
          </AccordionDetails>
        </Accordion>
        {
          i.replies && i.replies.length > 3 ? <div className="togglecollapseAll"><FontAwesomeIcon icon={toggleIcon} size='1x' color='#003366' /> <span onClick={(e) => toggleCollapse(e, i.commentId)}>Show more comments</span></div> : ""
        }
      </div>
    </>
  )
}

export default CommentStructure