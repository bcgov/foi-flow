import React, { useEffect, useState, useRef  } from 'react'
import './requesthistory.scss'
import { getCommentTypeIdByName, getCommentTypeFromId } from "../../../../helper/FOI/helper";
import RequestFilter from './RequestFilter';
import DisplayHistory from './DisplayHistory'
import { toast } from 'react-toastify';
import RequestHistoryExportModal from './RequestHistoryExportModel/RequestHistoryExportModal';
import ExportHistory from './ExportHistory';
import * as html2pdf from 'html-to-pdf-js';
import { useDispatch } from "react-redux";
import { saveRequestHistoryComment } from '../../../../apiManager/services/FOI/foiRequestNoteServices';

export const RequestHistorySection = ({
  requestHistoryArray,
  currentUser,
  bcgovcode,
  requestid,
  iaoassignedToList,
  ministryAssignedToList,
  requestNumber,
  commentTypes,
  ministryId,
  applicantCorrespondenceTemplates,
  setComment
}) => {

  const dispatch = useDispatch();
  const [requesthistory, sethistory] = useState([])
  const [exportHistory, setExportHistory] = useState([])
  const [selectedType, setSelectedType] = useState()
  const [filterkeyValue, setfilterkeyValue] = useState("")
  const [showHistoryExportModal, setShowHistoryExportModal] = useState(false);
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);
  
  const getTemplateName = (templateId) =>
    applicantCorrespondenceTemplates.find((obj) => obj.templateid === templateId)?.description;
  
  useEffect(() => {
    const _historybyCategory = filterHistory(); 
    
    const _filteredHistory = filterkeyValue
      ? _historybyCategory.filter((c) => {
          const textMatches = c.text?.toLowerCase().includes(filterkeyValue.toLowerCase());
          const typeMatches = getCommentTypeFromId(commentTypes, c.commentTypeId)
            ?.toLowerCase()
            .includes(filterkeyValue.toLowerCase());
          
          const templateName = c.type === 'message' ? getTemplateName(c.templateid) : null;
          const templateMatches = templateName
            ?.toLowerCase()
            .includes(filterkeyValue.toLowerCase());
  
          const responseMatches = c.category === 'response' &&
            "applicant response".includes(filterkeyValue.toLowerCase());
  
          return textMatches || typeMatches || templateMatches || responseMatches;
        })
      : _historybyCategory;
  
    const filteredhistory = filterkeyinCommentsandReplies(_historybyCategory, _filteredHistory);
    sethistory(filteredhistory);
    setExportHistory(requestHistoryArray)
  }, [requestHistoryArray, filterkeyValue]);
  
  const filterHistory = () => {
    return requestHistoryArray.filter(c => c.commentTypeId !== getCommentTypeIdByName(commentTypes,"Ministry Internal") && 
      c.commentTypeId !== getCommentTypeIdByName(commentTypes, "Ministry Peer Review"))
  };

  const filterkeyinCommentsandReplies = (_comments,filtercomments)=>{
      _comments.forEach(_comment=>{
            if(_comment.replies!=undefined && _comment.replies.length > 0 )
            {
                        let _filteredreply = _comment.replies.filter(c => c.text.toLowerCase().indexOf(filterkeyValue.toLowerCase()) > -1)
                        let _parentcomments = filtercomments.filter(fp => fp.commentId == _comment.commentId)

                        if(_filteredreply!=undefined && _filteredreply.length > 0 && _parentcomments.length === 0)
                        {
                          filtercomments.push(_comment)
                        }
                }
          });

    return filtercomments;
  }

  const getRequestNumber = ()=>{
    let requestHeaderString = 'Request #'
    if(requestNumber)
      {
        return requestHeaderString+requestNumber
      }else
      {
        return requestHeaderString+`U-00${requestid}`
      }  
  }

  const exportRequestHistory = async () =>{
    setShowHistoryExportModal(true);
  }
  const exportSelectedHistory = async (exportOptions) => {
    setExportHistory(await filterExportHistory(exportOptions));
    const toastID = toast.loading("Downloading file")
    toast.update(toastID, {
      render: "Downloading file",
      isLoading: true,
      autoClose: 3000,
    })
    let selectedCategory;
    if(exportOptions.isApplicantCorrespondenceChecked && exportOptions.isCommentsChecked){
      selectedCategory = 'All';
    } else if (exportOptions.isApplicantCorrespondenceChecked) {
      selectedCategory = 'Correspondence';
    } else if (exportOptions.isCommentsChecked) {
      selectedCategory = 'Comments';
    }
    setSelectedType(selectedCategory)
    await exportToPDF(selectedCategory)
    toast.update(toastID, {
      render: "File Downloaded",
      isLoading: false,
      autoClose: 3000,
    })
  }
  const filterExportHistory = (exportOptions) => {
    return requestHistoryArray.filter(c => (exportOptions.isApplicantCorrespondenceChecked && c.type === 'message') ||
    (exportOptions.isCommentsChecked && c.type === 'comment') )
  };

  const exportToPDF = async (selectedCategory) => {
    setIsGeneratingPDF(true)
    const element =  document.getElementById("exportHistory");
    // Options for html2pdf
    const options = {
      margin: 0.5,
      filename: `Request History ${requestid} - ${selectedCategory}.pdf`,
      image: { type: 'png', quality: 0.97 },
      html2canvas: { scale: 2 },
      jsPDF: { unit: 'in', format: 'a4', orientation: 'portrait', compress:true },
    };
    
    setIsGeneratingPDF(false)
  // Create and save the PDF
    await html2pdf().from(element).set(options).save().then(()=>{
      //create system generated comment
      const res = dispatch(saveRequestHistoryComment({ "requestid": requestid, 
        "comment": currentUser.name+" exported request history for "+selectedCategory+".", 
        "ministryrequestid": ministryId }));
      // This set comment refreshes comments and request history section
      setComment(res)
    });
  };
  return (
    <>
      <RequestHistoryExportModal
        exportSelectedHistory={exportSelectedHistory}
        showModal={showHistoryExportModal}
        closeModal={() => setShowHistoryExportModal(false)}
      />
      <div className="section">
        <div className="foi-request-review-header-row1">
          <div className="col-9 foi-request-number-header">
            <h1 className="foi-review-request-text foi-ministry-requestheadertext">{getRequestNumber()}</h1>
          </div>
          <div className="col-2 addcommentBox">
            <button type="button" style={{ display: 'block' }} className="btn foi-btn-create addcomment" onClick={exportRequestHistory}>Export All</button>
          </div>
        </div>
        <div className="displayComments">
          <div className="filterComments" >
            <RequestFilter oncommentfilterkeychange={(k)=>{setfilterkeyValue(k)}} />
          </div>
          <DisplayHistory requesthistory={requesthistory} bcgovcode={bcgovcode} currentUser={currentUser}
            iaoassignedToList={iaoassignedToList} ministryAssignedToList={ministryAssignedToList} 
            commentTypes={commentTypes} ministryId={ministryId} applicantCorrespondenceTemplates={applicantCorrespondenceTemplates}
          />
        </div>
        {isGeneratingPDF ? 
          <div id="exportHistory" className='exportHistory'>
            <div className="export_title">
              <h1 className="foi-review-request-text foi-ministry-requestheadertext">Request History - {selectedType}</h1>
            </div>
            <ExportHistory requesthistory={exportHistory} bcgovcode={bcgovcode} currentUser={currentUser}
                iaoassignedToList={iaoassignedToList} ministryAssignedToList={ministryAssignedToList} 
                commentTypes={commentTypes} ministryId={ministryId} applicantCorrespondenceTemplates={applicantCorrespondenceTemplates}
              />
          </div>: null}
      </div>
    </>
  )
}

export default RequestHistorySection;
