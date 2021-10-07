import React, { useEffect, useState }  from 'react';
import { DataGrid } from '@material-ui/data-grid';
import "./dashboard.scss";
import useStyles from './CustomStyle';
import { useDispatch, useSelector } from "react-redux";
import {push} from "connected-react-router";
import { fetchFOIRequestList, fetchFOIFullAssignedToList } from "../../../apiManager/services/FOI/foiRequestServices";
import { formatDate, addBusinessDays, businessDay } from "../../../helper/FOI/helper";
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';
import Loading from "../../../containers/Loading";

const Dashboard = React.memo(() => {


  const dispatch = useDispatch();
  const rows = useSelector(state=> state.foiRequests.foiRequestsList);
  const isLoading = useSelector(state=> state.foiRequests.isLoading);
  const [requestType, setRequestType] = useState("All");
  const [searchText, setSearchText] = useState("");
  const classes = useStyles();
  useEffect(()=>{
    dispatch(fetchFOIFullAssignedToList());
    dispatch(fetchFOIRequestList());
  },[dispatch]);

  const assignedToList = useSelector((state) => state.foiRequests.foiFullAssignedToList);  
  const isAssignedToListLoading = useSelector(state=> state.foiRequests.isAssignedToListLoading);

  function getFullName(params) {    
    return `${params.row.lastName || ''}, ${
      params.row.firstName || ''
    }`;
  }

  function getAssigneeValue(row) {
    const groupName = row.assignedGroup ? row.assignedGroup : "Unassigned";
    const assignedTo = row.assignedTo ? row.assignedTo : groupName;
    if (assignedToList.length > 0) {
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
    let receivedDateString = params.getValue(params.id, 'receivedDateUF');    
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
      headerName: 'CURRENT STATUS',      
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
    
    const [sortModel, setSortModel]= useState([
      {
        field: 'currentState',
        sort: 'desc',
      },
      {
        field: 'receivedDateUF',
        sort: 'desc',
      },   
    ]);

const requestTypeChange = (e) => { 
  setRequestType(e.target.value);
  
}

const setSearch = (e) => {
  setSearchText(e.target.value);
}

const search = (data) => {   
  var _rt =  (requestType === "general" || requestType === "personal") ? requestType : null ;
  const updatedRows = data.map(row=> ({ ...row, assignedToName: getAssigneeValue(row) }));
  return updatedRows.filter(row => ((row.firstName.toLowerCase().indexOf(searchText.toLowerCase()) > -1) || 
  (row.lastName.toLowerCase().indexOf(searchText.toLowerCase()) > -1) ||
  row.idNumber.toLowerCase().indexOf(searchText.toLowerCase()) > -1  ||
  row.currentState.toLowerCase().indexOf(searchText.toLowerCase()) > -1 ||
  row.requestType.toLowerCase().indexOf(searchText.toLowerCase()) > -1 ||
  (row.assignedTo && row.assignedTo.toLowerCase().indexOf(searchText.toLowerCase()) > -1) ||
  (!row.assignedTo && row.assignedGroup && row.assignedGroup.toLowerCase().indexOf(searchText.toLowerCase()) > -1)
  ) && (_rt !== null ? row.requestType === _rt : (row.requestType === "general" || row.requestType === "personal") ) );

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
                <input className="foi-general-radio" type="radio" value="general" name="requestType" onChange={requestTypeChange} /> General
                <input className="foi-personal-radio" type="radio" value="personal" name="requestType" onChange={requestTypeChange} /> Personal
                <input className="foi-all-radio" type="radio" value="All" name="requestType" onChange={requestTypeChange} defaultChecked  /> All              
              </div>            
              
            </div>
            <div style={{ height: 450 }} className={classes.root}>
              <DataGrid 
                className="foi-data-grid"
                getRowId={(row) => row.idNumber}
                rows={search(rows)} 
                columns={columns.current}                
                rowHeight={30}
                headerHeight={50}
                pageSize={10}
                rowsPerPageOptions={[10]}
                hideFooterSelectedRowCount={true}
                sortingOrder={['desc', 'asc']}
                sortModel={sortModel}
                sortingMode={'client'}
                onSortModelChange={(model) => setSortModel(model)}
                getRowClassName={(params) =>
                  `super-app-theme--${params.getValue(params.id, 'currentState').toLowerCase().replace(/ +/g, "")}`
                } 
                onRowClick={renderReviewRequest}
                />
            </div> </>):<Loading/> }
            </>
          </div>
        </div> 
      
    );
  });

export default Dashboard;