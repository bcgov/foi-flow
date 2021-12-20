import React, { useEffect, useState } from 'react'
import './attachments.scss'
import Popup from 'reactjs-popup'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faEllipsisH } from '@fortawesome/free-solid-svg-icons'
import { useDispatch } from "react-redux";
import AttachmentModal from './AttachmentModal';
import Loading from "../../../../containers/Loading";
import { getOSSHeaderDetails, saveFilesinS3, getFileFromS3 } from "../../../../apiManager/services/FOI/foiOSSServices";
import { saveFOIRequestAttachmentsList, replaceFOIRequestAttachment, saveNewFilename, deleteFOIRequestAttachment } from "../../../../apiManager/services/FOI/foiAttachmentServices";
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
  ministryAssignedToList,
  isMinistryCoordinator
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

  const downloadDocument = (file) => {
    const fileInfoList = [
      {
        ministrycode: "Misc",
        requestnumber: `U-00${requestId}`,
        filestatustransition: file.category,
        filename: file.filename,
        s3sourceuri: file.documentpath
      },
    ];
    dispatch(
      getOSSHeaderDetails(fileInfoList, (err, res) => {
        if (!err) {
          res.map((header, index) => {
            dispatch(
              getFileFromS3(header, file, (err, res) => {
              })
            );
          });
        }
      }));
  }

  const handlePopupButtonClick = (action, _attachment) => {
    setUpdateAttachment(_attachment);
    setMultipleFiles(false);
    switch (action) {
      case "replace":
        setModalFor("replace");
        setModal(true);
        break;
      case "rename":
        setModalFor("rename");
        setModal(true);
        break;
      case "download":
        downloadDocument(_attachment);
        setModalFor("download");
        setModal(false);
        break;
      case "delete":
        setModalFor("delete")
        setModal(true)
        break;
      default:
        setModal(false);
        break;
    }
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
    attachmentsList.push(<Attachment key={i} attachment={attachments[i]} handlePopupButtonClick={handlePopupButtonClick} getFullname={getFullname} isMinistryCoordinator={isMinistryCoordinator} />);
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


const Attachment = React.memo(({attachment, handlePopupButtonClick, getFullname, isMinistryCoordinator}) => {

  const [filename, setFilename] = useState("");
  const [disabled, setDisabled] = useState(isMinistryCoordinator && attachment.category == 'personal');
  let lastIndex = 0;
  useEffect(() => {
    if(attachment && attachment.filename) {
      lastIndex = attachment.filename.lastIndexOf(".");
      setFilename(lastIndex>0?attachment.filename.substr(0, lastIndex):attachment.filename);
      setDisabled(isMinistryCoordinator && attachment.category == 'personal')
    }
  }, [attachment])

  const getCategory = (category) => {
    switch(category) {
      case "cfr-review":
        return "cfr - review";
      case "cfr-feeassessed":
        return "cfr - fee estimate";
      case "signoff-response":
        return "signoff > response";
      case "harms-review":
        return "harms assessment - review";
      case "personal":
        return "personal";
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
              <div className={`attachment-name ${disabled? "attachment-disabled":""}`}>
                {attachment.filename}
              </div>
              <div className="attachment-badge">
                <span class={`badge ${disabled? "badge-secondary":"badge-primary"}`}>{getCategory(attachment.category)}</span>
              </div>
            </div>
            <div className="col-sm-2" style={{display:'inline-block'}}>
              <div className="col-sm-1" style={{marginLeft:'auto'}}>
                <AttachmentPopup attachment={attachment} handlePopupButtonClick={handlePopupButtonClick} disabled={disabled} />
              </div>                      
            </div>
          </div>
        </div>
        <div className="row foi-details-row">
          <div className={`col-sm-12 foi-details-col attachment-time ${disabled? "attachment-disabled":""}`}>                      
            {attachment.created_at}
          </div>
        </div>
        <div className="row foi-details-row">
          <div className={`col-sm-12 foi-details-col attachment-owner ${disabled? "attachment-disabled":""}`}>                      
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

const AttachmentPopup = React.memo(({attachment, handlePopupButtonClick, disabled}) => {
  const ref = React.useRef();
  const closeTooltip = () => ref.current && ref ? ref.current.close():{};

  const handleRename = () => {
    closeTooltip(); 
    handlePopupButtonClick("rename", attachment);
  }

  const handleReplace = () => {
    closeTooltip(); 
    handlePopupButtonClick("replace", attachment);
  }

  const handleDownload = () =>{
    closeTooltip();   
    handlePopupButtonClick("download", attachment);
  }

  const handleDelete = () => {
    closeTooltip(); 
    handlePopupButtonClick("delete", attachment);
  };

  const transitionStates = [
    "statetransition",
    StateTransitionCategories.cfrreview.name,
    StateTransitionCategories.cfrfeeassessed.name,
    StateTransitionCategories.signoffresponse.name,
    StateTransitionCategories.harmsreview.name
  ];

  const showReplace = (category) => {
    return transitionStates.includes(category.toLowerCase());
  }

  return (
    <Popup
      role='tooltip'
      ref={ref}
      trigger={
        <button className="actionsBtn">
          <FontAwesomeIcon icon={faEllipsisH} size='1x' color='darkblue' />
        </button>
      }
      className="attachment-popup"
      position={'bottom right'}
      closeOnDocumentClick
      disabled={disabled}
      // keepTooltipInside=".tooltipBoundary"
    >
      <div>
        <button className="childActionsBtn" onClick={handleDownload}>
          Download
        </button>
        <button className="childActionsBtn" onClick={handleRename}>
          Rename
        </button>
        {attachment.category === "personal"?"":
          showReplace(attachment.category)?
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