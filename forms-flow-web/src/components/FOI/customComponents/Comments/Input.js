import React, { useContext, useState } from 'react'
import AddCommentField from './AddCommentField'
import { ActionContext } from './ActionContext'
import { addToFullnameList, getFullnameList } from '../../../../helper/FOI/helper'

const Input = ({ add, bcgovcode, iaoassignedToList, ministryAssignedToList, setEditorChange, removeComment, setRemoveComment,
  restrictedReqTaglist, isRestricted }) => {
  
  const [fullnameList, setFullnameList] = useState(getFullnameList());
 
    if (!fullnameList) {
        console.log("Else!!");
        if (iaoassignedToList.length > 0) {
          addToFullnameList(iaoassignedToList, "iao");
          setFullnameList(getFullnameList());
        }

        if (ministryAssignedToList.length > 0) {
          addToFullnameList(ministryAssignedToList, bcgovcode);
          setFullnameList(getFullnameList());
        }
    }
      




  const action = useContext(ActionContext)
  return  (
    restrictedReqTaglist|| fullnameList && fullnameList?.length > 0 ? <AddCommentField authorImg={action.userImg} main add={add} fullnameList={fullnameList} restrictedReqTaglist={restrictedReqTaglist} setEditorChange={setEditorChange} removeComment={removeComment} setRemoveComment={setRemoveComment} isRestricted={isRestricted} /> :null
  )
}

export default Input
