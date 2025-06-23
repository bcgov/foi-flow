import React, { useContext, useState, useRef, useEffect } from 'react'
//import '../Comments/comments.scss'
import { faCaretDown } from '@fortawesome/free-solid-svg-icons'
import {
  modal,
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
import Tooltip from "@mui/material/Tooltip";
import { getOSSHeaderDetails, getFileFromS3 } from "../../../../apiManager/services/FOI/foiOSSServices";
import { saveAs } from "file-saver";
import { downloadZip } from "client-zip";
import { useDispatch, useSelector } from "react-redux";
import * as html2pdf from 'html-to-pdf-js';
import { ClickableChip } from '../../Dashboard/utils';
import { toast } from 'react-toastify';
import { getTemplateVariables } from './util';
import { DownloadCorrespondenceModal } from './DownloadCorrespondenceModal';

const CommunicationStructure = ({
  correspondence, 
  requestNumber, 
  currentIndex,
  fullName, 
  ministryId=null, 
  editDraft, 
  deleteDraft, 
  deleteResponse, 
  modalFor, 
  setModalFor,
  setModal,
  setUpdateAttachment, 
  setSelectedCorrespondence, 
  setCurrentResponseDate, 
  applicantCorrespondenceTemplates, 
  templateVariableInfo,
  showRenameCorrespondenceSubjectModal
}) => {

  // console.log("correspondence: ", correspondence);
  const templateList = useSelector((state) => state.foiRequests.foiEmailTemplates);
  const requestDetails = useSelector((state) => state.foiRequests.foiRequestDetail);
  const dispatch = useDispatch();
  const [popoverOpen, setPopoverOpen] = useState(false);
  const [communicationUploadModalOpen, setCommunicationUploadModalOpen] = useState(false);
  const [downloadCorrespondenceModalOpen, setDownloadCorrespondenceModalOpen] = useState(false);
  const [anchorPosition, setAnchorPosition] = useState(null);
  const [attachmentAnchorPosition, setAttachmentAnchorPosition] = useState(null);
  const [attachmentPopoverOpen, setAttachmentPopoverOpen] = useState(false)
  const [attachmentDownloadLink, setAttachmentDownloadLink] = useState('')
  const [deletePopoverOpen, setDeletePopoverOpen] = useState(false);
  const ref = useRef();
  const closeTooltip = () => ref.current && ref ? ref.current.close() : {};


  const getHtmlfromRawContent = () => {
    let markup = null
    // if (correspondence.commentTypeId === 1) {
    //   const rawContentFromStore = convertFromRaw(JSON.parse(correspondence.text))
    //   let initialEditorState = EditorState.createWithContent(rawContentFromStore);
    //   const rawContentState = convertToRaw(initialEditorState.getCurrentContent());
    //   const entityMap = rawContentState.entityMap;
    //   markup = draftToHtml(
    //     rawContentState
    //   );
    //   let commentmentions = []
    //   let updatedMarkup = ''

    //   Object.values(entityMap).forEach(entity => {
    //     if (entity.type === 'mention') {
    //       commentmentions.push(entity.data.mention.name);
    //     }

    //   });
    //   const distinctMentions = [... new Set(commentmentions)]
    //   distinctMentions.forEach(_mention => {
    //     updatedMarkup = markup.replaceAll(_mention, `<span class='taggeduser'>${_mention}</span>`)
    //     markup = updatedMarkup
    //   })
    // }
    // else {
      if (correspondence.text) {
        markup = `<p>${correspondence.text}</p>`
      } else {
        markup = `<p></p>`
      }
      
    //}
    return markup
  }

  useEffect(() => {
    if (downloadCorrespondenceModalOpen == false) setModalFor("add")
  }, [downloadCorrespondenceModalOpen])

  const ActionsPopover = () => {

    const renderCorrespondenceMenuItems = () => (
      <>
        <MenuItem
          onClick={(e) => {
            e.stopPropagation();
            setSelectedCorrespondence(correspondence);
            showRenameCorrespondenceSubjectModal();
            setPopoverOpen(false);
          }}
        >
          Rename Subject
        </MenuItem>
        <MenuItem
          onClick={() => {
            setModalFor("changeresponsedate");
            setCurrentResponseDate(correspondence.date);
            setModal(true);
            setSelectedCorrespondence(correspondence);
            setPopoverOpen(false);
          }}
        >
          Change Date
        </MenuItem>
        <MenuItem
          onClick={(e) => {
            e.stopPropagation();
            setModalFor("downloadcorrespondence")
            setDownloadCorrespondenceModalOpen(true);
            setPopoverOpen(false);
          }}
        >
          Download
        </MenuItem>
      </>
    );
  
    const renderDraftMenuItems = () => (
      <>
        <MenuItem onClick={() => {
          editDraft(correspondence)
          setPopoverOpen(false);
        }}>Edit</MenuItem>
        <MenuItem
          onClick={(e) => {
            e.stopPropagation();
            setModalFor("downloaddraft")
            setDownloadCorrespondenceModalOpen(true);
            setPopoverOpen(false);
        }}>Download</MenuItem>
        <MenuItem onClick={() => {
          deleteDraft(correspondence)
          setPopoverOpen(false);
        }}>Delete</MenuItem>
      </>
    );
  
    const renderResponseMenuItems = () => (
      <>
        <MenuItem
          onClick={() => {
            setModalFor("changeresponsedate");
            setCurrentResponseDate(correspondence.date);
            setModal(true);
            setSelectedCorrespondence(correspondence);
            setPopoverOpen(false);
          }}
        >
          Change Date
        </MenuItem>
        <MenuItem
          onClick={(e) => {
            e.stopPropagation();
            setSelectedCorrespondence(correspondence);
            showRenameCorrespondenceSubjectModal();
            setPopoverOpen(false);
          }}
        >
          Rename Subject
        </MenuItem>
        <MenuItem
          onClick={(e) => {
            e.stopPropagation();
            setModalFor("downloadcorrespondence")
            setDownloadCorrespondenceModalOpen(true);
            setPopoverOpen(false);
          }}
        >
          Download
        </MenuItem>
        <MenuItem onClick={() => deleteResponse(correspondence)}>Delete</MenuItem>
      </>
    );
  
    return (
      <div>
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
          {correspondence && (
            <MenuList>
              {correspondence.category === "correspondence" && renderCorrespondenceMenuItems()}
              {correspondence.category === "draft" && renderDraftMenuItems()}
              {correspondence.category === "response" && renderResponseMenuItems()}
            </MenuList>
          )}
        </Popover>
        {/* <DeleteAction /> */}
        <DownloadCorrespondenceModal modalOpen={downloadCorrespondenceModalOpen} setModalOpen={setDownloadCorrespondenceModalOpen} handleSave={download} modalFor={modalFor} />
      </div>
    );
  };

  const renderAttachmentMenuItems = () => (
    <>
      <MenuItem
        onClick={(e) => {
          e.stopPropagation();
          setModalFor("rename");
          setModal(true);
          setSelectedCorrespondence(correspondence);
          setPopoverOpen(false);
        }}
      >
        Rename Attachment
      </MenuItem>
      <MenuItem
        onClick={(e) => {
          e.stopPropagation();
          setPopoverOpen(false);
        }}
      >
        <a style={{color: "black", textDecoration: "none"}} href={attachmentDownloadLink} target="_blank">
          Download</a>
      </MenuItem>
    </>
  )

  const AttachmentActionsPopover = () => {
    return (<Popover
    anchorReference="anchorPosition"
    anchorPosition={
      attachmentAnchorPosition && {
        top: attachmentAnchorPosition.top,
        left: attachmentAnchorPosition.left,
      }
    }
    open={attachmentPopoverOpen}
    anchorOrigin={{
      vertical: "top",
      horizontal: "left",
    }}
    transformOrigin={{
      vertical: "top",
      horizontal: "left",
    }}
    onClose={() => setAttachmentPopoverOpen(false)}
  >
    {correspondence && (
      <MenuList>
        {renderAttachmentMenuItems()}
      </MenuList>
    )}
  </Popover>)
  }

  const handleDialogClose = () => {
    closeTooltip()
    setDeletePopoverOpen(false);
  }

  const download = async () => {
    setDownloadCorrespondenceModalOpen(false);
    let fileInfoList = correspondence.attachments.map(attachment => {
      return  {
        filename: attachment.filename,
        s3sourceuri: attachment.documenturipath
      }
    })
    let blobs = [];
    const toastID = toast.loading(`Downloading correspondence ${correspondence.category == "draft" ? "draft" : ""}...`);
    try {
      const response = await getOSSHeaderDetails(fileInfoList, dispatch);
      for (let header of response.data) {
        await getFileFromS3(header, (_err, res) => {
          let blob = new Blob([res.data], {type: "application/octet-stream"});
          blobs.push({name: header.filename, lastModified: res.headers['last-modified'], input: blob})
        });
      }
      toast.update(toastID, {
        render: `Correspondence ${correspondence.category == "draft" ? "draft " : ""}download complete`,
        type: "success",
        className: "file-upload-toast",
        isLoading: false,
        autoClose: 3000,
        hideProgressBar: true,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        closeButton: true
      });
    } catch (error) {
      console.log(error)
      toast.update(toastID, {
        render: `Correspondence ${correspondence.category == "draft" ? "draft " : ""}download failed`,
        type: "error",
        className: "file-upload-toast",
        isLoading: false,
        autoClose: 3000,
        hideProgressBar: true,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        closeButton: true
      });
    }
    const headerDiv = document.createElement("div");

    headerDiv.innerText = `Email from: ${requestDetails?.assignedGroupEmail}\n${getFullEmailListText() || 'Email to: None selected'}\n ${getFullCCEmailListText() || 'CC to: None selected'}\nEmail Subject: ${correspondence?.subject}\nSent: ${correspondence?.date}\n`;
    headerDiv.style.fontSize = "12px";
    headerDiv.style.fontFamily = "BCSans"
    headerDiv.style.marginBottom = "20px";
    let element = headerDiv.outerHTML
    if (correspondence?.text) element = element + correspondence?.text

    // For drafts, remove the relevant variables that have been filled in
    if (correspondence.category == "draft") {
      const template = applicantCorrespondenceTemplates.find(template => template.templateid == correspondence.templateid)
      const { requestDetails, requestExtensions, responsePackagePdfStitchStatus, cfrFeeData } = templateVariableInfo
      let variables = getTemplateVariables(requestDetails,requestExtensions, responsePackagePdfStitchStatus, cfrFeeData, template)
      let firstName, lastName, address, secondaryAddress, postal;
      variables.forEach((variable) => {
        if (variable.name == "{{firstName}}") firstName = variable.value
        if (variable.name == "{{lastName}}") lastName = variable.value
        if (variable.name == "{{address}}") address = variable.value
        if (variable.name == "{{secondaryAddress}}") secondaryAddress = variable.value
        if (variable.name == "{{postal}}") postal = variable.value
      })
      let addressStartIndex = element.indexOf(address) // -1 if undefined
      let secondaryAddressStartIndex = element.indexOf(secondaryAddress)
      let postalStartIndex = element.indexOf(postal)
      let endIndex;
      if (postalStartIndex != -1 && postal) endIndex = postalStartIndex + postal.length // if postal code exists, it is end of address string
      if (secondaryAddressStartIndex != -1 && secondaryAddress) endIndex = secondaryAddressStartIndex + secondaryAddress.length // if secondary address
      if (postalStartIndex == -1 && secondaryAddressStartIndex == -1 && addressStartIndex != -1 && address) endIndex = addressStartIndex + address.length // if only primary
      // slice must be done first so indexes don't change
      if (addressStartIndex && addressStartIndex != -1 && endIndex && endIndex != -1) {
        element = element.slice(0, addressStartIndex) + 'ADDRESS REDACTED' + element.slice(endIndex)
      }
      // then replace first and last name
      element = element.replaceAll(firstName, 'APPLICANT')
      element = element.replaceAll(lastName, 'APPLICANT')
    }
    let emailFilename = correspondence?.subject ? `${correspondence?.subject}.pdf` : `Correspondence Letter - ${requestNumber}.pdf`
    html2pdf().set({margin: 20}).from(element).outputPdf('blob').then(async (blob) => {
      blobs.push({name: emailFilename, lastModified: new Date(), input: blob})
      const zipfile = await downloadZip(blobs).blob()
      saveAs(zipfile, fullName + " " + correspondence.date.replace(/\|/g, "") + ".zip");
    });
  }


  const getTemplateName = (correspondence) => {
    if (correspondence?.subject) return correspondence.subject
    if (!correspondence?.sentby && correspondence?.templatename) return templateList.find((obj)=> obj.fileName == correspondence.templatename)?.templateName
    if (correspondence.category === "response") return "Applicant Response"
    if (correspondence?.sentby == "System Generated Email" && 
      (correspondence?.text.includes("as you have additional options outside of paying the fee") || 
      correspondence?.text.includes("has received your payment for FOI request"))) return "Fee Estimate / Outstanding Fee"
    return `Your FOI Request ${requestNumber}`
    // if(correspondence.templatename) {
    //   return correspondence.templatename;
    // } else {
    //   return applicantCorrespondenceTemplates.find((obj)=> obj.templateid == correspondence.templateId)?.description
    // }
  }

  const DeleteAction = () => {
    return (
        <Dialog
          open={deletePopoverOpen}
          onClose={handleDialogClose}
          aria-label="Delete"
          aria-description="Delete"
          maxWidth={'md'}
          fullWidth={true}
        >
                          <div id="deletemodal" onBlur={closeTooltip} className='modal deletemodal' style={modal}>
                            <div className='actions' style={modalActions}>
                                <button
                                  className='button'
                                  style={modalActionBtn}

                                  disabled
                                >
                                  Delete
                                </button>
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

const getFullEmailListText = () => {
  let fullEmailListText = correspondence?.emails?.length > 0 ? 'Email To: ' : '';
  correspondence?.emails.forEach((email, index) => {
    fullEmailListText = fullEmailListText + email
    if (index < correspondence.emails.length - 1) fullEmailListText = fullEmailListText + ', '
  })
  return fullEmailListText;
}
const fullEmailListText = getFullEmailListText();
const getFullCCEmailListText = () => {
  let fullCCEmailListText = correspondence?.ccemails?.length > 0 ? 'CC To: ' : '';
  correspondence?.ccemails.forEach((email, index) => {
    fullCCEmailListText = fullCCEmailListText + email
    if (index < correspondence.ccemails.length - 1) fullCCEmailListText = fullCCEmailListText + ', '
  })
  return fullCCEmailListText;
}
const fullCCEmailListText = getFullCCEmailListText();
let popoverEmailList = fullEmailListText + '\n' + fullCCEmailListText;
const totalNumberOfEmails = correspondence?.emails?.length + correspondence?.ccemails?.length
let emailText = '';
if (correspondence?.emails?.length > 0) {
  emailText = correspondence.emails[0];
} else if (correspondence?.ccemails?.length > 0) {
  emailText = correspondence.ccemails[0]
}
if (totalNumberOfEmails > 1) emailText = emailText + ` +${totalNumberOfEmails - 1}`
  return (
    <>
      <div className="communication-accordion" {...(correspondence ? {"data-communication-div-id":`${currentIndex}`} : {})}>
        <Accordion>
          <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            aria-controls="communication-accordion-summary"
            id={`communication-accordion-${currentIndex}`}
          >
              <div className="templateList">
                <div>
                  <div className="templateInfo">
                    {correspondence && (
                      <>
                      <div className="templateUser">{getTemplateName(correspondence)} - {fullName} </div> |  
                        {totalNumberOfEmails > 1 ? <><div className="templateUser"><Tooltip title={<span style={{ whiteSpace: 'pre-line' }}>{popoverEmailList}</span>} disableInteractive placement="top">{emailText}</Tooltip></div> |</>: totalNumberOfEmails == 1 ? <><div className="templateUser"> {emailText} </div>|</> : ''} 
                        <div className="templateTime">{correspondence?.date?.toUpperCase()} </div>
                        <div className="templateTime">{correspondence.edited ? "Edited": ""} </div>
                      </>
                    )
                    }
                    {!correspondence && (
                      <>
                    <div className="templateInfo">{fullName} </div> |  <div className="templateTime">{correspondence.date} </div>  <div className="templateTime">{correspondence.edited ? "Edited": ""} </div>
                    </>
                    )
                    }
                    {correspondence. category != 'response' && <div className="templateUser">{correspondence.category !== "draft" && <ClickableChip clicked={true} color={'primary'} label={correspondence.sentby ? 'emailed' : 'printed'} size="small" />}</div>}
                    </div>
                </div>
              </div>
              <div className="userActions">
                <div>
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
                </div>
              </div>
          </AccordionSummary>
          <AccordionDetails>
            <div className="commenttext" dangerouslySetInnerHTML={{ __html: getHtmlfromRawContent() }} >
            </div>
            {correspondence && correspondence.attachments?.map((attachment, index) => (
            <div className="email-attachment-item" key={attachment.applicantcorrespondenceattachmentid + attachment.filename}>
              <a href={`/foidocument?id=${ministryId}&filepath=${attachment.documenturipath.split('/').slice(4).join('/')}`} target="_blank">{attachment.filename}</a>
              <IconButton
                aria-label= "actions"
                id={`ellipse-icon-${currentIndex}`}
                key={`ellipse-icon-${currentIndex}`}
                // color="inherit"
                className="attachment-actions"
                onClick={(e) => {
                    e.stopPropagation();
                    setAttachmentPopoverOpen(true)
                    setUpdateAttachment(correspondence.attachments[index]);
                    setSelectedCorrespondence(correspondence);
                    setAttachmentDownloadLink(`/foidocument?id=${ministryId}&filepath=${attachment.documenturipath.split('/').slice(4).join('/')}`)
                    setAttachmentAnchorPosition(
                      e.currentTarget.getBoundingClientRect()
                      );
                }}
              >
                <MoreHorizIcon />
              </IconButton>
              <AttachmentActionsPopover />
            </div>
            ))}
          </AccordionDetails>
        </Accordion>
      </div>
    </>
  )
}

export default CommunicationStructure;