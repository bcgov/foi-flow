import React, { useEffect, useState } from 'react'
import './attachments.scss'
import Popup from 'reactjs-popup'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faEllipsisH } from '@fortawesome/free-solid-svg-icons'
import { useDispatch } from "react-redux";
import AttachmentModal from './AttachmentModal';
import { getOSSHeaderDetails, saveFilesinS3 } from "../../../../apiManager/services/FOI/foiRequestServices";

export const AttachmentSection = ({
  requestNumber,
  attachmentsArray,
  currentUser,
  setComment,
  requestid,
  ministryId,
  bcgovcode
}) => {
  // const [attachments, setAttachments] = useState(attachmentsArray)
  
  // useEffect(() => {
  //   setAttachments(attachmentsArray)
  // }, [attachmentsArray])
  
  const attachments = [
    {
      documentpath: "Username1",
      filename: "Fee Estimate Letter Sent",
      category: "cfrtofee",
      created_at: "2021-11-01",
      createdby: "richard@idir"
    },
    {
      documentpath: "Fees Form Complete",
      filename: "Fees Form Complete",
      category: "",
      created_at: "2021-11-02",
      createdby: "abin@idir"
    },
    {
      documentpath: "Call Clarification",
      filename: "Call Clarification",
      category: "",
      created_at: "2021-11-03",
      createdby: "foimma@idir"
    },
    {
      documentpath: "Call Sent to EDUC",
      filename: "Call Sent to EDUC",
      category: "",
      created_at: "2021-11-05",
      createdby: "foiedu@idir"
    },
  ];

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
        console.log(documents);
        // saveStatusId();
        // saveMinistryRequestObject.documents = documents;
        // saveMinistryRequest();
        // hasStatusRequestSaved(true,currentSelectedStatus);
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
                <b>{attachment.filename}</b>
              </div>
            </div>
            <div className="col-lg-7" style={{display:'inline-block'}}>
              <div className="col-lg-1" style={{marginLeft:'auto'}}>
                <button className="actionsBtn">
                  <FontAwesomeIcon icon={faEllipsisH} size='1x' color='darkblue' />
                </button>
              </div>                      
            </div>
          </div>
        </div>
        <div className="row foi-details-row" style={{paddingTop:15+'px'}}>
          <div className="col-lg-12 foi-details-col">                      
            {attachment.created_at}
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

export default AttachmentSection