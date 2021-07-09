import React, {useEffect} from 'react';
import {Form} from 'react-formio';
import formData from './reviewrequest.json';
import 'formiojs/dist/formio.builder.min.css';

const ReviewRequest = React.memo((props) => {
  
    useEffect(() => {       
        //console.log(`formdata = ${props.location.state.reviewRequestData}`)
    }, [])

     return (  
        <div className="container">    
        <div style={{maxWidth: '400px', margin: '50px'}}>
            <Form form={formData}/>
            
         
            {/* <h3>Your FOI Request Queue</h3> */}
            
            </div>
      </div>
    );
  });

export default ReviewRequest;