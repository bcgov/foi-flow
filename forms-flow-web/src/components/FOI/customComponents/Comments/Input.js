import React, { useContext, useEffect, useState } from 'react'
import AddCommentField from './AddCommentField'
import { ActionContext } from './ActionContext'
import { addToFullnameList, getFullnameList, setTeamTagList, getIAOTagList,
  getCommentTypeIdByName, getFullnameTeamList, getAssignToList,getIAOAssignToList } from '../../../../helper/FOI/helper'

const Input = ({ add, bcgovcode, iaoassignedToList, ministryAssignedToList, setEditorChange, removeComment, setRemoveComment,
  restrictedReqTaglist, isRestricted, isMinistry,setshowaddbox, commentTypes, commentTypeId,setCommentTypeId }) => {
  
  const [fullnameList, setFullnameList] = useState(getFullnameList());


  // useEffect(() => {
  //   console.log("setTeamTagList useeffect")
  //   setTeamTagList()
  // }, [])
    
    if (!fullnameList) {
        if (iaoassignedToList.length > 0) {
          addToFullnameList(iaoassignedToList, "iao");
          setFullnameList(getFullnameList());
        }

        if (ministryAssignedToList.length > 0) {
          addToFullnameList(ministryAssignedToList, bcgovcode);
          setFullnameList(getFullnameList());
        }
    }
      

  const filterTagList = (commentTypeId) => {
    let tagList= fullnameList;
    //getIAOAssignToList();
    if(commentTypeId == getCommentTypeIdByName(commentTypes, "IAO Internal") || 
        commentTypeId == getCommentTypeIdByName(commentTypes,"IAO Peer Review") )
      tagList= getIAOTagList("iao");//getAssignToList('iao')?.filter((e) => e.type === 'iao');
    else if(commentTypeId == getCommentTypeIdByName(commentTypes, "Ministry Internal") || 
        commentTypeId == getCommentTypeIdByName(commentTypes,"Ministry Peer Review"))
      tagList = getIAOTagList(bcgovcode);
    return tagList;
  }

  const action = useContext(ActionContext)
  return  (
    restrictedReqTaglist|| fullnameList && fullnameList?.length > 0 ? 
      <AddCommentField authorImg={action.userImg} main add={add} fullnameList={filterTagList(commentTypeId)} 
        restrictedReqTaglist={restrictedReqTaglist} setEditorChange={setEditorChange} removeComment={removeComment} 
          setRemoveComment={setRemoveComment} isRestricted={isRestricted} isMinistry={isMinistry} setshowaddbox={setshowaddbox} 
          commentTypes={commentTypes} commentTypeId={commentTypeId} setCommentTypeId={setCommentTypeId}/> :null
  )
}

export default Input
