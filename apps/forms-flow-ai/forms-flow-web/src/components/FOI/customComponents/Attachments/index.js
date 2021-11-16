import React, { useEffect, useState } from 'react'
import './attachments.scss'
import Popup from 'reactjs-popup'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faEllipsisH } from '@fortawesome/free-solid-svg-icons'
import { formatDate } from "../../../../helper/FOI/helper";

export const AttachmentSection = ({
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

  var attachmentsList = [];
  for(var i=0; i<attachments.length; i++) {
    attachmentsList.push(<Attachment key={i} attachment={attachments[i]} />);
  }

  return (
    <div>
      <div className="section">
        <div className="addAttachmentBox">
            <button type="button" className="btn foi-btn-create addAttachment" onClick={()=>{ alert("hello W"); }}>+ Add Attachment</button>
        </div>
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
                <AttachmentPopup attachment={attachment} />
              </div>                      
            </div>
          </div>
        </div>
        <div className="row foi-details-row" style={{paddingTop:15+'px'}}>
          <div className="col-lg-12 foi-details-col">                      
            {formatDate(attachment.created_at, 'yyyy MMM dd | HH:mm')}
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