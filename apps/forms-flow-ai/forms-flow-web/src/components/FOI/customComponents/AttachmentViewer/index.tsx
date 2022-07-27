import React from 'react';
import { useDispatch } from "react-redux";
import  { params } from './types'

import {getFOIS3DocumentPreSignedUrl} from '../../../../apiManager/services/FOI/foiOSSServices'


export  const AttachmentViewer = ({filepath}:params) => {
const dispatch = useDispatch();
const [presignedUrl, setpresignedUrl] = React.useState(filepath);

    React.useEffect(() => {
            if(filepath)
            {
                  const response = getFOIS3DocumentPreSignedUrl(filepath, dispatch)
                  response.then((result)=>{
                        console.log(result.data)
                        var viwerUrl =   result.data
                        if(filepath.toLowerCase().indexOf('.docx') >-1 ||filepath.toLowerCase().indexOf('.doc') >-1 || filepath.toLowerCase().indexOf('.xls') >-1 || filepath.toLowerCase().indexOf('.xlsx')>-1)
                        { 
                         viwerUrl =`https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(result.data)}`
                        }
                                                   
                        setpresignedUrl(viwerUrl)
                        console.log(JSON.stringify(result));
                  })
                           
                  console.log(filepath)
            }            
      },[filepath]);

return (<div><h5><iframe
      height="750px"
      width="100%"
      src={presignedUrl}
     /></h5></div>);

}

export default AttachmentViewer;