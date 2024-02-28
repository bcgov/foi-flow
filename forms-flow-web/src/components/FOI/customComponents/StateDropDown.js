import React, { useState } from "react";
import TextField from "@material-ui/core/TextField";
import MenuItem from "@material-ui/core/MenuItem";
import Input from "@material-ui/core/Input";
import "./statedropdown.scss";
import {
  StateList,
  MinistryStateList,
  StateEnum,
} from "../../../constants/FOI/statusEnum";
import { useSelector } from "react-redux";

import FOI_COMPONENT_CONSTANTS from "../../../constants/FOI/foiComponentConstants";
import { isBeforeOpen } from "../FOIRequest/utils";

const StateDropDown = ({
  requestState = StateEnum.unopened.name,
  requestStatus,
  handleStateChange,
  isMinistryCoordinator,
  isValidationError,
  stateTransition,
  updateStateDropDown,
  requestType,
  disabled,
}) => {
  const _isMinistryCoordinator = isMinistryCoordinator;

  const [status, setStatus] = useState(requestState);
  const cfrFeeData = useSelector(
    (reduxState) => reduxState.foiRequests.foiRequestCFRForm.feedata
  );
  const cfrStatus = useSelector(
    (reduxState) => reduxState.foiRequests.foiRequestCFRForm.status
  );

  let requestDetails = useSelector(
    (state) => state.foiRequests.foiRequestDetail
  );

  React.useEffect(() => {
    if (requestState && requestState !== status) {
      setStatus(requestState);
    }
  }, [requestState, updateStateDropDown]);

  const handleChange = (event) => {
    setStatus(event.target.value);
    handleStateChange(event.target.value);
  };

  const getClosedList = () => {
    const stateArray = [
      ...new Set(
        stateTransition &&
          stateTransition.map((_state) =>
            JSON.stringify({ status: _state.status })
          )
      ),
    ].map((s) => JSON.parse(s));
    const isCFR = stateArray.some(
      (_state) =>
        _state.status.toLowerCase() ===
        StateEnum.callforrecords.name.toLowerCase()
    );
    const isUnopened = stateArray.some(
      (_state) =>
        _state.status.toLowerCase() === StateEnum.unopened.name.toLowerCase()
    );
    let resultArray = [];
    if (isCFR) {
      resultArray = stateArray.filter(
        (_state) =>
          _state.status.toLowerCase() !== StateEnum.open.name.toLowerCase()
      );
    } else if (isUnopened) {
      resultArray = stateArray.filter(
        (_state) =>
          _state.status.toLowerCase() !== StateEnum.unopened.name.toLowerCase()
      );
    } else {
      resultArray = stateArray;
    }
    return resultArray;
  };

  const getStatusList = () => {
    let _state = "";
    if (requestState) _state = requestState;
    else if (
      requestStatus &&
      requestStatus != undefined &&
      requestStatus.toLowerCase().includes("days")
    )
      _state = "Open";
    else _state = requestStatus;

    let _stateList = StateList;
    if (_isMinistryCoordinator) {
      _stateList = MinistryStateList;
    }
    const personalRequest =
      requestType?.toLowerCase() ===
      FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_PERSONAL;
    const personalIAO = !_isMinistryCoordinator && personalRequest;
    const previousState =
      stateTransition?.length > 0 && stateTransition[1]?.status;
    switch (_state.toLowerCase()) {
      case StateEnum.unopened.name.toLowerCase():
        return _stateList.unopened;
      case StateEnum.intakeinprogress.name.toLowerCase():
        if (personalIAO) {
          return _stateList.intakeinprogressforpersonals;
        } else {
          return _stateList.intakeinprogress;
        }
      case StateEnum.peerreview.name.toLowerCase():
        if (!isMinistryCoordinator) {
          //const currentStatusVersion = stateTransition[0]?.version;
          if (previousState === StateEnum.intakeinprogress.name) {
            return _stateList.intakeinprogress;
          } else if (previousState === StateEnum.open.name)
            return _stateList.open;
          else if (previousState === StateEnum.review.name)
            return _stateList.review;
          else if (previousState === StateEnum.consult.name)
            return _stateList.consult;
          else if (previousState === StateEnum.response.name)
            return _stateList.response;
          else if (previousState === StateEnum.appfeeowing.name)
            return _stateList.appfeeowing;
        } else {
          return _stateList.peerreview;
        }
      case StateEnum.open.name.toLowerCase():
        return _stateList.open;
      case StateEnum.closed.name.toLowerCase():
        return getClosedList();
      case StateEnum.redirect.name.toLowerCase():
        return _stateList.redirect;
      case StateEnum.callforrecords.name.toLowerCase():
        if (_isMinistryCoordinator && personalRequest)
          return _stateList.callforrecordsforpersonal;
        if (
          personalIAO &&
          (requestDetails.bcgovcode.toLowerCase() === "mcf" ||
            requestDetails.bcgovcode.toLowerCase() === "msd")
        )
          return _stateList.callforrecordscfdmsdpersonal;
        return _stateList.callforrecords;
      case StateEnum.tagging.name.toLowerCase():
        return _stateList.tagging;
      case StateEnum.readytoscan.name.toLowerCase():
        return _stateList.readytoscan;
      case StateEnum.review.name.toLowerCase():
        if (
          personalIAO &&
          (requestDetails.bcgovcode.toLowerCase() === "mcf" ||
            requestDetails.bcgovcode.toLowerCase() === "msd")
        )
          return _stateList.reviewcfdmsdpersonal;
        return _stateList.review;
      case StateEnum.onhold.name.toLowerCase():
        if (previousState === StateEnum.response.name) {
          return _stateList.onhold.filter(
            (_state) =>
              _state.status.toLowerCase() !==
              StateEnum.callforrecords.name.toLowerCase()
          );
        } else if (previousState === StateEnum.feeassessed.name) {
          return _stateList.onhold.filter(
            (_state) =>
              _state.status.toLowerCase() !==
              StateEnum.response.name.toLowerCase()
          );
        }
        return _stateList.onhold;
      case StateEnum.consult.name.toLowerCase():
        return _stateList.consult;
      case StateEnum.signoff.name.toLowerCase():
        return _stateList.signoff;
      case StateEnum.feeassessed.name.toLowerCase():
        if (personalIAO) return _stateList.feeassessedforpersonal;
        return _stateList.feeassessed;
      case StateEnum.deduplication.name.toLowerCase():
        return _stateList.deduplication;
      case StateEnum.harms.name.toLowerCase():
        return _stateList.harms;
      case StateEnum.response.name.toLowerCase():
        if (personalIAO) return _stateList.responseforpersonal;
        else if (cfrFeeData?.balanceremaining > 0 && cfrStatus === "approved") {
          return _stateList.response;
        } else {
          return _stateList.response.filter(
            (val) =>
              val.status.toLowerCase() !== StateEnum.onhold.name.toLowerCase()
          );
        }
      case StateEnum.section5pending.name.toLowerCase():
        if (personalIAO) {
          return _stateList.section5pending;
        }
        break;
      case StateEnum.appfeeowing.name.toLowerCase():
        return _stateList.appfeeowing;

      default:
        return [];
    }
  };
  const getDisableMenuItem = (index, status) => {
    if (index === 0) {
      return false;
    }

    return isValidationError || requestState === StateEnum.unopened.name ||
      (isBeforeOpen(requestDetails)
        && status === 'Open'
        //&& !requestDetails.foiRequestApplicantID comment back in after axis decomission
      );
  };
  const statusList = getStatusList();
  const menuItems =
    statusList.length > 0 &&
    statusList.map((item, index) => {
      return (
        <MenuItem
          disabled={getDisableMenuItem(index, item.status)}
          className="foi-state-menuitem"
          key={item.status}
          value={item.status}
        >
          <span
            className={`foi-menuitem-span ${item.status
              .toLowerCase()
              .replace(/\s/g, "")}`}
          ></span>
          {item.status}
        </MenuItem>
      );
    });
  return (
    <TextField
      id="foi-status-dropdown"
      label="Status"
      className="foi-state-dropdown"
      InputLabelProps={{ shrink: false }}
      inputProps={{ "aria-labelledby": "foi-status-dropdown-label" }}
      select
      value={status}
      onChange={handleChange}
      input={<Input />}
      variant="outlined"
      fullWidth
      disabled={disabled}
    >
      {menuItems}
    </TextField>
  );
};

export default StateDropDown;
