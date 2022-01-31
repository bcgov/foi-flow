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
  
  const defaultSortModel = [{ field: 'idNumber', sort: 'asc' }];
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
    return formatDate(receivedDateString, 'yyyy MMM, dd');    
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

  const setSearch = (e) => {
    var keyword = e.target.value;
    setRowsState(defaultRowsState);
    setFilterModel((prev) => ({ ...prev, keyword}));
  }

  const updateAssigneeName = (data) => {  
    return data.map(row=> ({ ...row, assignedToName: getAssigneeValue(row) }));
  }
 

  const renderReviewRequest = (e) => {
    if (e.row.ministryrequestid) {
      dispatch(push(`/foi/foirequests/${e.row.id}/ministryrequest/${e.row.ministryrequestid}/${e.row.currentState}`));
    }
    else {
      dispatch(push(`/foi/reviewrequest/${e.row.id}/${e.row.currentState}`));
    }
  }
  const addRequest = (e) => {
    dispatch(push(`/foi/addrequest`));
  }

     return (  
            
        <div className="container foi-container">
           
          <div className="col-sm-12 col-md-12 foi-grid-container">
            <div className="foi-dashboard-row2">
              <h3 className="foi-request-queue-text">Your FOI Request Queue</h3>
              <button type="button" className="btn foi-btn-create" onClick={addRequest} >{FOI_COMPONENT_CONSTANTS.ADD_REQUEST}</button>
            </div>
            <> { !isLoading && !isAssignedToListLoading ? (<>
            <div className="foi-dashboard-row2">             
              <div className="form-group has-search">
                <span className="fa fa-search form-control-search"></span>
                <input type="text" className="form-control" placeholder="Search . . ." onChange={setSearch} />               
              </div>
             
              <div className="foi-request-type">
                <input className="foi-general-radio" type="radio" value="myRequests" name="requestFilter" onChange={requestFilterChange} /> My Requests
                <input className="foi-personal-radio" type="radio" value="watchingRequests" name="requestFilter" onChange={requestFilterChange} /> Watching Requests
                <input className="foi-all-radio" type="radio" value="All" name="requestFilter" onChange={requestFilterChange} defaultChecked  /> My Team Requests            
              </div>            
              
            </div>
            <div style={{ height: 450 }} className={classes.root}>
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
            </div> </>):<Loading/> }
            </>
          </div>
        </div> 
      
    );
};

export default Dashboard;