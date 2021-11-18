import React, { useEffect, useState } from 'react'
import './attachments.scss'
import Popup from 'reactjs-popup'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faEllipsisH } from '@fortawesome/free-solid-svg-icons'
import { useDispatch } from "react-redux";
import AttachmentModal from './AttachmentModal';
import { getOSSHeaderDetails, saveFilesinS3, saveFOIRequestAttachmentsList } from "../../../../apiManager/services/FOI/foiRequestServices";
import { formatDate } from "../../../../helper/FOI/helper";

export const AttachmentSection = ({
  requestNumber,
  attachmentsArray,
  currentUser,
  setAttachment,
  requestId,
  ministryId,
  bcgovcode
}) => {
  const [attachments, setAttachments] = useState(attachmentsArray)
  
  useEffect(() => {
    setAttachments(attachmentsArray);
    console.log(attachmentsArray);
  }, [attachmentsArray])
  

  const [openModal, setModal] = useState(false);
  const [successCount, setSuccessCount] = useState(0);
  const [fileCount, setFileCount] = useState(0);
  const dispatch = useDispatch();
  const [documents, setDocuments] = useState([]);
  const addAttachments = () => {
    setModal(true);
  }
  React.useEffect(() => {
    if (successCount === fileCount && successCount !== 0) {
        setModal(false);
        const documentsObject = {documents: documents};
        dispatch(saveFOIRequestAttachmentsList(requestId, ministryId,documentsObject));        
    }
  },[successCount])

  const handleContinueModal = (value, fileInfoList, files) => {
    setModal(false);
    setFileCount(files.length);
    if (value) {
        if (files.length !== 0) {
          dispatch(getOSSHeaderDetails(fileInfoList, (err, res) => {         
            let _documents = [];
            if (!err) {
              res.map((header, index) => {
                const _file = files.find(file => file.name === header.filename);
                const documentDetails = {documentpath: header.filepath, filename: header.filename, category: 'attachmentlog'};
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

  var attachmentsList = [];
  for(var i=0; i<attachments.length; i++) {
    attachmentsList.push(<Attachment key={i} attachment={attachments[i]} />);
  }

  return (
    <div>
      <div className="section">
        <div className="addAttachmentBox">
            <button type="button" className="btn foi-btn-create addAttachment" onClick={addAttachments}>+ Add Attachment</button>
        </div>
        <AttachmentModal openModal={openModal} handleModal={handleContinueModal} multipleFiles={true} requestNumber={requestNumber} />
        <div className="displayAttachments">
          {attachmentsList}
        </div>
      </div>
    </div>
  )
}


const Attachment = React.memo(({attachment}) => {

  return (
    <div className="container-fluid">
      <div className="row foi-details-row">
        <div className="row foi-details-row">
          <div className="col-lg-12 foi-details-col">
            <div className="col-lg-5" style={{display:'inline-block',paddingLeft:'0px'}}>
              <div style={{display:'inline',paddingRight:15+'px'}}>                      
                <b>{attachment.filename.split('.').shift()}</b>
              </div>
            </div>
            <div className="col-lg-7" style={{display:'inline-block'}}>
              <div className="col-lg-1" style={{marginLeft:'auto'}}>
                <AttachmentPopup attachment={attachment} />
              </div>                      
            </div>
          </div>
        </div>
        <div className="row foi-details-row" style={{paddingTop:15+'px'}}>
          <div className="col-lg-12 foi-details-col">                      
            {formatDate(attachment.created_at, 'yyyy MMM dd | p')}
          </div>
        </div>
        <div className="row foi-details-row" style={{paddingBottom:15+'px'}}>
          <div className="col-lg-12 foi-details-col">                      
            {attachment.createdby}
          </div>
        </div>
        <div className="row foi-details-row" style={{paddingBottom:15+'px'}}>
          <div className="col-lg-12 foi-details-col">                      
            <hr className="solid" />
          </div>
        </div>
      </div>
    </div>
  );
})

const AttachmentPopup = React.memo(({attachment}) => {

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
        <button className="childActionsBtn">
          Rename
        </button>
        {attachment.category?
          <button className="childActionsBtn">
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