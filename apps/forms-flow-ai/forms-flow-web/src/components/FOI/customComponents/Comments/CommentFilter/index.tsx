import React from 'react';
import { useDispatch } from "react-redux";
import './index.scss'
import  { params } from './types'


export  const CommentFilter = ({oncommentfilterchange, filterValue}:params) => {
const dispatch = useDispatch();

return (

            <fieldset>
              <legend style={{display: 'none'}}>Filter Comments</legend>
              <input type="radio" id="rballcomments" name="commentsfilter" value={-1} onChange={oncommentfilterchange} checked={filterValue === -1 ? true:false} />
              <label htmlFor="rballcomments">All Comments</label>
              <input type="radio" id="rbrequesthistory" name="commentsfilter" value={2} onChange={oncommentfilterchange} />
              <label htmlFor="rbrequesthistory">Request History</label>
              <input type="radio" id="rbusercomments" name="commentsfilter" value={1} onChange={oncommentfilterchange} />
              <label htmlFor="rbusercomments">User Comments</label>
            </fieldset>
         
);

}

export default CommentFilter;