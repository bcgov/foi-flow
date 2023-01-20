import React, { useContext, useState, useEffect } from 'react'
import { useSelector } from "react-redux"
import AddCommentField from './AddCommentField'
import { ActionContext } from './ActionContext'
import { addToFullnameList, getFullnameList, addToRestrictedRequestTagList,getRestrictedRequestTagList, getAssignToList } from '../../../../helper/FOI/helper'

const Input = ({ add, bcgovcode, iaoassignedToList, ministryAssignedToList, setEditorChange, removeComment, setRemoveComment,
  restrictedReqTaglist }) => {
  
  const [fullnameList, setFullnameList] = useState(getFullnameList());
  //const [commentTagList, setCommentTagList] = useState(getRestrictedRequestTagList());

   //console.log("fullnameList",fullnameList)
 
    if (!fullnameList) {
        console.log("Else!!");
        if (iaoassignedToList.length > 0) {
          addToFullnameList(iaoassignedToList, "iao");
          setFullnameList(getFullnameList());
          //setCommentTagList(getFullnameList());
        }

        if (ministryAssignedToList.length > 0) {
          addToFullnameList(ministryAssignedToList, bcgovcode);
          setFullnameList(getFullnameList());
          //setCommentTagList(getFullnameList());
        }
    }
      




  const action = useContext(ActionContext)
  return  (
    restrictedReqTaglist|| fullnameList && fullnameList?.length > 0 ? <AddCommentField authorImg={action.userImg} main add={add} fullnameList={fullnameList} restrictedReqTaglist={restrictedReqTaglist} setEditorChange={setEditorChange} removeComment={removeComment} setRemoveComment={setRemoveComment} /> :null
  )
}

export default Input
