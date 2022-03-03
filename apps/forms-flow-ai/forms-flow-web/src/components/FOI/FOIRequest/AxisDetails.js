import React from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';


const AxisDetails = React.memo(({  
    requestDetails,
    createSaveRequestObject,
    syncAxisData
}) => {

    const [axisRequestId, setAxisRequestId] = React.useState(requestDetails?.axisRequestId);
    let sampleRequestDetails = {};
    const handleAxisIdChange = (e) => {
        setAxisRequestId(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.AXIS_REQUEST_ID, e.target.value);
    }

    const syncWithAxis = () => {
        sampleRequestDetails = {"axisRequestId":"EDU-2015-50012","axisSyncDate":"2022-03-03T13:59:18Z",
        "description":"Copies of all my school records when taught by Miss Stacey at the Avonlea School.","fromDate":null,
        "toDate":null,"requestType":"personal","receivedDate":"2015-02-19","receivedDateUF":"2015-02-19T00:00:00Z",
        "requestProcessStart":"2015-02-19","dueDate":"2015-04-09","originalDueDate":null,"category":"Individual","receivedMode":"Email",
        "deliveryMode":"Secure File Transfer","ispiiredacted":true,"firstName":"Anne","middleName":"","lastName":"Shirely",
        "businessName":"Rollings Reliables","email":"redhairedanne@greengables.ca","address":"Green Gables","addressSecondary":"",
        "city":"Avonlea","province":"Prince Edward Island","country":"Canada","postal":"K9K 9K9","phonePrimary":"250-998-8956",
        "phoneSecondary":"250-153-1864","workPhonePrimary":"250-545-2454","workPhoneSecondary":"","correctionalServiceNumber":null,
        "publicServiceEmployeeNumber":null,"selectedMinistries":[{"code":"EDUC"}],"additionalPersonalInfo":{"birthDate":null,
        "anotherFirstName":"","anotherMiddleName":"","anotherLastName":"","personalHealthNumber":""},"Extensions":[{"extensionreasonid":8,
        "extendedduedays":1,"extededduedate":"2015-04-07","extensionstatusid":2,"approvednoofdays":1,"approveddate":"2015-02-24",
        "denieddate":"2015-02-24"}]};
        syncAxisData(sampleRequestDetails);
    }

     return (
        
        <Card className="foi-details-card">            
            <label className="foi-details-label">AXIS DETAILS</label>
            <CardContent>          
                <div className="row foi-details-row">
                    <div className="col-lg-6 foi-details-col">                       
                        <TextField                            
                            label="AXIS ID Number" 
                            InputLabelProps={{ shrink: true, }} 
                            variant="outlined"                             
                            value={axisRequestId}
                            fullWidth
                            onChange={handleAxisIdChange}
                            required={true}
                        />
                    </div>
                    <div className="col-lg-6 foi-details-col">                       
                        <button type="button" onClick={() => syncWithAxis()} style={{float: "right"}} disabled={!axisRequestId}
                        className='btn-axis-sync'>Sync with AXIS</button>
                    </div>
                </div>             
            </CardContent>
        </Card>       
    );
  });

export default AxisDetails;