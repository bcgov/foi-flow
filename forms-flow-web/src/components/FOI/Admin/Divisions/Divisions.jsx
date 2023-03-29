import React, { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { push } from "connected-react-router";
import SearchBar from "./SearchBar";
import Button from "@mui/material/Button";
import CreateDivisionModal from "./CreateDivisionModal";
import DisableDivisionModal from "./DisableDivisionModal";
import EditDivisionModal from "./EditDivisionModal";
import IconButton from "@mui/material/IconButton";
import Stack from "@mui/material/Stack";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid";
import DeleteIcon from "@material-ui/icons/Delete";
import EditIcon from "@material-ui/icons/Edit";
import { DataGrid } from "@mui/x-data-grid";

import {
  fetchProgramAreaDivisions,
  createProgramAreaDivision,
  editProgramAreaDivision,
  disableProgramAreaDivision,
} from "../../../../apiManager/services/FOI/foiAdminServices";

import "./divisions.scss";

const Divisions = () => {
  const [searchResults, setSearchResults] = useState(null);
  const [selectedDivision, setSelectedDivision] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDisableModal, setShowDisableModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const dispatch = useDispatch();

  let divisions = useSelector(
    (state) => state.foiRequests.foiProgramAreaDivisionList
  );

  useEffect(async () => {
    await Promise.all([dispatch(fetchProgramAreaDivisions())]);
  }, []);

  const createDivision = async (data) => {
    console.log(data);
    await Promise.all([
      dispatch(
        createProgramAreaDivision({
          name: data.name,
          programareaid: data.programareaid,
        })
      ),
    ]);
  };

  const editDivision = async (data) => {
    console.log(data);
    await Promise.all([
      dispatch(
        editProgramAreaDivision(
          {
            name: data.name,
            programareaid: data.programareaid,
            sortorder: data.sortorder,
          },
          data.divisionid
        )
      ),
    ]);
  };

  const disableDivision = async (data) => {
    console.log(data);
    await Promise.all([dispatch(disableProgramAreaDivision(data.divisionid))]);
  };

  const openCreateDivisionModal = () => {
    setShowCreateModal(true);
  };

  const openDisableDivisionModal = (data) => {
    setSelectedDivision(data);
    setShowDisableModal(true);
  };

  const openEditDivisionModal = (data) => {
    setSelectedDivision(data);
    setShowEditModal(true);
  };

  const columns = [
    {
      field: "divisionid",
      headerName: "ID",
      width: 75,
    },
    {
      field: "name",
      headerName: "Division",
      flex: 1,
    },
    {
      field: "programarea",
      headerName: "Program Area",
      flex: 1,
    },
    {
      field: "areabcgovcode",
      headerName: "Code",
      width: 75,
    },
    {
      field: "sortorder",
      headerName: "Sort Order",
      width: 100,
    },
    {
      field: "action",
      headerName: "Action",
      renderHeader: () => <></>,
      width: 100,
      align: "right",
      sortable: false,
      renderCell: (params) => (
        <Stack direction="row" spacing={0}>
          <IconButton onClick={() => openEditDivisionModal(params.row)}>
            <EditIcon />
          </IconButton>
          <IconButton onClick={() => openDisableDivisionModal(params.row)}>
            <DeleteIcon />
          </IconButton>
        </Stack>
      ),
    },
  ];

  return (
    <div className="container divisions-container">
      <Grid
        container
        direction="row"
        className="divisions-grid-container"
        spacing={1}
      >
        <Grid item xs={12}>
          <Typography variant="h4" component="h1" className="divisions-title">
            Manage Divisions
          </Typography>
        </Grid>
        <Grid item xs={12}>
          <Button variant="text" onClick={() => dispatch(push(`/admin`))}>Back to Admin</Button>
        </Grid>
        <Grid
          item
          container
          xs={12}
          spacing={3}
          alignItems="center"
          sx={{
            paddingBottom: "15px",
          }}
        >
          <Grid item xs>
            <SearchBar
              autocompleteOptions={divisions
                .map((division) => division.name)
                .filter((value, index, self) => self.indexOf(value) === index)}
              items={divisions}
              setSearchResults={setSearchResults}
            />
          </Grid>
          <Grid item xs={6} sm={4} md={2} alignItems="right">
            <Box display="flex" justifyContent="flex-end">
              <Button
                size="small"
                variant="contained"
                onClick={() => openCreateDivisionModal()}
              >
                New Division
              </Button>
            </Box>
          </Grid>
        </Grid>
        <Grid item xs={12} className="divisions-data-grid-container">
          <DataGrid
            autoHeight
            className="divisions-data-grid"
            getRowId={(row) => row.divisionid}
            rows={
              searchResults && searchResults.length > 0
                ? searchResults
                : divisions
            }
            columns={columns}
            rowHeight={30}
            headerHeight={50}
            hideFooterSelectedRowCount={true}
            disableColumnMenu={true}
            pagination
          />
        </Grid>
      </Grid>
      <CreateDivisionModal
        divisions={divisions}
        saveDivision={createDivision}
        showModal={showCreateModal}
        closeModal={() => setShowCreateModal(false)}
      />
      <DisableDivisionModal
        initialDivision={selectedDivision}
        disableDivision={disableDivision}
        showModal={showDisableModal}
        closeModal={() => setShowDisableModal(false)}
      />
      <EditDivisionModal
        initialDivision={selectedDivision}
        divisions={divisions}
        saveDivision={editDivision}
        showModal={showEditModal}
        closeModal={() => setShowEditModal(false)}
      />
    </div>
  );
};

export default Divisions;
