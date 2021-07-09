import React from 'react';
import './attacheddocument.scss';
import InputLabel from '@material-ui/core/InputLabel';
const AttachedDocument = React.memo((props) => {
    
    // const labelData = props.labelData;
    // const legendData = labelData.label;
    // const inputLabel = labelData.value;
     return ( 
         
            <InputLabel id="demo-simple-select-label" className="foi-attached-documents-label">Attached Documents</InputLabel>
            // <div className="foi-attached-documents-label">
            //     Attached Documents
            // </div>

    
    );
  });
export default AttachedDocument;