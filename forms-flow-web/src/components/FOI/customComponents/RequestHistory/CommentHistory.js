import React, { useState } from 'react'
import './requesthistory.scss';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faCaretDown, faCaretUp } from '@fortawesome/free-solid-svg-icons'
import 'react-quill/dist/quill.snow.css';
import draftToHtml from 'draftjs-to-html';
import { convertToRaw, convertFromRaw, EditorState } from "draft-js";
import Chip from "@material-ui/core/Chip";
import { getCommentLabelFromId } from "../../../../helper/FOI/helper";


const CommentHistory = ({ i, reply, parentId, totalcommentCount, currentIndex, isreplysection, hasAnotherUserComment, 
  fullName, commentTypes, isEmail=false, ministryId=null}) => {

  let needCollapsed = false
  let halfDivclassname = isreplysection ? "halfDiv undermaincomment" : "halfDiv"
  needCollapsed = isreplysection && totalcommentCount > 3 && currentIndex < totalcommentCount - 2 ? true : false

  const [toggleIcon, settoggleIcon] = useState(faCaretDown)

  const setInnerText = (e, text) => {
    e.target.innerText = text
  }

  const setnodeDisplay = (commentnode, displaymode) => {
    commentnode.style.display = displaymode
  }

  const toggleCollapse = (e, parentcommentId) => {

    let hiddenreplies = document.getElementsByName(`hiddenreply_${parentcommentId}`)
    hiddenreplies.forEach((commentnode) => {
      commentnode.style.display === 'none' ? setnodeDisplay(commentnode, 'flex') : setnodeDisplay(commentnode, 'none')
    })
    let _toggleIcon = e.target.innerText === "Show more comments" ? faCaretUp : faCaretDown
    settoggleIcon(_toggleIcon)
    e.target.innerText === "Show fewer comments" ? setInnerText(e, "Show more comments") : setInnerText(e, "Show fewer comments")
  }

  const getHtmlfromRawContent = () => {
    let markup = null
    if (i.commentTypeId != null && i.commentTypeId !== 2 && i.commentTypeId !== 3) {
      const rawContentFromStore = convertFromRaw(JSON.parse(i.text))
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
      markup = `<p>${i.text}</p>`
    }

    return markup
  }
  
  return (
    <>
      <div {...(isEmail ? {"data-msg-halfdiv-id":`${currentIndex}`} : {})} name={needCollapsed ? `hiddenreply_${parentId}` : `reply_${parentId}`} 
        className={halfDivclassname} style={needCollapsed ? { display: 'none' } : {}} >
        <div
          className="userInfo"
          style={reply ? { marginLeft: 15, marginTop: '6px' }: {}}
        >
          <div className="commentsTwo">

            <div className="fullName">{fullName} </div> |  <div className="commentdate">{i.date} </div> 
            {(i.commentTypeId != null && i.commentTypeId !== 2 && i.commentTypeId !== 3 && (parentId == null || parentId == undefined)) &&
              <div>
                <Chip
                    item
                    label={getCommentLabelFromId(commentTypes, i.commentTypeId )}
                    className="commentTypeChip"
                    style={{
                      backgroundColor: "#003366",
                      margin:"4px 4px 4px 8px"
                    }}
                  />
              </div>
            }
            <div className="commentdate">{i.edited ? "Edited": ""} </div>
          </div>
          <div className="commenttext" dangerouslySetInnerHTML={{ __html: getHtmlfromRawContent() }} ></div>
        </div>
        {isEmail && i.attachments?.map((attachment) => (
          <div className="email-attachment-item" key={attachment.filename}>
            <a href={`/foidocument?id=${ministryId}&filepath=${attachment.documenturipath.split('/').slice(4).join('/')}`} target="_blank">{attachment.filename}</a>
          </div>
        ))}
      </div>
      {
        i.replies && i.replies.length > 3 ? <div className="togglecollapseAll"><FontAwesomeIcon icon={toggleIcon} size='1x' color='#003366' /> <span onClick={(e) => toggleCollapse(e, i.commentId)}>Show more comments</span></div> : ""
      }
    </>
  )
}

export default CommentHistory