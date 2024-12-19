import { useState } from 'react';
import '../requesthistory.scss';
import 'reactjs-popup/dist/index.css';
import { ClickableChip } from '../../../Dashboard/utils';
import { addToFullnameList, getCommentTypeIdByName, getFullnameList } from '../../../../../helper/FOI/helper';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import CommentHistory from '../CommentHistory';
import _ from "lodash";
import ExportRequestDetailsHistory from './ExportRequestDetails';
import ExportCFRForms from './ExportCFRForms';
import { StateEnum } from '../../../../../constants/FOI/statusEnum';
import FOI_COMPONENT_CONSTANTS from '../../../../../constants/FOI/foiComponentConstants';



const ExportHistory = ({
  bcgovcode,
  currentUser,
  iaoassignedToList,
  ministryAssignedToList,
  commentTypes,
  ministryId,
  applicantCorrespondenceTemplates,
  requestDetails,
  requestState,
  foiRequestCFRFormHistory,
  foiRequestCFRForm,
  applicantCorrespondence,
  requestNotes,
  selectedExportOptions
}) => {

  const [fullnameList, setFullnameList] = useState(getFullnameList);
  let cfrForms = [foiRequestCFRForm]
  foiRequestCFRFormHistory.map((cfrHistory) => {
    if (cfrHistory['cfrfeestatus.description'] === 'Approved') {
      cfrForms.push(cfrHistory);
    }
  })

  const showCFRTab = () => {
    return (
      requestState !== StateEnum.intakeinprogress.name &&
      requestState !== StateEnum.unopened.name &&
      requestState !== StateEnum.open.name &&
      requestDetails?.requestType ===
        FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_GENERAL
    );
  };

  const finduserbyuserid = (userId) => {
    let user = fullnameList.find((u) => u.username === userId);
    return user && user.fullname ? user.fullname : userId;
  };

  const getfullName = (commenttypeid, userId) => {
    if (commenttypeid !== 2 && commenttypeid !== 3) {
      if (fullnameList) {
        return finduserbyuserid(userId);
      } else {
        if (iaoassignedToList.length > 0) {
          addToFullnameList(iaoassignedToList, 'iao');
          setFullnameList(getFullnameList());
        }
        if (ministryAssignedToList.length > 0) {
          addToFullnameList(iaoassignedToList, bcgovcode);
          setFullnameList(getFullnameList());
        }
        return finduserbyuserid(userId);
      }
    } else {
      return 'Request History';
    }
  };

  const getHtmlfromRawContent = (item) => {
    return `<p>${item.text || ''}</p>`;
  };

  const renderreplies = (i) => {
    return (
      i.replies &&
      i.replies
        .sort((a, b) => a.commentId - b.commentId)
        .map((a, replyindex) => (
          <div key={a.commentId}>
            <CommentHistory
              i={a}
              reply
              parentId={i.commentId}
              totalcommentCount={-100}
              currentIndex={replyindex}
              isreplysection={true}
              hasAnotherUserComment={false}
              fullName={getfullName(a.commentTypeId, a.userId)}
              commentTypes={commentTypes}
            />
          </div>
        ))
    );
  };

  const getTemplateName = (templateId) => {
    return applicantCorrespondenceTemplates.find((obj) => obj.templateid == templateId)?.description;
  };

  const renderrequesthistory = () => {
    if (!fullnameList?.length) return null;

    let filteredRequestNotes = requestNotes.filter(
      c => c.commentTypeId !== getCommentTypeIdByName(commentTypes, "Ministry Internal") &&
        c.commentTypeId !== getCommentTypeIdByName(commentTypes, "Ministry Peer Review")
    )
    const sortedCommentsHistory = [...filteredRequestNotes].sort((a, b) =>
      new Date(b.created_at || b.dateUF) - new Date(a.created_at || a.dateUF)
    );

    return sortedCommentsHistory.map((item, index) => {
      item.type = 'comment';
      const hasOtherUserComments = item.replies?.some((reply) => reply.userId !== currentUser.userId);
      const fullName = getfullname(item);
  
      return (
        <div
          key={`${item.type}-${index}`}
          className="historysection"
          data-comid={item.commentId || null}
          data-msgid={!item.commentId ? index : null}
        >
          {rendercomment(item, index, fullName, hasOtherUserComments)}
        </div>
      );
    });
  };
  const renderCommunications = () => {
    if (!fullnameList?.length) return null;

    const sortedCommunications = [...applicantCorrespondence].sort((a, b) =>
      new Date(b.created_at || b.dateUF) - new Date(a.created_at || a.dateUF)
    );

    return sortedCommunications.map((item, index) => {
      item.type = 'message';
      const fullName = getfullname(item);
      const emailText = getemailtext(item);
      const dateText = item.date.toUpperCase();

      return (
        <div
          key={`${item.type}-${index}`}
          className="historysection"
          data-comid={item.commentId || null}
          data-msgid={!item.commentId ? index : null}
        >
          {rendercommunication(item, index, fullName, emailText, dateText)}
        </div>
      );
    });
  };

  const getfullname = (item) => {
    return item.type === 'comment' ? getfullName(item.commentTypeId, item.userId) : getfullName(0, item.createdby);
  };

  const getemailtext = (item) => {
    if (item.type === 'comment') return '';
    const emailCount = item.emails.length;
    return emailCount === 1 ? item.emails[0] : emailCount > 1 ? `${item.emails[0]} +${emailCount - 1}` : '';
  };
  
  const rendercomment = (item, index, fullName, hasOtherUserComments) => (
    <>
      <CommentHistory
        i={item}
        totalcommentCount={-100}
        currentIndex={index}
        c={false}
        hasAnotherUserComment={hasOtherUserComments}
        fullName={fullName}
        commentTypes={commentTypes}
      />
      <div className="replySection">{renderreplies(item)}</div>
    </>
  );

  const rendercommunication = (item, index, fullName, emailText, dateText) => (
    <div className="communication-accordion" {...(item ? { "data-communication-div-id": `${index}` } : {})}>
      <Accordion expanded>
        <AccordionSummary
          aria-controls="communication-accordion-summary"
          id={`communication-accordion-${index}`}
        >
          <div className="templateList">
            <div className="templateInfo">
              {rendertemplateinfo(item, fullName, emailText, dateText)}
              {item.category !== 'response' && rendercategorychip(item)}
            </div>
          </div>
        </AccordionSummary>
        <AccordionDetails>
          <div className="commenttext" dangerouslySetInnerHTML={{ __html: getHtmlfromRawContent(item) }}></div>
          {renderattachments(item)}
        </AccordionDetails>
      </Accordion>
    </div>
  );

  const rendertemplateinfo = (item, fullName, emailText, dateText) => (
    <>
      <div className="templateUser">
        {item.category === "response" ? "Applicant Response" : getTemplateName(item.templateid)} - {fullName}
      </div>
      {item.emails.length > 0 && <div className="templateUser"> {emailText} |</div>}
      <div className="templateTime">{dateText.toUpperCase()}</div>
      <div className="templateTime">{item.edited ? "Edited" : ""}</div>
    </>
  );

  const rendercategorychip = (item) => (
    <div className="templateUser">
      {item.category !== "draft" && (
        <ClickableChip clicked={true} color="primary" label={item.sentby ? 'emailed' : 'printed'} size="small" />
      )}
    </div>
  );

  const renderattachments = (item) => (
    item.attachments?.map((attachment) => (
      <div className="email-attachment-item" key={attachment.filename}>
        <a href={`/foidocument?id=${ministryId}&filepath=${attachment.documenturipath.split('/').slice(4).join('/')}`} target="_blank">
          {attachment.filename}
        </a>
      </div>
    ))
  );

  return (
    <div>
      {selectedExportOptions.isRequestDetailsChecked &&
        <div>
          <div>
            <div className="export_title">
              <h1 className="foi-review-request-text foi-ministry-requestheadertext">Request Details</h1>
            </div>
            <ExportRequestDetailsHistory requestDetails={requestDetails} requestState={requestState}
              iaoassignedToList={iaoassignedToList} />
          </div>
          {showCFRTab() &&
            <div style={{ pageBreakInside: 'avoid' }}>
              <div className="export_title">
                <h1 className="foi-review-request-text foi-ministry-requestheadertext">CFR Forms</h1>
              </div>
              <ExportCFRForms foiRequestCFRFormHistory={foiRequestCFRFormHistory} foiRequestCFRForm={foiRequestCFRForm} />
            </div>}
            <div className="row foi-details-row">
              <div className="col-lg-12 foi-details-col">
                <hr />
              </div>
            </div>
        </div>
      }
      {
        selectedExportOptions.isApplicantCorrespondenceChecked &&
        <div style={{ pageBreakInside: 'avoid' }}>
          <div className="export_title">
            <h1 className="foi-review-request-text foi-ministry-requestheadertext">Applicant Correspondence</h1>
          </div>
          <div> {applicantCorrespondence.length === 0 ? (
            <div className="nofiltermessage">No communications under this filter category</div>
          ) : (
            renderCommunications()
          )}
          </div>
          <div className="row foi-details-row">
            <div className="col-lg-12 foi-details-col">
              <hr />
            </div>
          </div>
        </div>
      }
      {
        selectedExportOptions.isCommentsChecked &&
        <div style={{ pageBreakInside: 'avoid' }}>
          <div className="export_title">
            <h1 className="foi-review-request-text foi-ministry-requestheadertext">Comments</h1>
          </div>
          <div> {requestNotes.length === 0 ? (
            <div className="nofiltermessage">No request history under this filter category</div>
          ) : (
            renderrequesthistory()
          )}
          </div>
        </div>
      }
    </div>
  );
};

export default ExportHistory;
