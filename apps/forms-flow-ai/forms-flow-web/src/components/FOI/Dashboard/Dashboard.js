import React, { useEffect, useState }  from 'react';
import { DataGrid } from '@mui/x-data-grid';
import "./dashboard.scss";
import useStyles from './CustomStyle';
import { useDispatch, useSelector } from "react-redux";
import {push} from "connected-react-router";
import { fetchFOIRequestListByPage } from "../../../apiManager/services/FOI/foiRequestServices";
import { fetchFOIFullAssignedToList } from "../../../apiManager/services/FOI/foiMasterDataServices";
import { formatDate, addBusinessDays, businessDay } from "../../../helper/FOI/helper";
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';
import Loading from "../../../containers/Loading";
import { debounce } from './utils';
import Grid from "@material-ui/core/Grid"
import Radio from "@material-ui/core/Radio"
import RadioGroup from "@material-ui/core/RadioGroup"
import TextField from "@material-ui/core/TextField"
import FormControlLabel from "@material-ui/core/FormControlLabel"
import SearchIcon from '@material-ui/icons/Search';

const Dashboard = ({userDetail}) => {
  const dispatch = useDispatch();

  const assignedToList = useSelector((state) => state.foiRequests.foiFullAssignedToList);  
  const isAssignedToListLoading = useSelector(state=> state.foiRequests.isAssignedToListLoading);

  const requestQueue = useSelector(state=> state.foiRequests.foiRequestsList);
  const isLoading = useSelector(state=> state.foiRequests.isLoading);
  
  const classes = useStyles();
  useEffect(()=>{
    dispatch(fetchFOIFullAssignedToList());
    dispatch(fetchFOIRequestListByPage());
  },[dispatch]);

  const defaultRowsState = {page: 0, pageSize: 10};
  const [rowsState, setRowsState] = React.useState(defaultRowsState);
  
  const defaultSortModel = [{ field: 'currentState', sort: 'desc' }, { field: 'receivedDateUF', sort: 'desc' }];
  const [sortModel, setSortModel] = React.useState(defaultSortModel);
  let serverSortModel;
  const [filterModel, setFilterModel] = React.useState({
    fields: ['firstName', 'lastName', 'requestType', 'idNumber', 'currentState', 'assignedTo'],
    keyword: null 
  });
  const [requestFilter, setRequestFilter] = useState("All");

  useEffect(() => {
    serverSortModel = updateSortModel();
    // page+1 here, because initial page value is 0 for mui-data-grid
    dispatch(fetchFOIRequestListByPage(rowsState.page+1, rowsState.pageSize, serverSortModel, filterModel.fields, filterModel.keyword, requestFilter, userDetail.preferred_username));
  }, [rowsState, sortModel, filterModel, requestFilter]);

  function getFullName(params) {    
    return `${params.row.lastName || ''}, ${
      params.row.firstName || ''
    }`;
  }

  // update sortModel for applicantName & assignedTo
  const updateSortModel = (() => {
    let smodel = JSON.parse(JSON.stringify(sortModel));
    if(smodel) {
      smodel.map( (row) => {
        if(row.field === 'assignedToName')
          row.field = 'assignedTo';
      });

      let field = smodel[0]?.field;
      let order = smodel[0]?.sort;
      if(field == 'applicantName') {
        smodel.shift();
        smodel.unshift({field: 'lastName', sort: order},{field: 'firstName', sort: order})
      }
    }

    return smodel;
  });

  function getAssigneeValue(row) {
    const groupName = row.assignedGroup ? row.assignedGroup : "Unassigned";
    const assignedTo = row.assignedTo ? row.assignedTo : groupName;
    if (assignedToList && assignedToList.length > 0) {
      const assigneeDetails = assignedToList.find(assigneeGroup => assigneeGroup.name === groupName);
      const assignee = assigneeDetails && assigneeDetails.members && assigneeDetails.members.find(_assignee => _assignee.username === assignedTo);
      if (groupName === assignedTo) {
        return assignedTo;
      }
      else {        
        return  assignee !== undefined ? `${assignee.lastname}, ${assignee.firstname}`: "invalid user";
      }
    }
    else {
      return assignedTo;
    }
  }

  function getReceivedDate(params) {
    let receivedDateString = params.row.receivedDateUF;    
    const dateString = receivedDateString ? receivedDateString.substring(0,10): "";
    receivedDateString = receivedDateString ? new Date(receivedDateString): "";    

    if (receivedDateString !== "" && ((receivedDateString.getHours() > 16 || (receivedDateString.getHours() === 16 && receivedDateString.getMinutes() > 30)) || !businessDay(dateString))) {    
        receivedDateString = addBusinessDays(receivedDateString, 1);     
    }    
    return formatDate(receivedDateString, "MMM dd yyyy");    
  }
   
  const columns = React.useRef([    
    {
      field: 'applicantName',
      headerName: 'APPLICANT NAME',
      width: 170,      
      headerAlign: 'left',
      valueGetter: getFullName,     
    },
    { 
      field: 'requestType', 
      headerName: 'REQUEST TYPE',  
      width: 150, 
      headerAlign: 'left' 
    },
    { field: 'idNumber', 
      headerName: 'ID NUMBER',
      width: 150,
      headerAlign: 'left',
    },
    { 
      field: 'currentState', 
      headerName: 'CURRENT STATE',      
      headerAlign: 'left',
      width: 180
    },
    {      
      field: 'assignedToName',
      headerName: 'ASSIGNED TO',
      width: 180,
      headerAlign: 'left',
      
    },
    { field: 'receivedDate', headerName: 'RECEIVED DATE', 
      width: 180,    
      headerAlign: 'left',
      valueGetter: getReceivedDate,
    },    
    { field: 'xgov', headerName: 'XGOV', 
      width: 100,      
      headerAlign: 'left',
    },
    { 
      field: 'receivedDateUF', headerName: '', width: 0, hide: true, renderCell:(params)=>(<span></span>)}
  ]);  
      
  const requestFilterChange = (e) => {
    setRowsState(defaultRowsState);
    setRequestFilter(e.target.value);
  }

  const setSearch = debounce((e) => {
    var keyword = e.target.value;
    setFilterModel((prev) => ({ ...prev, keyword}));
    setRowsState(defaultRowsState);
  }, 500);

  const updateAssigneeName = (data) => {  
    return data.map(row=> ({ ...row, assignedToName: getAssigneeValue(row) }));
  }
 
  const renderReviewRequest = (e) => {
    if (e.row.ministryrequestid) {
      dispatch(push(`/foi/foirequests/${e.row.id}/ministryrequest/${e.row.ministryrequestid}`));
    }
    else {
      dispatch(push(`/foi/reviewrequest/${e.row.id}`));
    }
  }
  
  const addRequest = (e) => {
    dispatch(push(`/foi/addrequest`));
  }

    return (            
      <div className="container foi-container">          
        <Grid
          container
          direction="row"
          className="foi-grid-container"
          spacing={1}
        >
          <Grid
            item
            container
            direction="row"
            alignItems="center"
            xs={12} 
            className="foi-dashboard-row2" 
          >
            <Grid item lg={6} xs={12}>
              <h3 className="foi-request-queue-text">Your FOI Request Queue</h3>
            </Grid>
            <Grid item container lg={6} xs={12} justifyContent="flex-end">
              <button type="button" className="btn foi-btn-create" onClick={addRequest}>
                {FOI_COMPONENT_CONSTANTS.ADD_REQUEST}
              </button>
            </Grid>
          </Grid>
          <> { !isLoading && !isAssignedToListLoading ? (<>
          <Grid 
            item 
            container
            alignItems="center"
            xs={12}
          >
            <Grid item lg={6} xs={12} className="form-group has-search">
              <SearchIcon className="form-control-search"/>
              <input type="text" className="form-control" placeholder="Search . . ." onChange={setSearch} />
            </Grid>

            <Grid item container lg={6} xs={12} justifyContent="flex-end">
              <RadioGroup
                name="controlled-radio-buttons-group"
                value={requestFilter}
                onChange={requestFilterChange}
                row
              >
                <FormControlLabel 
                  className="form-control-label" 
                  value="myRequests"
                  control={<Radio className="mui-radio" color="primary"/>}
                  label="My Requests" 
                />
                <FormControlLabel
                  className="form-control-label" 
                  value="watchingRequests"
                  control={<Radio className="mui-radio" color="primary"/>}
                  label="Watching Requests" 
                />
                <FormControlLabel
                  className="form-control-label" 
                  value="All"
                  control={<Radio className="mui-radio" color="primary"/>}
                  label="My Team Requests" 
                />
              </RadioGroup>
            </Grid>     
          </Grid>
          <Grid item xs={12} style={{ height: 450 }} className={classes.root}>
            <DataGrid 
              className="foi-data-grid"
              getRowId={(row) => row.idNumber}
              rows={updateAssigneeName(requestQueue.data)} 
              columns={columns.current}                
              rowHeight={30}
              headerHeight={50}
              rowCount = {requestQueue.meta.total}
              pageSize={rowsState.pageSize}
              rowsPerPageOptions={[10]}
              hideFooterSelectedRowCount={true}
              disableColumnMenu={true}

              pagination
              paginationMode='server'
              onPageChange={(page) => setRowsState((prev) => ({ ...prev, page }))}
              onPageSizeChange={(pageSize) =>
                setRowsState((prev) => ({ ...prev, pageSize }))
              }

              sortingOrder={['desc', 'asc']}
              sortModel={sortModel}
              sortingMode={'server'}
              onSortModelChange={(model) => setSortModel(model)}
              getRowClassName={(params) =>
                `super-app-theme--${params.row.currentState.toLowerCase().replace(/ +/g, "")}`
              }
              onRowClick={renderReviewRequest}
              loading={isLoading}
              />
          </Grid> </>):<Loading/> }
          </>
        </Grid>
      </div>      
    );
};

export default Dashboard;