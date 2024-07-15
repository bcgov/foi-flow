import React, { useContext, useState, useRef, useEffect } from 'react'
import '../Comments/comments.scss'
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
import { getOSSHeaderDetails, getFileFromS3 } from "../../../../apiManager/services/FOI/foiOSSServices";
import { saveAs } from "file-saver";
import { downloadZip } from "client-zip";
import { useDispatch } from "react-redux";
import * as html2pdf from 'html-to-pdf-js';
import CommunicationUploadModal from '../Comments/CommunicationUploadModal';
import { Chip } from '@material-ui/core'


const CommunicationStructure = ({correspondence, currentIndex,
  fullName, ministryId=null, editDraft, deleteDraft, deleteResponse, setModalFor,setModal,setUpdateAttachment, 
  setSelectedCorrespondence, setCurrentResponseDate, applicantCorrespondenceTemplates}) => {


  const dispatch = useDispatch();
  const [popoverOpen, setPopoverOpen] = useState(false);
  const [communicationUploadModalOpen, setCommunicationUploadModalOpen] = useState(false);
  const [anchorPosition, setAnchorPosition] = useState(null);
  const [deletePopoverOpen, setDeletePopoverOpen] = useState(false);
  //console.log("I:",correspondence)
  const ref = useRef();
  const closeTooltip = () => ref.current && ref ? ref.current.close() : {};


  const getHtmlfromRawContent = () => {
    let markup = null
    if (correspondence.commentTypeId === 1) {
      const rawContentFromStore = convertFromRaw(JSON.parse(correspondence.text))
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
      if (correspondence.text) {
        markup = `<p>${correspondence.text}</p>`
      } else {
        markup = `<p></p>`
      }
      
    }
    return markup
  }

  const ActionsPopover = () => {

    const renderDownloadMenuItem = () => (
      <MenuItem
        onClick={(e) => {
          e.stopPropagation();
          download();
          setPopoverOpen(false);
        }}
      >
        Download
      </MenuItem>
    );
  
    const renderDraftMenuItems = () => (
      <>
        <MenuItem onClick={() => {
          editDraft(correspondence)
          setPopoverOpen(false);
        }}>Edit</MenuItem>
        <MenuItem onClick={() => {
          deleteDraft(correspondence)
          setPopoverOpen(false);
          }}>Delete</MenuItem>
        {renderDownloadMenuItem()}
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
          onClick={() => {
            setUpdateAttachment(correspondence.attachments[0]);
            setModalFor("rename");
            setModal(true);
            setSelectedCorrespondence(correspondence);
            setPopoverOpen(false);
          }}
        >
          Rename
        </MenuItem>
        {renderDownloadMenuItem()}
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
              {correspondence.category === "correspondence" && renderDownloadMenuItem()}
              {correspondence.category === "draft" && renderDraftMenuItems()}
              {correspondence.category === "response" && renderResponseMenuItems()}
            </MenuList>
          )}
        </Popover>
        <DeleteAction />
        <CommunicationUploadModal 
          openModal={communicationUploadModalOpen} 
          setOpenModal={setCommunicationUploadModalOpen}
          message={{ body: "", title: "Add Response" }}
          ministryId={ministryId}
        />
      </div>
    );
  };

  const handleDialogClose = () => {
    closeTooltip()
    setDeletePopoverOpen(false);
  }

  const download = async () => {
    const elementToClickForExpand = document.querySelector(`#communication-accordion-${currentIndex}`);
    let isAriaExpanded = elementToClickForExpand.ariaExpanded
    if (isAriaExpanded == 'false') elementToClickForExpand.click();
    let fileInfoList = correspondence.attachments.map(attachment => {
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
    const element = document.querySelector(`[data-communication-div-id="${currentIndex}"]`);
    html2pdf().from(element).outputPdf('blob').then(async (blob) => {
      blobs.push({name: "Email Body.pdf", lastModified: new Date(), input: blob})
      const zipfile = await downloadZip(blobs).blob()
      saveAs(zipfile, fullName + " " + correspondence.date.replace("|", "") + ".zip");
    });
  }


  const getTemplateName = (templateId) => {
    return applicantCorrespondenceTemplates.find((obj)=> obj.templateid == templateId)?.description
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


  return (
    <>
      <div className="comment-accordion" {...(correspondence ? {"data-communication-div-id":`${currentIndex}`} : {})}>
        <Accordion>
          <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            aria-controls="communication-accordion-summary"
            id={`communication-accordion-${currentIndex}`}
          >
              <div className="halfDiv">
                <div className="userInfo">
                  <div className="commentsTwo">
                    {correspondence && (
                      <>
                      <div className="fullName">{correspondence.category === "response" ? "Applicant Response": getTemplateName(correspondence.templateid)} - {fullName} </div> |  
                        <div className="commentdate">{correspondence.date} </div>  
                        <div className="commentdate">{correspondence.edited ? "Edited": ""} </div>
                      </>
                    )
                    }
                    {!correspondence && (
                      <>
                    <div className="fullName">{fullName} </div> |  <div className="commentdate">{correspondence.date} </div>  <div className="commentdate">{correspondence.edited ? "Edited": ""} </div>
                    </>
                    )
                    }
                    <Chip label={correspondence.sentby ? 'emailed' : 'exported'} variant="outlined" />
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
            {correspondence && correspondence.attachments?.map((attachment) => (
            <div className="email-attachment-item" key={attachment.filename}>
              <a href={`/foidocument?id=${ministryId}&filepath=${attachment.documenturipath.split('/').slice(4).join('/')}`} target="_blank">{attachment.filename}</a>
            </div>
            ))}
          </AccordionDetails>
        </Accordion>
      </div>
    </>
  )
}

export default CommunicationStructure