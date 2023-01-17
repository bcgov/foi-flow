import React, { useContext, useState, useEffect } from 'react'
import { useSelector } from "react-redux"
import AddCommentField from './AddCommentField'
import { ActionContext } from './ActionContext'
import { addToFullnameList, getFullnameList, addToRestrictedRequestTagList,getRestrictedRequestTagList, getAssignToList } from '../../../../helper/FOI/helper'

const Input = ({ add, bcgovcode, iaoassignedToList, ministryAssignedToList, setEditorChange, removeComment, setRemoveComment,
  isRestricted,assigneeDetails,requestWatchers }) => {
  
  const [fullnameList, setFullnameList] = useState(getFullnameList());
  const [commentTagList, setCommentTagList] = useState(getRestrictedRequestTagList());

  useEffect(()=>{
    if(isRestricted){
      addToRestrictedRequestTagList(requestWatchers, assigneeDetails, fullnameList, bcgovcode);
      let tagList = getRestrictedRequestTagList();
      
      //console.log("tagList", tagList);
      //console.log("bcgovcode:{}",bcgovcode , getAssignToList(bcgovcode));
      setCommentTagList(tagList);
    }
    else{
      if (!fullnameList) {
          console.log("Else!!");
          if (iaoassignedToList.length > 0) {
            addToFullnameList(iaoassignedToList, "iao");
            setFullnameList(getFullnameList());
            setCommentTagList(getFullnameList());
          }

          if (ministryAssignedToList.length > 0) {
            addToFullnameList(ministryAssignedToList, bcgovcode);
            setFullnameList(getFullnameList());
            setCommentTagList(getFullnameList());
          }
      }
      setCommentTagList(fullnameList);
    }
  }, [requestWatchers, assigneeDetails])


  const action = useContext(ActionContext)
  return  (
    commentTagList && commentTagList?.length > 0 ? <AddCommentField authorImg={action.userImg} main add={add} fullnameList={commentTagList} setEditorChange={setEditorChange} removeComment={removeComment} setRemoveComment={setRemoveComment} /> :null
  )
}

export default Input
