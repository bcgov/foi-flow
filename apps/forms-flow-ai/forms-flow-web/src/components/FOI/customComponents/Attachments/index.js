import React, { useEffect, useState } from 'react'
import './attachments.scss'
import Popup from 'reactjs-popup'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faEllipsisH } from '@fortawesome/free-solid-svg-icons'
import { useDispatch } from "react-redux";
import AttachmentModal from './AttachmentModal';
import Loading from "../../../../containers/Loading";
import { getOSSHeaderDetails, saveFilesinS3, saveFOIRequestAttachmentsList, replaceFOIRequestAttachment } from "../../../../apiManager/services/FOI/foiRequestServices";
import { StateTransitionCategories } from '../../../../constants/FOI/statusEnum'

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
  const [openRenameModal, setRenameModal] = useState(false);
  const [currentAttachment, setCurrentAttachment] = useState();
  const [multipleFiles, setMultipleFiles] = useState(true);
  const [modalFor, setModalFor] = useState("add");
  const [updateAttachment, setUpdateAttachment] = useState({});

  const addAttachments = () => {
    setModal(true);
  }

  React.useEffect(() => {    
    if (successCount === fileCount && successCount !== 0) {
        setModal(false);
        const documentsObject = {documents: documents};
        if (modalFor === 'replace' && updateAttachment) {
          const replaceDocumentObject = {filename: documents[0].filename, documentpath: documents[0].documentpath};          
          dispatch(replaceFOIRequestAttachment(requestId, ministryId, updateAttachment.foiministrydocumentid, replaceDocumentObject,(err, res) => {
            if (!err) {
              setAttachmentLoading(false);
            }
          }));
        }
        else {
        dispatch(saveFOIRequestAttachmentsList(requestId, ministryId, documentsObject,(err, res) => {
          if (!err) {
            setAttachmentLoading(false);
          }
        }));
      }
    }
  },[successCount])

  const handleContinueModal = (value, fileInfoList, files) => {
    setModal(false);
    if (files) {
    setFileCount(files.length);
    if (value) {
        if (files.length !== 0) {
          setAttachmentLoading(true);
          dispatch(getOSSHeaderDetails(fileInfoList, (err, res) => {         
            let _documents = [];
            if (!err) {
              res.map((header, index) => {
                const _file = files.find(file => file.name === header.filename);
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

  const handleReplace = (_attachment) => {
    setModal(true);
    setMultipleFiles(false);
    setUpdateAttachment(_attachment);
    setModalFor('replace');
  }

  const handleRename = (_attachment) => {
    setModal(true);
    setUpdateAttachment(_attachment);
    setModalFor('replace');
    
    if (currentAttachment.filename !== newFilename) {
      dispatch(saveNewFilename(newFilename, documentId, requestId, ministryId, (err, res) => {
        if (res === 200) {
          setSuccessCount(index+1);
        }
        else {
          setSuccessCount(0);
        }
      }));
    }
  }

  var attachmentsList = [];
  for(var i=0; i<attachments.length; i++) {
    attachmentsList.push(<Attachment key={i} attachment={attachments[i]} iaoassignedToList={iaoList} ministryAssignedToList={ministryList} handleReplace={handleReplace} />);
  }
  console.log(updateAttachment);
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
        <AttachmentModal openModal={openModal} handleModal={handleContinueModal} multipleFiles={true} requestNumber={requestNumber} requestId={requestId} />
        <RenameModal openModal={openRenameModal} handleModal={handleRenameModal} requestNumber={requestNumber} requestId={requestId} />
        <AttachmentModal modalFor={modalFor} openModal={openModal} handleModal={handleContinueModal} multipleFiles={multipleFiles} requestNumber={requestNumber} requestId={requestId} attachment={updateAttachment} />
        <div className="displayAttachments">
          {attachmentsList}
        </div>
      </div>
      }
    </div>
  )
}


const Attachment = React.memo(({attachment, iaoassignedToList, ministryAssignedToList, handleReplace}) => {

  const getfullName = (userId) => {
    let user;

    if(iaoassignedToList.length > 0) {
      iaoassignedToList.forEach(function (obj) {
        var groupmembers = obj.members
        var iao_user = groupmembers.find(m => m["username"] === userId)
        if (iao_user && iao_user != undefined) {
          user = iao_user;
        }
      })
  
      if(user && user != undefined) {
        if(user["lastname"] && user["firstname"]) {
          return `${user["lastname"]}, ${user["firstname"]}`;
        } else {
          return userId;
        }
      }
    }

    if(ministryAssignedToList.length > 0 && !user) {
      ministryAssignedToList.forEach(function (obj) {
        var groupmembers = obj.members
        var ministry_user = groupmembers.find(m => m["username"] === userId)
        if (ministry_user && ministry_user != undefined) {
          user = ministry_user;
        }
      })

      if(user && user != undefined) {
        if(user["lastname"] && user["firstname"]) {
          return `${user["lastname"]}, ${user["firstname"]}`;
        } else {
          return userId;
        }
      }
    }
      
    return userId;
  }

  const handleReplaceClick = (attachment) => {
    handleReplace(attachment);
  }

  return (
    <div className="container-fluid">
      <div className="row foi-details-row">
        <div className="row foi-details-row">
          <div className="col-sm-12 foi-details-col">
            <div className="col-sm-10" style={{display:'inline-block',paddingLeft:'0px'}}>
              <div className="attachment-name">                      
                {attachment && attachment.filename ? attachment.filename.split('.').shift() : ""}
              </div>
            </div>
            <div className="col-sm-2" style={{display:'inline-block'}}>
              <div className="col-sm-1" style={{marginLeft:'auto'}}>
                <AttachmentPopup attachment={attachment} handleReplaceClick={handleReplaceClick}/>
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
            {getfullName(attachment.createdby)}
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

const AttachmentPopup = React.memo(({attachment, handleReplaceClick}) => {

  const handleReplaceButtonClick = () => {
    handleReplaceClick(attachment);
  }
  return (
    <Popup
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
        <button className="childActionsBtn" onClick={rename(attachment)}>
          Rename
        </button>
        {(attachment.category==="statetransition" || attachment.category===StateTransitionCategories.cfrreview.name || attachment.category===StateTransitionCategories.cfrfeeassessed.name || attachment.category===StateTransitionCategories.signoffresponse.name || attachment.category===StateTransitionCategories.harmsreview.name )?
          <button className="childActionsBtn" onClick={handleReplaceButtonClick}>
            Replace
          </button>
          :
          <button className="childActionsBtn">
            Delete
          </button>
        }
      </div>
    </Popup>
  );
})

export default AttachmentSection