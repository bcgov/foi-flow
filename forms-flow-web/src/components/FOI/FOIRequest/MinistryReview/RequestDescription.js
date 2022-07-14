import React from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import { useSelector } from "react-redux";
import { makeStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import { formatDate } from '../../../../helper/FOI/helper';
import RequestDescriptionHistory from "../../RequestDescriptionHistory";
import './RequestDescription.scss'

const useStyles = makeStyles((_theme) => ({
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
    const _requestDetails = requestDetails.requestDetails;
    let requestDescriptionHistoryList = useSelector(state => state.foiRequests.foiRequestDescriptionHistoryList);
    const sortedList = requestDescriptionHistoryList.sort((a, b) => {
        return new Date(a.createdAt) - new Date(b.createdAt);
    });
    const filteredList = sortedList.filter((request, index, self) =>
        index === self.findIndex((copyRequest) => (
            copyRequest.description === request.description && copyRequest.fromDate === request.fromDate && copyRequest.toDate === request.toDate
        ))
    )

    const [openModal, setOpenModal] = React.useState(false);
    const handleDescriptionHistoryClick = () => {
        setOpenModal(true);
    }
    const handleModalClose = () => {
        setOpenModal(false);
    }
    return (
      <Card id="requestDescriptionMinistry" className="foi-details-card">
        <RequestDescriptionHistory
          requestDescriptionHistoryList={filteredList}
          openModal={openModal}
          handleModalClose={handleModalClose}
        />
        <div className="row foi-details-row">
          <div className="col-lg-8 foi-details-col">
            <label className="foi-details-label">REQUEST DESCRIPTION</label>
          </div>
          <div className="col-lg-4 foi-details-col">
            <div className="foi-request-description-history">
              <button
                type="button"
                className={`btn btn-link btn-description-history ${
                  filteredList.length <= 1 ? classes.btndisabled : ""
                }`}
                disabled={filteredList.length <= 1}
                onClick={handleDescriptionHistoryClick}
              >
                Description History
              </button>
            </div>
          </div>
        </div>
        <CardContent>
          <div className="row foi-details-row">
            <div className="col-lg-12 foi-details-col">
              <div className="ministry-request-description-row">
                <Typography className="ministry-heading">
                  <b>Date Range for Record Search</b>
                </Typography>
                <div className="ministry-request-dates">
                  <Typography className="ministry-start-date ministry-heading">
                    <b>Start Date: </b>
                    {_requestDetails.fromDate
                      ? formatDate(
                          _requestDetails.fromDate,
                          "MMM dd yyyy"
                        ).toUpperCase()
                      : ""}
                  </Typography>
                  <Typography>
                    <b>End Date: </b>
                    {_requestDetails.toDate
                      ? formatDate(
                          _requestDetails.toDate,
                          "MMM dd yyyy"
                        ).toUpperCase()
                      : ""}
                  </Typography>
                </div>
              </div>
              <Typography className="ministry-bottom-request-description-header ministry-heading">
                <b>Request Description</b>
              </Typography>
              <Typography>{_requestDetails.description}</Typography>
            </div>
          </div>
        </CardContent>
      </Card>
    );


})


export default RequestDescription;