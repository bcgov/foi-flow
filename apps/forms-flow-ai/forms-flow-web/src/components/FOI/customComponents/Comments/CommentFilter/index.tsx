import React from 'react';
import { useDispatch } from "react-redux";
import './index.scss'
import  { params } from './types'


export  const CommentFilter = ({oncommentfilterchange}:params) => {
const dispatch = useDispatch();

return (

            <fieldset>
              <legend style={{display: 'none'}}>Filter Comments</legend>
              <input type="radio" id="rballcomments" name="commentsfilter" value={-1} onChange={(e)=>oncommentfilterchange(e)} checked={true} />
              <label htmlFor="rballcomments">All Comments</label>
              <input type="radio" id="rbrequesthistory" name="commentsfilter" value={2} onChange={(e)=>oncommentfilterchange(e)} />
              <label htmlFor="rbrequesthistory">Request History</label>
              <input type="radio" id="rbusercomments" name="commentsfilter" value={1} onChange={(e)=>oncommentfilterchange(e)} />
              <label htmlFor="rbusercomments">User Comments</label>
            </fieldset>
         
);

}

export default CommentFilter;