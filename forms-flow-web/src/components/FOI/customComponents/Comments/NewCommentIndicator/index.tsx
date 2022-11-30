import { addBusinessDays } from "../../../../../helper/FOI/helper"
import { params } from "./types"
import './index.scss'
import {FOI_FLOW_NEW_COMMENT_EXPIRY_IN_DAYS} from '../../../../../constants/constants'

export const NewCommentIndicator = ({commentdate}:params) =>{

    let newcommmentexpirydate = new Date()
    if(commentdate != undefined && commentdate !='')
    {
        let _newexpirydate = addBusinessDays(commentdate.toString(),FOI_FLOW_NEW_COMMENT_EXPIRY_IN_DAYS)
        newcommmentexpirydate = new Date(_newexpirydate)
    }
    var today = new Date();
    return (<span className={newcommmentexpirydate > today ?'newComment' : '' }></span>);

  }


  export default NewCommentIndicator;

