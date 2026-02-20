import { useState, useEffect } from "react";
import Stack from "@mui/material/Stack";
import Paper from "@mui/material/Paper";
import Box from "@mui/material/Box";
import SearchIcon from "@material-ui/icons/Search";
import InputAdornment from "@mui/material/InputAdornment";
import InputBase from "@mui/material/InputBase";
import Grid from "@mui/material/Grid";
import IconButton from "@mui/material/IconButton";
import { ClickableChip } from "../Dashboard/utils";
import { DataGrid } from "@mui/x-data-grid";
import { toast } from "react-toastify";

import {
  fetchApplicantProfileByKeyword,
  fetchApplicantRequests,
} from "../../../apiManager/services/FOI/foiApplicantProfileService";

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
  const [searchText, setSearchText] = useState("");
  const [searchMode, setSearchMode] = useState(initialSearchMode);

 useEffect(() => {
    if (searchText && searchText.length > 0) setSearchMode("manual")
  }, [searchText])

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
      field: "primaryPhone",
      headerName: "PRIMARY PHONE",
      flex: 1,
    },
  ];

  const onSearchChange = (e) => {
    if (searchMode === "auto") {
      setSearchText(e.target.value);
    }
  };

  const search = (rows) => {
    return rows.filter(
      (r) =>
        r.firstName.toLowerCase().indexOf(searchText.toLowerCase()) > -1 ||
        r.middleName?.toLowerCase().indexOf(searchText.toLowerCase()) > -1 ||
        r.lastName.toLowerCase().indexOf(searchText.toLowerCase()) > -1 ||
        r.birthDate?.toLowerCase().indexOf(searchText.toLowerCase()) > -1 ||
        r.email?.toLowerCase().indexOf(searchText.toLowerCase()) > -1 ||
        r.primaryPhone?.toLowerCase().indexOf(searchText.toLowerCase()) > -1,
    );
  };

  const onSearchEnter = (e) => {
    if (searchMode === "manual" && e.key === "Enter") {
      const keywordJSON = createKeywordJSON(e.target.value);
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
  };

  const createKeywordJSON = (keyword) => {
    const keywordJSON = {
      keywords: {},
    };
    const mobileNumberRegex =
      /^(\+\d{1,3}[-.●]?)?\(?\d{3}\)?[-.●]?\d{3}[-.●]?\d{4}$/;
    const stringRegex = /^[A-Za-z0-9\s.@!#$%^&*()\-_=+[\]{};:'",<.>/?\\|]+$/;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const isValidEmail = emailRegex.test(keyword);
    const isValidNumber = mobileNumberRegex.test(keyword);
    const isValidString = stringRegex.test(keyword);
    if (isValidEmail) {
      keywordJSON.keywords["email"] = keyword;
    }
    if (isValidNumber) {
      keywordJSON.keywords["homephone"] = keyword;
      keywordJSON.keywords["workphone"] = keyword;
      keywordJSON.keywords["workphone2"] = keyword;
      keywordJSON.keywords["mobilephone"] = keyword;
    }
    if (isValidString) {
      keywordJSON.keywords["firstname"] = keyword;
      keywordJSON.keywords["lastname"] = keyword;
      keywordJSON.keywords["email"] = keyword;
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
            id="filter"
            placeholder="Search..."
            defaultValue={searchText}
            onChange={onSearchChange}
            onKeyDown={onSearchEnter}
            sx={{
              color: "#38598A",
            }}
            startAdornment={
              <InputAdornment position="start">
                <IconButton sx={{ color: "#38598A" }}>
                  <span className="hideContent">Search</span>
                  <SearchIcon />
                </IconButton>
              </InputAdornment>
            }
            fullWidth
          />
        </Grid>
        <Grid
          item
          container
          alignItems="flex-start"
          justifyContent="center"
          xs={2.5}
          minWidth="100px"
        >
          <Stack direction="row" sx={{ overflowX: "hidden" }} spacing={1}>
            <ClickableChip
              label={"MANUAL"}
              color="primary"
              size="small"
              onClick={() => setSearchMode("manual")}
              clicked={searchMode === "manual"}
            />
            <ClickableChip
              label={"AUTO"}
              color="primary"
              size="small"
              onClick={() => setSearchMode("auto")}
              clicked={searchMode === "auto"}
            />
          </Stack>
        </Grid>
      </Paper>
      <Box sx={{ height: "calc(100% - 100px)", width: "100%" }}>
        <DataGrid
          className="foi-data-grid foi-applicant-data-grid"
          rows={search(rows)}
          columns={columns}
          hideFooter={true}
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
