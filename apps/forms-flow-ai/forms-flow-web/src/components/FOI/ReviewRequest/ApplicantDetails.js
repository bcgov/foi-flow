import React, {useEffect} from 'react';
import "./applicantdetails.scss";
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import { useSelector } from "react-redux";
import { SelectWithLegend } from '../customComponents';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
  root: {
    '& .MuiTextField-root': {
      margin: theme.spacing(1),
      width: '25ch',
    },
  },
}));
const ApplicantDetails = React.memo((props) => {
  
    useEffect(() => {       
        //console.log(`formdata = ${props.location.state.reviewRequestData}`)
    }, [])

    const category = useSelector(state=> state.foiRequests.foiCategoryList);
    // const foiRequestDetails = useSelector(state=> state.foiRequests.foiRequestDetail);
    
    const classes = useStyles();
     return (
        
        <Card className="foi-applicant-details-card">            
            <label className="foi-applcant-details-label">APPLICANT DETAILS</label>
            <CardContent>
            <form className={classes.root} noValidate autoComplete="off">
                <div className="row foi-applicant-details-row">
                    <div className="col-lg-6 foi-applicant-details-col">                       
                        <TextField                            
                            label="Applicant First Name" 
                            InputLabelProps={{ shrink: true, }} 
                            variant="outlined" 
                            defaultValue="Jane"
                            fullWidth
                        />
                        <TextField                          
                            label="Applicant Middle Name" 
                            InputLabelProps={{ shrink: true, }} 
                            defaultValue="M" 
                            variant="outlined"
                            fullWidth
                        />
                        <TextField                            
                            label="Applicant Last Name" 
                            InputLabelProps={{ shrink: true, }} 
                            defaultValue="Deo" 
                            variant="outlined"
                            fullWidth 
                        />                                                
                    </div>
                    <div className="col-lg-6 foi-applicant-details-col">                      
                       
                        <TextField                            
                            label="Organization" 
                            InputLabelProps={{ shrink: true, }} 
                            defaultValue="The Canadian Cancer Society" 
                            variant="outlined" 
                            fullWidth
                        /> 
                        <SelectWithLegend selectData = {category} legend="Category" selectDefault="Select Category" required={true}/>
                       
                        <TextField                           
                            label="Email" 
                            InputLabelProps={{ shrink: true, }} 
                            defaultValue="email@gmail.com" 
                            variant="outlined" 
                            fullWidth
                        /> 
                    </div>
                </div> 
                </form>             
            </CardContent>
        </Card>
       
    );
  });

export default ApplicantDetails;