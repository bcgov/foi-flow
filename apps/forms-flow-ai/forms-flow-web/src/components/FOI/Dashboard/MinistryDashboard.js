import React, { useEffect, useState }  from 'react';
import { DataGrid } from '@mui/x-data-grid';
import "./dashboard.scss";
import useStyles from './CustomStyle';
import { useDispatch, useSelector } from "react-redux";
import {push} from "connected-react-router";
import { fetchFOIMinistryRequestListByPage } from "../../../apiManager/services/FOI/foiRequestServices";
import { fetchFOIFullAssignedToList } from "../../../apiManager/services/FOI/foiMasterDataServices";
import { formatDate } from "../../../helper/FOI/helper";
import Loading from "../../../containers/Loading";
import { StateEnum } from '../../../constants/FOI/statusEnum';

const MinistryDashboard = ({userDetail}) => {

  const dispatch = useDispatch(); 
 
  const ministryAssignedToList = useSelector(state=> state.foiRequests.foiMinistryAssignedToList);
  const isAssignedToListLoading = useSelector(state=> state.foiRequests.isAssignedToListLoading);  

  const requestQueue = useSelector(state=> state.foiRequests.foiMinistryRequestsList);
  const isLoading = useSelector(state=> state.foiRequests.isLoading);

  const classes = useStyles();
  useEffect(()=>{
    dispatch(fetchFOIFullAssignedToList());
    dispatch(fetchFOIMinistryRequestListByPage());
  },[dispatch]);

  const defaultRowsState = {page: 0, pageSize: 10};
  const [rowsState, setRowsState] = React.useState(defaultRowsState);
  
  const defaultSortModel = [{field: 'currentState', sort: 'desc'}, {field: 'cfrduedate', sort: 'asc'}];
  const [sortModel, setSortModel] = React.useState(defaultSortModel);
  let serverSortModel;
  const [filterModel, setFilterModel] = React.useState({
    fields: ['applicantcategory', 'requestType', 'idNumber', 'currentState', 'assignedTo'],
    keyword: null 
  });
  const [requestFilter, setRequestFilter] = useState("All");

  useEffect(() => {
    serverSortModel = updateSortModel();
    // page+1 here, because initial page value is 0 for mui-data-grid
    dispatch(fetchFOIMinistryRequestListByPage(rowsState.page+1, rowsState.pageSize, serverSortModel, filterModel.fields, filterModel.keyword, requestFilter, userDetail.preferred_username));
  }, [rowsState, sortModel, filterModel, requestFilter]);

  // update sortModel for records due, ldd & assignedTo
  const updateSortModel = (() => {
    let smodel = JSON.parse(JSON.stringify(sortModel));
    if(smodel) {
      smodel.map( (row) => {
        if(row.field === 'CFRDueDateValue' || row.field === 'DueDateValue')
          row.field = 'cfrduedate';
        if(row.field === 'assignedToName')
          row.field = 'assignedministryperson';
      });
    }

    return smodel;
  });

  function getAssigneeValue(row) {
    const groupName = row.assignedministrygroup ? row.assignedministrygroup : "Unassigned";
    const assignedTo = row.assignedministryperson ? row.assignedministryperson : groupName;    
    if (ministryAssignedToList.length > 0) {
      const assigneeDetails = ministryAssignedToList.find(assigneeGroup => assigneeGroup.name === groupName);
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

  function getRecordsDue(params) {
    let receivedDateString = params.row.cfrduedate;
    const currentStatus = params.row.currentState;
    if (currentStatus.toLowerCase() === StateEnum.onhold.name.toLowerCase()) { 
      return "N/A"
    }
    else {
      return formatDate(receivedDateString, 'yyyy MMM, dd');
    }
        
  }

  function getLDD(params) {
    let receivedDateString = params.row.duedate;
    const currentStatus = params.row.currentState;
    if (currentStatus.toLowerCase() === StateEnum.onhold.name.toLowerCase()) {
      return "N/A"
    }
    else {
      return formatDate(receivedDateString, 'yyyy MMM, dd'); 
    } 
       
  }

  const columns = React.useRef([
    { 
      field: 'idNumber', 
      headerName: 'ID NUMBER',
      width: 150, 
      headerAlign: 'left',      
    },
    { 
      field: 'applicantcategory', 
      headerName: 'APPLICANT TYPE',  
      width: 180, 
      headerAlign: 'left'    
    },
    { 
      field: 'requestType', 
      headerName: 'REQUEST TYPE',  
      width: 150, 
      headerAlign: 'left'       
    },
    
    { field: 'currentState', 
      headerName: 'REQUEST STATE',  
      width: 180, 
      headerAlign: 'left'      
    },    
    {      
      field: 'assignedToName',
      headerName: 'ASSIGNEE',
      width: 180,
      headerAlign: 'left',
    },
    { 
      field: 'CFRDueDateValue', 
      headerName: 'RECORDS DUE', 
      width: 150,    
      headerAlign: 'left',
      valueGetter: getRecordsDue,
    },    
    { 
      field: 'DueDateValue', 
      headerName: 'LDD', 
      width: 150,    
      headerAlign: 'left',
      valueGetter: getLDD,
    },
    { field: 'cfrduedate', headerName: '', width: 0, hide: true, renderCell:(params)=>(<span></span>)}
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
  if(data)
    return data.map(row=> ({ ...row, assignedToName: getAssigneeValue(row) }));
  else
    return data;
}

const renderReviewRequest = (e) => {
  if (e.row.ministryrequestid) {    
    dispatch(push(`/foi/ministryreview/${e.row.id}/ministryrequest/${e.row.ministryrequestid}/${e.row.currentState}`));
  }
}

     return (  
            
        <div className="container foi-container">
           
          <div className="col-sm-12 col-md-12 foi-grid-container">
            <div className="foi-dashboard-row2">
              <h3 className="foi-request-queue-text">Your FOI Request Queue</h3>
            </div>
            <> { !isLoading  && !isAssignedToListLoading  ? (<>
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
                  `super-app-theme--${params.row.currentState.toLowerCase().replace(/ +/g, "")}-${params.row.cfrstatus.toLowerCase().replace(/ +/g, "")}`
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

export default MinistryDashboard;