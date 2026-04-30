import React, { useState, memo, useEffect } from "react";
import { makeStyles } from "@material-ui/core/styles";
import {
  Box,
  Grid,
  IconButton,
  InputAdornment,
  InputBase,
  Paper,
} from "@mui/material";
import { ApplicantProfileSearchView } from "./ApplicantProfileSearchView";
import { DataGrid, GridSearchIcon } from "@mui/x-data-grid";
import { useDispatch } from "react-redux";

const useStyles = makeStyles((theme) => ({
  root: {
    "& .MuiTextField-root": {
      margin: theme.spacing(1, "0px"),
    },
  },
  disabledTitle: {
    opacity: "0.3",
  },
}));

const ApplicantProfileAdmin = React.memo(
  ({ modalOpen, handleModalClose, applicantType = "applicant" }) => {
    const [rows, setRows] = useState([]);
    const [primaryApplicantID, setPrimaryApplicantID] = useState();
    const [selectionModel, setSelectionModel] = React.useState([]);
    useEffect(() => {
      console.log("selectionModel: ", selectionModel);
    }, [selectionModel]);
    const dispatch = useDispatch();
    // const rows = [{"firstName": "fname", "foiRequestApplicantID": 1, "middleName": "mname"}];
    const columns = [
      {
        field: "firstName",
        headerName: "FIRST NAME",
        flex: 1,
      },
      {
        field: "middleName",
        headerName: "MIDDLE NAME",
        flex: 1,
      },
      {
        field: "lastName",
        headerName: "LAST NAME",
        flex: 1,
      },
      {
        field: "birthDate",
        headerName: "DATE OF BIRTH",
        flex: 1,
        valueGetter: (params) => params.row?.additionalPersonalInfo?.birthDate,
      },
      {
        field: "email",
        headerName: "EMAIL",
        flex: 1,
      },
      {
        field: "category",
        headerName: "CATEGORY",
        flex: 1,
      },
    ];

    const searchKeywords = () => {
      return;
    };

    const mergeProfiles = () => {
      console.log("MERGING: ", selectionModel);
      console.log("Primary: ", primaryApplicantID)
    };
    
    const onSelectionModelChange = (newSelectionModel) => {
        console.log('newSelectionModel: ', newSelectionModel)
        if (!primaryApplicantID && newSelectionModel.length > 0) setPrimaryApplicantID(newSelectionModel[0])
        if (primaryApplicantID && newSelectionModel.length == 0) setPrimaryApplicantID(null)
        if (primaryApplicantID && !newSelectionModel.includes(primaryApplicantID)) setPrimaryApplicantID(newSelectionModel[0])
        setSelectionModel(newSelectionModel);
    }

    useEffect(() => {
        console.log('PRIMARY ID: ', primaryApplicantID)
        console.log('SELECTION MODEL: ', selectionModel)
    }, [primaryApplicantID, selectionModel])

    return (
      <>
        <div>BREAK</div>
        <div>BREAK</div>
        <div>BREAK</div>
        <input
          id="primary-applicant"
          placeholder="Primary Applicant ID"
          value={primaryApplicantID}
          onChange={(e) => setPrimaryApplicantID(e.target.value)}
        ></input>
        <div className="container foi-container">
          <button onClick={mergeProfiles}>merge</button>
          <ApplicantProfileSearchView
            setShowApplicantProfileTab={null}
            setShowSearchApplicantsTab={null}
            isLoading={false}
            setIsLoading={() => {}}
            rows={rows}
            setRows={setRows}
            dispatch={dispatch}
            setSelectedApplicant={null}
            setRequestHistory={null}
            initialSearchMode="auto"
            selectionModel={selectionModel}
            onSelectionModelChange={onSelectionModelChange}
            primaryApplicantID={primaryApplicantID}
          />
        </div>
      </>
    );
  },
);

export default ApplicantProfileAdmin;
