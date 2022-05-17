import React, { useEffect, useState } from 'react';
import Link from '@material-ui/core/Link';
import { useSelector } from "react-redux";
import { makeStyles } from '@material-ui/core/styles';
import "./foirequestheader.scss";
import TextField from '@material-ui/core/TextField';
import { getMenuItems, getAssignedTo, getStatus, getFullName} from "./utils";
import Input from '@material-ui/core/Input';
import FOI_COMPONENT_CONSTANTS from '../../../../constants/FOI/foiComponentConstants';
import { StateEnum } from '../../../../constants/FOI/statusEnum';
import { useParams } from 'react-router-dom';
import { calculateDaysRemaining } from "../../../../helper/FOI/helper";
import { Watcher } from '../../customComponents'

const useStyles = makeStyles((theme) => ({
    formControl: {
      margin: theme.spacing(1),
      minWidth: 120,
    },
    item: {
        paddingLeft: theme.spacing(3),
    },
    group: {
        fontWeight: theme.typography.fontWeightBold,
        opacity: 1,
    },
  }));
const FOIRequestHeader = React.memo(
  ({
    headerValue,
    headerText,
    requestDetails,
    handleAssignedToInitialValue,
    handleAssignedToValue,
    createSaveRequestObject,
    handlestatusudpate,
    userDetail,
    disableInput,
  }) => {
    /**
     *  Header of Review request in the UI
     *  AssignedTo - Mandatory field
     */
    const classes = useStyles();
    const { requestId, ministryId } = useParams();

    //get the assignedTo master data
    const assignedToList = useSelector(
      (state) => state.foiRequests.foiAssignedToList
    );

    //handle default value for the validation of required fields
    React.useEffect(() => {
      let _daysRemaining = calculateDaysRemaining(requestDetails.dueDate);
      let _status = getStatus({ headerValue, requestDetails });
      const _cfrDaysRemaining = requestDetails.cfrDueDate
        ? calculateDaysRemaining(requestDetails.cfrDueDate)
        : "";
      handlestatusudpate(_daysRemaining, _status, _cfrDaysRemaining);
     
    }, [requestDetails, handleAssignedToInitialValue, handlestatusudpate]);

    useEffect(() => {
        setAssignedTo(getAssignedTo(requestDetails));
    }, [requestDetails]);

    const [selectedAssignedTo, setAssignedTo] = React.useState(() => getAssignedTo(requestDetails));
    const [menuItems, setMenuItems] = useState([])

    const preventDefault = (event) => event.preventDefault();

    useEffect(() => {
      // handle case where assigned user was removed from group
      if (assignedToList && assignedToList.length > 0) {
        var assignedTeam = assignedToList.find(team => team.name === requestDetails.assignedGroup);
        if (assignedTeam && requestDetails.assignedTo && !assignedTeam.members.find(member => member.username === requestDetails.assignedTo)) {
          setAssignedTo("|Unassigned");
          handleAssignedToValue("|Unassigned");
        }
      }
    }, [assignedToList]);

    useEffect(() => {
      setMenuItems(
        getMenuItems({ classes, assignedToList, selectedAssignedTo })
      );
    }, [selectedAssignedTo, assignedToList]);    

    //handle onChange event for assigned To
    const handleAssignedToOnChange = (event) => {
      setAssignedTo(event.target.value);
      //event bubble up - to validate required fields
      handleAssignedToValue(event.target.value);
      createSaveRequestObject(
        FOI_COMPONENT_CONSTANTS.ASSIGNED_TO,
        event.target.value,
        event.target.name
      );
    };

    const status = getStatus({ headerValue, requestDetails });

    const showMinistryAssignedTo =
      status.toLowerCase() === StateEnum.callforrecords.name.toLowerCase() ||
      status.toLowerCase() === StateEnum.closed.name.toLowerCase() ||
      status.toLowerCase() === StateEnum.deduplication.name.toLowerCase() ||
      status.toLowerCase() === StateEnum.harms.name.toLowerCase() ||
      status.toLowerCase() === StateEnum.review.name.toLowerCase() ||
      status.toLowerCase() === StateEnum.feeassessed.name.toLowerCase() ||
      status.toLowerCase() === StateEnum.consult.name.toLowerCase() ||
      status.toLowerCase() === StateEnum.signoff.name.toLowerCase() ||
      status.toLowerCase() === StateEnum.onhold.name.toLowerCase() ||
      status.toLowerCase() === StateEnum.response.name.toLowerCase();

    const getMinistryAssignedTo = () => {
      if (requestDetails?.assignedministryperson)
        return getFullName(requestDetails?.assignedministrypersonLastName, requestDetails?.assignedministrypersonFirstName, requestDetails?.assignedministryperson);
      return requestDetails.assignedministrygroup;
    }
    const ministryAssignedTo = getMinistryAssignedTo();
    return (
      <div className="foi-request-review-header-row1">
        <div className="foi-request-review-header-col1">
          <div className="foi-request-review-header-col1-row">
            <Link href="#" onClick={preventDefault}>
              <h3 className="foi-review-request-text">{headerText}</h3>
            </Link>
          </div>
          {window.location.href.indexOf(FOI_COMPONENT_CONSTANTS.ADDREQUEST) ===
            -1 && (
            <div
              className="foi-request-review-header-col1-row"
              style={{ marginTop: 5 + "px", display: "block" }}
            >
              <Watcher
                watcherFullList={assignedToList}
                requestId={requestId}
                ministryId={ministryId}
                userDetail={userDetail}
                disableInput={disableInput}
              />
            </div>
          )}
        </div>

        <div className="foi-assigned-to-container">
          <div className="foi-assigned-to-inner-container">
            <TextField
              id="assignedTo"
              label={showMinistryAssignedTo ? "IAO Assigned To" : "Assigned To"}
              inputProps={{ "aria-labelledby": "assignedTo-label"}}
              InputLabelProps={{ shrink: true }}
              select
              value={selectedAssignedTo}
              onChange={handleAssignedToOnChange}
              input={<Input />}
              variant="outlined"
              fullWidth
              required
              disabled={disableInput}
              error={selectedAssignedTo.toLowerCase().includes("unassigned")}
            >
              {menuItems}
            </TextField>
          </div>

          {showMinistryAssignedTo && (
            <>
            <TextField
                id="ministryAssignedTotxt"
                label="Ministry Assigned To"
                InputLabelProps={{ shrink: true }}
                value={ministryAssignedTo}
                variant="outlined"
                fullWidth
                disabled={true}
              />
            </>
          )}
        </div>
      </div>
    );
  }
);

export default FOIRequestHeader;