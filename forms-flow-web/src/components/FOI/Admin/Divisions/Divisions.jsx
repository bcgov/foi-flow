import React, { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { push } from "connected-react-router";
import SearchBar from "../customComponents";
import CreateDivisionModal from "./CreateDivisionModal";
import DisableDivisionModal from "./DisableDivisionModal";
import EditDivisionModal from "./EditDivisionModal";
import CreateSectionModal from "./CreateSectionModal";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import { DataGrid } from "@mui/x-data-grid";
import Grid from "@mui/material/Grid";
import IconButton from "@mui/material/IconButton";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import DeleteIcon from "@material-ui/icons/Delete";
import EditIcon from "@material-ui/icons/Edit";
import VisibilityIcon from "@material-ui/icons/Visibility";
import VisibilityOffIcon from "@material-ui/icons/VisibilityOff";
import { toast } from "react-toastify";

import {
  fetchProgramAreaDivisions,
  createProgramAreaDivision,
  editProgramAreaDivision,
  disableProgramAreaDivision,
  updateProgramAreaDivisionSelectable,
} from "../../../../apiManager/services/FOI/foiAdminServices";
import {fetchAllProgramAreasForAdmin} from "../../../../apiManager/services/FOI/foiMasterDataServices";
import "./divisions.scss";
import Loading from "../../../../containers/Loading";
import {isFoiAdmin} from "../../../../helper/FOI/helper";


const Divisions = ({userDetail}) => {
  const [searchResults, setSearchResults] = useState(null);
  const [divisionRows, setDivisionRows] = useState([]);
  const [selectedDivision, setSelectedDivision] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showCreateSectionModal, setShowCreateSectionModal] = useState(false);
  const [showDisableModal, setShowDisableModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const dispatch = useDispatch();

  const userGroups = userDetail?.groups?.map(group => group.slice(1));
  let isAdmin = isFoiAdmin(userGroups);

  let divisions = useSelector(
    (state) => state.foiRequests.foiProgramAreaDivisionList
  );

  useEffect(() => {
    setDivisionRows(divisions || []);
  }, [divisions]);

  useEffect(async () => {
    if(isAdmin){
      await Promise.all([dispatch(fetchProgramAreaDivisions()),
        dispatch(fetchAllProgramAreasForAdmin())]);
    }
  }, []);

  const createDivision = async (data) => {
    await Promise.all([
      dispatch(
        createProgramAreaDivision({
          name: data.name,
          programareaid: data.programareaid,
          issection: data.issection,
          parentid: data.parentid,
          specifictopersonalrequests: data.specifictopersonalrequests
        },
        (err, res) => {            
            if (!err && res) {
              toast.success(res.message?res.message : "Division created successfully.", {
                position: "top-right",
                autoClose: 3000,
                hideProgressBar: true,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
                progress: undefined,
              });
            } else {
              toast.error(
                "Temporarily unable to create division. Please try again in a few minutes.",
                {
                  position: "top-right",
                  autoClose: 3000,
                  hideProgressBar: true,
                  closeOnClick: true,
                  pauseOnHover: true,
                  draggable: true,
                  progress: undefined,
                }
              );
            }
          }
        )
      ),
    ]);
  };

  const editDivision = async (data) => {
    await Promise.all([
      dispatch(
        editProgramAreaDivision(
          {
            name: data.name,
            programareaid: data.programareaid,
            sortorder: data.sortorder,
            issection: data.issection,
            parentid: data.parentid,
            specifictopersonalrequests: data.specifictopersonalrequests
          },
          data.divisionid,
          (err, res) => {            
            if (!err && res) {
              toast.success(res.message?res.message : "Division updated successfully.", {
                position: "top-right",
                autoClose: 3000,
                hideProgressBar: true,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
                progress: undefined,
              });
            } else {
              toast.error(
                "Temporarily unable to update division. Please try again in a few minutes.",
                {
                  position: "top-right",
                  autoClose: 3000,
                  hideProgressBar: true,
                  closeOnClick: true,
                  pauseOnHover: true,
                  draggable: true,
                  progress: undefined,
                }
              );
            }
          }
        )
      ),
    ]);
  };

  const disableDivision = async (data) => {
    await Promise.all([dispatch(disableProgramAreaDivision(data.divisionid ,
      (err, res) => {            
        if (!err && res) {
          toast.success(res.message?res.message : "Division disabled successfully.", {
            position: "top-right",
            autoClose: 3000,
            hideProgressBar: true,
            closeOnClick: true,
            pauseOnHover: true,
            draggable: true,
            progress: undefined,
          });
        } else {
          toast.error(
            "Unable to disable division. Please try again in a few minutes and ensure that the division is not associated to any FOI Request records or sections.",
            {
              position: "top-right",
              autoClose: 4500,
              hideProgressBar: true,
              closeOnClick: true,
              pauseOnHover: true,
              draggable: true,
              progress: undefined,
            }
          );
        }
      }))
    ]);
  };

  const toggleDivisionSelectable = async (data) => {
    const newValue = !data.isselectable;

    await Promise.all([
      dispatch(
        updateProgramAreaDivisionSelectable(
          data.divisionid,
          newValue,
          (err, res) => {
            if (!err && res) {
              const updateSelectableRow = (row) =>
                row.divisionid === data.divisionid
                  ? { ...row, isselectable: newValue }
                  : row;

              setDivisionRows((rows) =>
                rows.map(updateSelectableRow)
              );

              setSearchResults((rows) =>
                rows ? rows.map(updateSelectableRow) : rows
              );

              toast.success(
                newValue
                  ? "Division is now visible to ministry users."
                  : "Division is now hidden from ministry users.",
                {
                  position: "top-right",
                  autoClose: 3000,
                  hideProgressBar: true,
                  closeOnClick: true,
                  pauseOnHover: true,
                  draggable: true,
                  progress: undefined,
                }
              );
            } else {
              toast.error(
                "Unable to update division visibility. Please try again.",
                {
                  position: "top-right",
                  autoClose: 3000,
                  hideProgressBar: true,
                  closeOnClick: true,
                  pauseOnHover: true,
                  draggable: true,
                  progress: undefined,
                }
              );
            }
          }
        )
      ),
    ]);
  };
  const openCreateDivisionModal = () => {
    setShowCreateModal(true);
  };

  const openCreateSectionModal = () => {
    setShowCreateSectionModal(true)
  }

  const openDisableDivisionModal = (data) => {
    setSelectedDivision(data);
    setShowDisableModal(true);
  };

  const openEditDivisionModal = (data) => {
    setSelectedDivision(data);
    setShowEditModal(true);
  };

  const filterParentDivisions = (divisionObj, divisionsArr, operation) => {
    let filteredDivisions = divisionsArr.filter(division => !division.issection);
    if(operation === "EDIT") {
      filteredDivisions = filteredDivisions.filter(division => division.divisionid !== divisionObj.divisionid);
    }
    if (divisionObj.programareaid && divisionObj.specifictopersonalrequests) {
      return filteredDivisions.filter(division => division.programareaid === divisionObj.programareaid && division.specifictopersonalrequests);
    } 
    if (divisionObj.programareaid && !divisionObj.specifictopersonalrequests) {
      return filteredDivisions.filter(division => division.programareaid === divisionObj.programareaid && !division.specifictopersonalrequests);
    }
    return filteredDivisions;
  }

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
      field: "issection",
      headerName: "Section?",
      width: 100,
    },
    {
      field: "parentid",
      headerName: "Parent Division",
      width: 150,
      align: "center",
      renderCell: (params) => <>{params.value ? params.value : "-"}</>,
    },
    {
      field: "specifictopersonalrequests",
      headerName: "Personal Requests",
      width: 150,
      align: "center",
    },
    {
      field: "isselectable",
      headerName: "Visible?",
      width: 100,
      align: "center",
      renderCell: (params) => <>{params.row.issection || params.row.type ? "-" : params.value ? "Yes" : "No"}</>,
    },
    {
      field: "sortorder",
      headerName: "Sort Order",
      width: 100,
      align: "center",
      renderCell: (params) => <>{params.value ? params.value : "-"}</>,
    },
    {
      field: "action",
      headerName: "Action",
      renderHeader: () => <></>,
      width: 140,
      align: "right",
      sortable: false,
      renderCell: (params) => (
        <Stack direction="row" spacing={0}>
          <IconButton onClick={() => openEditDivisionModal(params.row)}>
            <EditIcon />
          </IconButton>

          {!params.row.issection && !params.row.type && (
            <IconButton
              onClick={() => toggleDivisionSelectable(params.row)}
              title={
                params.row.isselectable
                  ? "Hide from ministry users"
                  : "Show to ministry users"
              }
            >
              {params.row.isselectable ? (
                <VisibilityIcon />
              ) : (
                <VisibilityOffIcon />
              )}
            </IconButton>
          )}

          <IconButton onClick={() => openDisableDivisionModal(params.row)}>
            <DeleteIcon />
          </IconButton>
        </Stack>
      ),
    },
  ];

  return (isAdmin ?
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
          <Button variant="text" onClick={() => dispatch(push(`/foi/admin`))}>
            Back to Admin
          </Button>
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
              // autocompleteOptions={divisions
              //   .map((division) => division.name)
              //   .filter((value, index, self) => self.indexOf(value) === index)}
              items={divisionRows}
              setSearchResults={setSearchResults}
            />
          </Grid>
          <Grid item xs={6} sm={4} md={3}>
            <Box display="flex" justifyContent="flex-end">
              <Button
                style={{marginRight: "10px"}}
                size="small"
                variant="contained"
                onClick={() => openCreateDivisionModal()}
              >
                New Division
              </Button>
              <Button
                size="small"
                variant="contained"
                onClick={() => (openCreateSectionModal())}
              >
                New Section
              </Button>
            </Box>
          </Grid>
        </Grid>
        <Grid item xs={12} className="divisions-data-grid-container">
          <DataGrid
            autoHeight
            className="divisions-data-grid"
            getRowId={(row) => row.divisionid}
            rows={searchResults ? searchResults : divisionRows}
            columns={columns}
            rowHeight={30}
            headerHeight={50}
            hideFooterSelectedRowCount={true}
            disableColumnMenu={true}
            pagination
            components={{
              NoRowsOverlay: () => (
                <Stack
                  height="100%"
                  alignItems="center"
                  justifyContent="center"
                >
                  No divisions found.
                </Stack>
              ),
            }}
          />
        </Grid>
      </Grid>
      <CreateDivisionModal
        divisions={divisions}
        saveDivision={createDivision}
        showModal={showCreateModal}
        closeModal={() => setShowCreateModal(false)}
      />
      <CreateSectionModal
        divisions={divisions}
        filterParentDivisions={filterParentDivisions}
        saveDivision={createDivision}
        showModal={showCreateSectionModal}
        closeModal={() => setShowCreateSectionModal(false)}
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
        filterParentDivisions={filterParentDivisions}
        saveDivision={editDivision}
        showModal={showEditModal}
        closeModal={() => setShowEditModal(false)}
      />
    </div>: 
    <Loading />
  );
};

export default Divisions;
