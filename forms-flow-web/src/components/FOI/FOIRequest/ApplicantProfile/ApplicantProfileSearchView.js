import { useState, useEffect } from "react";
import Stack from "@mui/material/Stack";
import Paper from "@mui/material/Paper";
import Box from "@mui/material/Box";
import SearchIcon from "@material-ui/icons/Search";
import InputAdornment from "@mui/material/InputAdornment";
import InputBase from "@mui/material/InputBase";
import Grid from "@mui/material/Grid";
import IconButton from "@mui/material/IconButton";
import { ClickableChip } from "../../Dashboard/utils";
import { DataGrid } from "@mui/x-data-grid";
import { toast } from "react-toastify";
import './applicantprofile.scss';
import {
  fetchApplicantProfileByKeyword,
  fetchApplicantRequests,
} from "../../../../apiManager/services/FOI/foiApplicantProfileService";
import { Button } from "@mui/material";

export const ApplicantProfileSearchView = ({
  setShowApplicantProfileTab,
  setShowSearchApplicantsTab,
  isLoading,
  setIsLoading,
  rows,
  setRows,
  dispatch,
  setSelectedApplicant,
  setRequestHistory,
  initialSearchMode = "auto"
}) => {
  const [firstNameSearchText, setFirstNameSearchText] = useState("")
  const [lastNameSearchText, setLastNameSearchText] = useState("")
  const [emailSearchText, setEmailSearchText] = useState("")

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
    }
  ];

  const onFirstNameChange = (e) => {
    setFirstNameSearchText(e.target.value);
  }

  const onLastNameChange = (e) => {
    setLastNameSearchText(e.target.value);
  }

  const onEmailChange = (e) => {
    setEmailSearchText(e.target.value);
  }

  const search = (rows) => {
    return rows.filter(
      (r) =>
        r.firstName?.toLowerCase().indexOf(firstNameSearchText.toLowerCase()) > -1 ||
        r.lastName?.toLowerCase().indexOf(lastNameSearchText.toLowerCase()) > -1 ||
        r.email?.toLowerCase().indexOf(emailSearchText.toLowerCase()) > -1 
    );
  };

  const searchKeywords = () => {
    const keywordJSON = createKeywordsJSON();
      setIsLoading(true);
      dispatch(
        fetchApplicantProfileByKeyword(keywordJSON, (err, res) => {
          if (!err) {
            setRows(res);
            setIsLoading(false);
          } else {
            toast.error(
              "Temporarily unable to fetch applicant profiles. Please try again in a few minutes.",
              {
                position: "top-right",
                autoClose: 3000,
                hideProgressBar: true,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
                progress: undefined,
              },
            );
          }
        }),
      );
  }

  const onSearchEnter = (e) => {
    if (e.key === "Enter") {
      searchKeywords()
    }
  };
  const createKeywordsJSON = () => {
    const keywordJSON = {
      keywords: {},
    };
    const stringRegex = /^[A-Za-z0-9\s.@!#$%^&*()\-_=+[\]{};:'",<.>/?\\|]+$/;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const isValidEmail = stringRegex.test(emailSearchText);
    const isValidFirstName = stringRegex.test(firstNameSearchText);
    const isValidLastName = stringRegex.test(lastNameSearchText);
    if (isValidEmail) {
      keywordJSON.keywords["email"] = emailSearchText;
    }
    if (isValidFirstName) {
      keywordJSON.keywords["firstname"] = firstNameSearchText;
    }
    if (isValidLastName) {
      keywordJSON.keywords["lastname"] = lastNameSearchText;
    }
    return keywordJSON;
  };

  const selectApplicantRow = (e) => {
    const applicant = e.row;
    const applicantID = applicant.foiRequestApplicantID;
    dispatch(
      fetchApplicantRequests(applicantID, (err, res) => {
        setSelectedApplicant(applicant);
        setRequestHistory(res);
        setIsLoading(false);
        setShowApplicantProfileTab(true);
        setShowSearchApplicantsTab(false);
      }),
    );
  };

  return (
    <>
      <div style={{ fontSize: "13px" }}>
        Select an applicant to view their details. Or create a new profile if
        applicant cannot be found.
      </div>
      <Paper
        component={Grid}
        sx={{
          border: "1px solid #38598A",
          color: "#38598A",
          margin: "20px 0",
        }}
        alignItems="center"
        justifyContent="center"
        direction="row"
        container
        item
        xs={12}
        elevation={0}
      >
        <Grid
          item
          container
          alignItems="center"
          direction="row"
          xs={true}
          sx={{
            borderRight: "2px solid #38598A",
            backgroundColor: "rgba(56,89,138,0.1)",
          }}
        >
          <InputBase
            id="filter-firstname"
            placeholder="First Name"
            defaultValue={firstNameSearchText}
            onChange={onFirstNameChange}
            onKeyDown={onSearchEnter}
            sx={{
              color: "#38598A",
            }}
            startAdornment={
              <InputAdornment position="start">
                <IconButton sx={{ color: "#38598A" }} onClick={() => searchKeywords()}>
                  <span className="hideContent">Search</span>
                  <SearchIcon />
                </IconButton>
              </InputAdornment>
            }
            endAdornment={
              <InputAdornment position="start">
                AND
              </InputAdornment>
            }
          />
          <InputBase
            id="filter-lastname"
            placeholder="Last Name"
            defaultValue={lastNameSearchText}
            onChange={onLastNameChange}
            onKeyDown={onSearchEnter}
            sx={{
              color: "#38598A",
            }}
            endAdornment={
              <InputAdornment position="start">
                AND
              </InputAdornment>
            }
          />
          <InputBase
            id="filter-email"
            placeholder="Email"
            defaultValue={emailSearchText}
            onChange={onEmailChange}
            onKeyDown={onSearchEnter}
            sx={{
              color: "#38598A",
            }}
          />
        </Grid>
        <button onClick={(e) => {
            e.preventDefault();
            searchKeywords()
          }} 
          className="search-button">
          Search
        </button>
      </Paper>
      <Box sx={{ height: "calc(100% - 100px)", width: "100%" }}>
        <DataGrid
          className="foi-data-grid foi-applicant-data-grid"
          rows={search(rows)}
          columns={columns}
          hideFooter={false}
          pageSizeOptions={[5]}
          rowHeight={30}
          headerHeight={50}
          loading={isLoading}
          onRowClick={selectApplicantRow}
          getRowId={(row) => row.foiRequestApplicantID}
        />
      </Box>
    </>
  );
};
