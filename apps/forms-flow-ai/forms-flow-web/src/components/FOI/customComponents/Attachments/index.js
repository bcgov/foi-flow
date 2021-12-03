import React, { useEffect, useState } from 'react'
import './attachments.scss'
import Popup from 'reactjs-popup'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faEllipsisH } from '@fortawesome/free-solid-svg-icons'
import { useDispatch } from "react-redux";
import AttachmentModal from './AttachmentModal';
import Loading from "../../../../containers/Loading";
import { getOSSHeaderDetails, saveFilesinS3, saveFOIRequestAttachmentsList, replaceFOIRequestAttachment, saveNewFilename, deleteFOIRequestAttachment } from "../../../../apiManager/services/FOI/foiRequestServices";
import { StateTransitionCategories } from '../../../../constants/FOI/statusEnum'
import { addToFullnameList, getFullnameList } from '../../../../helper/FOI/helper'

export const AttachmentSection = ({
  requestNumber,
  requestState,
  attachmentsArray,
  currentUser,
  setAttachment,
  requestId,
  ministryId,
  bcgovcode,
  iaoassignedToList,
  ministryAssignedToList
}) => {
  const [attachments, setAttachments] = useState(attachmentsArray)
  const [iaoList, setIaoList] = useState(iaoassignedToList)
  const [ministryList, setMinistryList] = useState(ministryAssignedToList)
  
  useEffect(() => {
    setAttachments(attachmentsArray);
    setIaoList(iaoassignedToList);
    setMinistryList(ministryAssignedToList);
  }, [attachmentsArray, iaoassignedToList, ministryAssignedToList])
  

  const [openModal, setModal] = useState(false);
  const [successCount, setSuccessCount] = useState(0);
  const [fileCount, setFileCount] = useState(0);
  const dispatch = useDispatch();
  const [documents, setDocuments] = useState([]);
  const [isAttachmentLoading, setAttachmentLoading] = useState(false);
  const [multipleFiles, setMultipleFiles] = useState(true);
  const [modalFor, setModalFor] = useState("add");
  const [updateAttachment, setUpdateAttachment] = useState({});
  const [fullnameList, setFullnameList] = useState(getFullnameList);

  const addAttachments = () => {
    setModalFor('add');
    setMultipleFiles(true);
    setUpdateAttachment({});
    setModal(true);
  }

  React.useEffect(() => {    
    if (successCount === fileCount && successCount !== 0) {
        setModal(false);
        const documentsObject = {documents: documents};
        if (modalFor === 'replace' && updateAttachment) {
          const replaceDocumentObject = {filename: documents[0].filename, documentpath: documents[0].documentpath};
          const documentId = ministryId ? updateAttachment.foiministrydocumentid : updateAttachment.foidocumentid;      
          dispatch(replaceFOIRequestAttachment(requestId, ministryId, documentId, replaceDocumentObject,(err, res) => {
            if (!err) {
              setAttachmentLoading(false);
              setSuccessCount(0);
            }
          }));
        }
        else {
          dispatch(saveFOIRequestAttachmentsList(requestId, ministryId, documentsObject,(err, res) => {
          if (!err) {
            setAttachmentLoading(false);
            setSuccessCount(0);
          }
        }));
      }
    }
  },[successCount])

  const handleContinueModal = (value, fileInfoList, files) => {
    setModal(false);
    if (modalFor === 'delete' && value) { 
      const documentId = ministryId ? updateAttachment.foiministrydocumentid : updateAttachment.foidocumentid;
      dispatch(deleteFOIRequestAttachment(requestId, ministryId, documentId, {}));
    }
    else if (files) {
    setFileCount(files.length);
    if (value) {
        if (files.length !== 0) {
          setAttachmentLoading(true);
          dispatch(getOSSHeaderDetails(fileInfoList, (err, res) => {
            let _documents = [];
            if (!err) {
              res.map((header, index) => {
                const _file = files.find(file => file.filename === header.filename);
                const documentDetails = {documentpath: header.filepath, filename: header.filename, category: 'general'};
                _documents.push(documentDetails);
                setDocuments(_documents);
                dispatch(saveFilesinS3(header, _file, (err, res) => {
                  if (res === 200) {
                    setSuccessCount(index+1);
                  }
                  else {
                    setSuccessCount(0);
                  }
                }));
              });
            }
          }));
        }             
    }
  }
  }

  const handlePopupButtonClick = (action, _attachment) => {
    setUpdateAttachment();
    setUpdateAttachment(_attachment);
    setMultipleFiles(false);
    switch(action) {
      case 'replace':        
        setModalFor('replace');        
        break;
      case 'rename':        
        setModalFor('rename');        
        break;
      case 'delete':        
        setModalFor('delete');        
        break;
      default:
        setModal(false);
        break;
    }
    setModal(true);
  }

  const handleRename = (_attachment, newFilename) => {
    setModal(false);

    if (updateAttachment.filename !== newFilename) {
      const documentId = ministryId ? updateAttachment.foiministrydocumentid : updateAttachment.foidocumentid;
      dispatch(saveNewFilename(newFilename, documentId, requestId, ministryId, (err, res) => {
        if (!err) {
          setAttachmentLoading(false);
        }
      }));
    }
  }

  const getFullname = (userId) => {
    let user;

    if(fullnameList) {
      user = fullnameList.find(u => u.username === userId);
      return user && user.fullname ? user.fullname : userId;
    } else {

      if(iaoassignedToList.length > 0) {
        addToFullnameList(iaoassignedToList, "iao");
        setFullnameList(getFullnameList());
      }
  
      if(ministryAssignedToList.length > 0) {
        addToFullnameList(iaoassignedToList, bcgovcode);
        setFullnameList(getFullnameList());
      }
  
      user = fullnameList.find(u => u.username === userId);
      return user && user.fullname ? user.fullname : userId;
    }
  };

  var attachmentsList = [];
  for(var i=0; i<attachments.length; i++) {
    attachmentsList.push(<Attachment key={i} attachment={attachments[i]} handlePopupButtonClick={handlePopupButtonClick} getFullname={getFullname} />);
  }
  
  return (
    <div>
      { isAttachmentLoading ? <Loading /> : 
      <div className="section">
        <div className="foi-request-number-header">
          <h1 className="foi-review-request-text foi-ministry-requestheadertext">{`Request #${requestNumber ? requestNumber :`U-00${requestId}`}`}</h1>
        </div>
        <div className="addAttachmentBox">
            <button type="button" className="btn foi-btn-create addAttachment" onClick={addAttachments}>+ Add Attachment</button>
        </div>
        <AttachmentModal modalFor={modalFor} openModal={openModal} handleModal={handleContinueModal} multipleFiles={multipleFiles} requestNumber={requestNumber} requestId={requestId} attachment={updateAttachment} attachmentsArray={attachmentsArray} handleRename={handleRename} />
        <div className="displayAttachments">
          {attachmentsList}
        </div>
      </div>
      }
    </div>
  )
}


