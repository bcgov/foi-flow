import React from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import { InputLabel } from '@material-ui/core';
import { useSelector } from "react-redux";
import { makeStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import { formatDate } from '../../../../helper/FOI/helper';
import RequestDescriptionHistory from "../../RequestDescriptionHistory";

const useStyles = makeStyles((theme) => ({
    headingError: {
      color: "#ff0000"    
    },
    headingNormal: {
      color: "000000"
    },
    btndisabled: { 
      color: "#808080"
    }
}));

const RequestDescription = React.memo((requestDetails) => {
    const classes = useStyles();
    var requestDescriptionHistoryList = useSelector(state=> state.foiRequests.foiRequestDescriptionHistoryList);
    const filteredList = requestDescriptionHistoryList.filter((request, index, self) =>
        index === self.findIndex((copyRequest) => (
            copyRequest.description === request.description && copyRequest.fromDate === request.fromDate && copyRequest.toDate === request.toDate
        ))
    )
    const sortedList = filteredList.sort((a, b) => {       
        return new Date(a.createdAt) - new Date(b.createdAt);
    });

    const [openModal, setOpenModal] = React.useState(false);
    const handleDescriptionHistoryClick = () => {
        setOpenModal(true);
    }
    const handleModalClose = () => {
        setOpenModal(false);
    }
    return (
        
        <Card className="foi-details-card">            
            <label className="foi-details-label">REQUEST DESCRIPTION</label>
            <CardContent>
            <RequestDescriptionHistory requestDescriptionHistoryList={sortedList} openModal={openModal} handleModalClose={handleModalClose}/>
                <div className="row foi-details-row">
                  
                    <div className="foi-request-description-history">
                        <button type="button" className={`btn btn-link btn-description-history ${!(sortedList.length > 1)? classes.btndisabled : ""}`} disabled={!(sortedList.length > 1)}  onClick={handleDescriptionHistoryClick}>
                            Description History
                        </button>
                    </div> 
                </div>
                <div className="row foi-details-row">
                  
                  <div className="col-lg-10 foi-details-col">
                    <div className="acc-request-description-row">
                        <Typography className="acc-daterange-heading"><b>Date Range for Record Search</b></Typography>
                        <div className="acc-request-dates">
                            <Typography className="acc-start-date"><b>Start Date: </b>{requestDetails.requestDetails.fromDate ? formatDate(requestDetails.requestDetails.fromDate, 'yyyy MMM dd') : ""}</Typography>
                            <Typography><b>End Date: </b>{requestDetails.requestDetails.toDate ? formatDate(requestDetails.requestDetails.toDate, 'yyyy MMM dd') : ""}</Typography>
                        </div>                                                              
                    </div>
                    <Typography className="acc-bottom-request-description-header"><b>Request Description</b></Typography>
                    <Typography>
                    {requestDetails.requestDetails.description}
                    </Typography>
                  </div>
              </div>               
            </CardContent>
        </Card>       
    );


})


export default RequestDescription;