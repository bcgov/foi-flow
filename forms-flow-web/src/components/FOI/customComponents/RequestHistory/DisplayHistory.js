import React, { useState } from 'react';
import './requesthistory.scss';
import 'reactjs-popup/dist/index.css';
import CommentStructure from '../Comments/CommentStructure';
import { ClickableChip } from '../../Dashboard/utils';
import { addToFullnameList, getFullnameList } from '../../../../helper/FOI/helper';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';

const DisplayHistory = ({
  requesthistory,
  bcgovcode,
  currentUser,
  iaoassignedToList,
  ministryAssignedToList,
  commentTypes,
  ministryId,
  applicantCorrespondenceTemplates,
}) => {
  const [fullnameList, setFullnameList] = useState(getFullnameList);
  const [showmorehidden, setshowmorehidden] = useState(false);

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

  const showhiddenhistory = (_e, count) => {
    let hiddenhistory = document.getElementsByName('historysectionhidden');
    if (hiddenhistory && Array.from(hiddenhistory).filter((_c) => _c.style.display === 'none').length > 0) {
      let cnt = 0;
      hiddenhistory.forEach((_com) => {
        if (cnt < count && _com.style.display === 'none') {
          _com.style.display = 'block';
          cnt++;
        }
      });
      hiddenhistory = document.getElementsByName('historysectionhidden');
      if (Array.from(hiddenhistory).filter((_c) => _c.style.display === 'none').length === 0) {
        document.getElementById('showMoreParentHistory').style.display = 'none';
        setshowmorehidden(true);
      }
    } else {
      document.getElementById('showMoreParentHistory').style.display = 'none';
    }
  };

  const checkhistorylengthforindex = (history, index) => {
    let historylenghchecker = {
      totalcharacterCount: history?.text?.length || 0,
      reachedLimit: false,
      returnindex: 10,
    };

    if (historylenghchecker.totalcharacterCount > 2000 && index > 10) {
      historylenghchecker.returnindex = index;
      historylenghchecker.reachedLimit = true;
      return historylenghchecker;
    }

    if (history.replies && history.replies.length > 0) {
      history.replies.forEach((reply) => {
        if (!historylenghchecker.reachedLimit) {
          historylenghchecker.totalcharacterCount += reply.text?.length;
          if (historylenghchecker.totalcharacterCount > 2000 && index > 10) {
            historylenghchecker.returnindex = index;
            historylenghchecker.reachedLimit = true;
            return historylenghchecker;
          }
        }
      });
    }

    return historylenghchecker;
  };

  const getHtmlfromRawContent = (item) => {
    return `<p>${item.text || ''}</p>`;
  };

  const dynamicIndexFinder = () => {
    let returnindex = 10;
    let totalcharacterCount = 0;
    let reachedLimit = false;

    requesthistory.forEach((history, index) => {
      if (!reachedLimit) {
        let historylenghchecker = checkhistorylengthforindex(history, index);
        totalcharacterCount += historylenghchecker.totalcharacterCount;
        reachedLimit = historylenghchecker.reachedLimit;
        returnindex = historylenghchecker.returnindex;
      }
    });

    return returnindex;
  };

  let limit = dynamicIndexFinder();

  const renderreplies = (i) => {
    return (
      i.replies &&
      i.replies
        .sort((a, b) => a.commentId - b.commentId)
        .map((a, replyindex) => (
          <div key={a.commentId}>
            <CommentStructure
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

    const sortedRequestHistory = [...requesthistory].sort((a, b) => 
      new Date(a.created_at || a.dateUF) - new Date(b.created_at || b.dateUF)
    );
  
    return sortedRequestHistory.map((item, index) => {
      const isHidden = index >= limit && !showmorehidden;
      const commonStyles = { display: isHidden ? 'none' : 'block' };
      const hasOtherUserComments = item.replies?.some((reply) => reply.userId !== currentUser.userId);
      const fullName = getfullname(item);
      const emailText = getemailtext(item);
      const dateText = getdatetext(item);
  
      return (
        <div
          key={`${item.type}-${index}`} 
          className="historysection"
          data-comid={item.commentId || null}
          data-msgid={!item.commentId ? index : null}
          name={isHidden ? 'historysectionhidden' : ''}
          style={commonStyles}
        >
          {item.type === 'comment' ? 
            rendercomment(item, index, fullName, hasOtherUserComments) : 
            rendercommunication(item, index, fullName, emailText, dateText)}
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
  
  const getdatetext = (item) => {
    if (item.type === 'comment') return '';
    return item.date === item.created_at ? item.date.toUpperCase() : item.date.split('|')[0].trim();
  };
  
  const rendercomment = (item, index, fullName, hasOtherUserComments) => (
    <>
      <CommentStructure
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
      <Accordion>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
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
    <div style={{ paddingBottom: '2%', marginBottom: '2%' }}>
      {requesthistory.length === 0 ? (
        <div className="nofiltermessage">No request history under this filter category</div>
      ) : (
        renderrequesthistory()
      )}
      <div
        id="showMoreParentHistory"
        className="showMoreParentHistory"
        style={!showmorehidden && requesthistory.length > 10 ? { display: 'block' } : { display: 'none' }}
      >
        <button className="btn foi-btn-create btnshowmore" onClick={(e) => showhiddenhistory(e, 5)}>
          Show more request history
        </button>
      </div>
    </div>
  );
};

export default DisplayHistory;