const Attachment = React.memo(({attachment, handlePopupButtonClick, getFullname}) => {

  const [filename, setFilename] = useState("");
  let lastIndex = 0;
  useEffect(() => {
    if(attachment && attachment.filename) {
      lastIndex = attachment.filename.lastIndexOf(".");
      setFilename(lastIndex>0?attachment.filename.substr(0, lastIndex):attachment.filename);
    }
  }, [attachment])

  const getCategory = (category) => {
    switch(category) {
      case "cfr-review":
        return "cfr - review";
      case "cfr-feeassessed":
        return "cfr - fee estimate";
      case "signoff-response":
        return "signoff - response";
      case "harms-review":
        return "harms assessment - review";
      default:
        return "general";
    }
  }

  return (
    <div className="container-fluid">
      <div className="row foi-details-row">
        <div className="row foi-details-row">
          <div className="col-sm-12 foi-details-col">
            <div className="col-sm-10" style={{display:'inline-block',paddingLeft:'0px'}}>
              <div className="attachment-name">
                {attachment.filename}
              </div>
              <div className="attachment-badge">
                <span class="badge badge-primary">{getCategory(attachment.category)}</span>
              </div>
            </div>
            <div className="col-sm-2" style={{display:'inline-block'}}>
              <div className="col-sm-1" style={{marginLeft:'auto'}}>
                <AttachmentPopup attachment={attachment} handlePopupButtonClick={handlePopupButtonClick}/>
              </div>                      
            </div>
          </div>
        </div>
        <div className="row foi-details-row">
          <div className="col-sm-12 foi-details-col attachment-time">                      
            {attachment.created_at}
          </div>
        </div>
        <div className="row foi-details-row">
          <div className="col-sm-12 foi-details-col attachment-owner">                      
            {getFullname(attachment.createdby)}
          </div>
        </div>
        <div className="row foi-details-row">
          <div className="col-sm-12 foi-details-col">                      
            <hr className="solid" />
          </div>
        </div>
      </div>
    </div>
  );
})

const AttachmentPopup = React.memo(({attachment, handlePopupButtonClick}) => {

  const handleRename = () => {
    handlePopupButtonClick("rename", attachment);
  }

  const handleReplace = () => {
    handlePopupButtonClick("replace", attachment);
  }

  const handleDelete = () => {
    handlePopupButtonClick("delete", attachment);
  }

  return (
    <Popup
      role='tooltip'
      trigger={
        <button className="actionsBtn">
          <FontAwesomeIcon icon={faEllipsisH} size='1x' color='darkblue' />
        </button>
      }
      className="attachment-popup"
      position={'bottom right'}
      closeOnDocumentClick
      // keepTooltipInside=".tooltipBoundary"
    >
      <div>
        <button className="childActionsBtn">
          Download
        </button>
        <button className="childActionsBtn" onClick={handleRename}>
          Rename
        </button>
        {(attachment.category==="statetransition" || attachment.category===StateTransitionCategories.cfrreview.name || attachment.category===StateTransitionCategories.cfrfeeassessed.name || attachment.category===StateTransitionCategories.signoffresponse.name || attachment.category===StateTransitionCategories.harmsreview.name )?
          <button className="childActionsBtn" onClick={handleReplace}>
            Replace
          </button>
          :
          <button className="childActionsBtn" onClick={handleDelete}>
            Delete
          </button>
        }
      </div>
    </Popup>
  );
})

export default AttachmentSection