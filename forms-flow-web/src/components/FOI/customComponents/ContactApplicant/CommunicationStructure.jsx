import React, { useContext, useState, useRef, useEffect } from 'react'
import '../Comments/comments.scss'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faReply, faInfoCircle, faCaretDown, faCaretUp } from '@fortawesome/free-solid-svg-icons'
import {
  modal,
  modalHeader,
  modalContent,
  modalActions,
  modalActionBtn,
  modalDelBtn
} from '../Comments/ModalStyles'
import { ActionContext } from '../Comments/ActionContext'
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
import NewCommentIndicator from '../Comments/NewCommentIndicator';
import CommunicationUploadModal from '../Comments/CommunicationUploadModal';
import TextField from "@material-ui/core/TextField";
import AttachmentModal from '../Attachments/AttachmentModal';

const CommunicationStructure = ({ i, reply, parentId, totalcommentCount, currentIndex, isreplysection, hasAnotherUserComment, 
  fullName, isEmail=false, ministryId=null, editDraft, deleteDraft, modalFor, setModalFor,setModal,setUpdateAttachment}) => {

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
      if (i.text) {
        markup = `<p>${i.text}</p>`
      } else {
        markup = `<p></p>`
      }
      
    }
    return markup
  }
  const [popoverOpen, setPopoverOpen] = useState(false);
  const [communicationUploadModalOpen, setCommunicationUploadModalOpen] = useState(false);
  const [anchorPosition, setAnchorPosition] = useState(null);
  const [deletePopoverOpen, setDeletePopoverOpen] = useState(false);
  const [newFilename, setNewFilename] = useState("");
  //const [updateAttachment, setUpdateAttachment] = useState({});
  const [extension, setExtension] = useState("");
  const [errorMessage, setErrorMessage] = useState();
  const [openModal, setOpenModal] = useState(false);


  const parseFileName = (_attachment) => {
    setNewFilename("");
    setExtension("");
    setErrorMessage("");
    if (_attachment && _attachment.filename) {
      let lastIndex = _attachment.filename.lastIndexOf(".");
      setNewFilename(
        lastIndex > 0
          ? _attachment.filename.substr(0, lastIndex)
          : _attachment.filename
      );
      setExtension(
        lastIndex > 0 ? _attachment.filename.substr(lastIndex + 1) : ""
      );
    }
  };

  // const handlePopupButtonClick = (action, _attachment) => {
  //   console.log("_attachment::",_attachment)
  //   console.log("action::",action)
  //   setUpdateAttachment(_attachment);
  //   //setMultipleFiles(false);
  //   switch (action) {
  //     // case "replace":
  //     //   setModalFor("replace");
  //     //   setModal(true);
  //     //   break;
  //     case "rename":
  //       setModalFor("rename");
  //       setModal(true);
  //       break;
  //     case "reclassify":
  //       setModalFor("reclassify");
  //       //setModal(true);
  //       break;
  //     case "download":
  //       //downloadDocument(_attachment);
  //       setModalFor("download");
  //       //setModal(false);
  //       break;
  //     case "delete":
  //       setModalFor("delete")
  //       //setModal(true)
  //       break;
  //     default:
  //       //setModal(false);
  //       break;
  //   }
  // }

  const ActionsPopover = () => {
    return (
      <>
      <Popover
        anchorReference="anchorPosition"
        //onClick={setUpdateAttachment(i.attachments[0])}
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
        {isEmail && i.category === "correspondence" ?
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
          </MenuList> : isEmail && i.category === "draft" ?
          <MenuList>
          <MenuItem
            onClick={(e) => {
              editDraft(i)
            }}
          >
            Edit
          </MenuItem>  
          <MenuItem
            onClick={(e) => {
              deleteDraft(i);
            }}
          >
            Delete
          </MenuItem>
          <MenuItem
              onClick={(e) => {
                  e.stopPropagation();
                  download();
                  setPopoverOpen(false);
              }}
            >
              Download
            </MenuItem>
        </MenuList> : isEmail && i.category === "response" ?
        <MenuList>
        <MenuItem
          onClick={(e) => {
            editDraft(i)
          }}
        >
          Change Date
        </MenuItem>  
        <MenuItem
          onClick={(e) => {
            //handlePopupButtonClick("rename", e)
            setUpdateAttachment(i.attachments[0])
            setModalFor("rename");
            setOpenModal(true);
            setModal(true);
            //deleteDraft(i);
          }}
        >
          Rename
        </MenuItem>
        <MenuItem
            onClick={(e) => {
                e.stopPropagation();
                download();
                setPopoverOpen(false);
            }}
          >
            Download
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
    const elementToClickForExpand = document.querySelector(`#comment-accordion-${currentIndex}`);
    let isAriaExpanded = elementToClickForExpand.ariaExpanded
    if (isAriaExpanded == 'false') elementToClickForExpand.click();
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

  // const handleRename = (_attachment, newFilename) => {
  //   setModal(false);

  //   if (updateAttachment.filename !== newFilename) {
  //     const documentId = ministryId ? updateAttachment.foiministrydocumentid : updateAttachment.foidocumentid;
  //     dispatch(saveNewFilename(newFilename, documentId, requestId, ministryId, (err, _res) => {
  //       if (!err) {
  //         setAttachmentLoading(false);
  //       }
  //     }));
  //   }
  // }

  // const saveNewFilename = () => {
  //   if (validateFilename(newFilename)) {
  //     if (!containDuplicate(newFilename)) {
  //       setErrorMessage("");
  //       handleRename(attachment, newFilename + "." + extension);
  //     } else {
  //       setErrorMessage(
  //         `File name "${newFilename}.${extension}" already exists`
  //       );
  //     }
  //   } else {
  //     setErrorMessage(
  //       `File name cannot be empty and cannot contain these characters, / : * ? " < > |`
  //     );
  //   }
  // };

  const updateFilename = (e) => {
    if (checkInvalidCharacters(e.target.value)) {
      setNewFilename(e.target.value);
      setErrorMessage("");
    } else {
      setErrorMessage(
        `File name cannot contain these characters, / : * ? " < > |`
      );
    }
  };

  const checkInvalidCharacters = (fname) => {
    let rg1 = /^[^\/:*?"<>|]+$/; // forbidden characters  / : * ? " < > |
    return !fname || rg1.test(fname);
  };

  let message = { title: "Rename Attachment", body: "" }

  return (
    <>
      <div className="comment-accordion" {...(isEmail ? {"data-msg-halfdiv-id":`${currentIndex}`} : {})}>
        <Accordion>
          <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            aria-controls="comment-accordion-summary"
            id={`comment-accordion-${currentIndex}`}
          >
              <div name={needCollapsed ? `hiddenreply_${parentId}` : `reply_${parentId}`} className={halfDivclassname} style={needCollapsed ? { display: 'none' } : {}} >
                <div
                  className="userInfo"
                  style={reply ? { marginLeft: 15, marginTop: '6px' }: {}}
                >
                  <NewCommentIndicator commentdate={i.dateUF}/>
                  <div className="commentsTwo">
                    {isEmail && (
                      <>
                      <div className="fullName">{i.category === "response" ? "Applicant Response - ": ""} {fullName} </div> |  <div className="commentdate">{i.date} </div>  
                        <div className="commentdate">{i.edited ? "Edited": ""} </div>
                      </>
                    )
                    }
                    {!isEmail && (
                      <>
                    <div className="fullName">{fullName} </div> |  <div className="commentdate">{i.date} </div>  <div className="commentdate">{i.edited ? "Edited": ""} </div>
                    </>
                    )
                    }
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

{/* <AttachmentModal
modalFor={"rename"}
openModal={openModal}
// handleModal={uploadFor == "response" ? saveResponse : handleContinueModal}
handleModal={uploadFor == "response" ? saveResponse : handleContinueModal}
multipleFiles={true}
requestNumber={requestNumber}
requestId={requestId}
attachmentsArray={files}
existingDocuments={files}
attachment={{}}
handleRename={undefined}
handleReclassify={undefined}
isMinistryCoordinator={false}
uploadFor={uploadFor}
maxNoFiles={10}
bcgovcode={undefined}
/>  */}
// const ModalForRename = ({
//   modalFor,
//   newFilename,
//   updateFilename,
//   errorMessage,
//   extension,
// }) => {
//   console.log("Inside Rename Modal!")
//   return modalFor === "rename" ? (
//     <div className="row">
//       <div className="col-sm-1"></div>
//       <div className="col-sm-9">
//         <TextField
//           id="renameAttachment"
//           label="Rename Attachment"
//           inputProps={{ "aria-labelledby": "renameAttachment-label" }}
//           InputLabelProps={{ shrink: true }}
//           variant="outlined"
//           fullWidth
//           value={newFilename}
//           onChange={updateFilename}
//           error={errorMessage !== undefined && errorMessage !== ""}
//           helperText={errorMessage}
//         />
//       </div>
//       <div className="col-sm-1 extension-name">.{extension}</div>
//       <div className="col-sm-1"></div>
//     </div>
//   ) : null;
// };


export default CommunicationStructure