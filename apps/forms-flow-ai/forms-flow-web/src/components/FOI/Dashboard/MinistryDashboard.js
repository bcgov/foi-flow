import React, { useEffect, useState }  from 'react';
import { DataGrid } from '@material-ui/data-grid';
import "./dashboard.scss";
import useStyles from './CustomStyle';
import { useDispatch, useSelector } from "react-redux";
import {push} from "connected-react-router";
import { fetchFOIMinistryRequestList, fetchFOIFullAssignedToList } from "../../../apiManager/services/FOI/foiRequestServices";
import { formatDate } from "../../../helper/FOI/helper";
import Loading from "../../../containers/Loading";

const MinistryDashboard = React.memo((props) => {

  const dispatch = useDispatch();  
  const assignedToList = useSelector((state) => state.foiRequests.foiFullAssignedToList);
  const rows = useSelector(state=> state.foiRequests.foiMinistryRequestsList);  
  const isLoading = useSelector(state=> state.foiRequests.isLoading);
  const isAssignedToListLoading = useSelector(state=> state.foiRequests.isAssignedToListLoading);  
  const [requestFilter, setRequestFilter] = useState("All");
  const [searchText, setSearchText] = useState("");
  const classes = useStyles();
  useEffect(()=>{
    dispatch(fetchFOIFullAssignedToList());
    dispatch(fetchFOIMinistryRequestList());
    
  },[dispatch]);

  function getAssigneeValue(params) {
    const groupName = params.row.assignedministrygroup ? params.row.assignedministrygroup : "Unassigned";
    const assignedTo = params.row.assignedministryperson ? params.row.assignedministryperson : groupName;
    if (assignedToList.length > 0) {
      const assigneeDetails = assignedToList.find(assigneeGroup => assigneeGroup.name === groupName);
      const assignee = assigneeDetails && assigneeDetails.members && assigneeDetails.members.find(assignee => assignee.username === assignedTo);
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
    let receivedDateString = params.getValue(params.id, 'cfrduedate'); 
    return formatDate(receivedDateString, 'yyyy MMM, dd');    
  }
  function getLDD(params) {
    let receivedDateString = params.getValue(params.id, 'duedate'); 
    return formatDate(receivedDateString, 'yyyy MMM, dd');    
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
    
    { field: 'cfrstatus', 
      headerName: 'CFR STATUS',  
      width: 150, 
      headerAlign: 'left'      
    },    
    {      
      field: 'assignedToValue',
      headerName: 'ASSIGNEE',
      width: 180,
      headerAlign: 'left',
      valueGetter: getAssigneeValue,      
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

    const [sortModel, setSortModel]= useState([
      {
        field: 'cfrduedate',
        sort: 'desc',
      },        
    ]);
    

const requestFilterChange = (e) => { 
  setRequestFilter(e.target.value);
  
}

const setSearch = (e) => {
  setSearchText(e.target.value);
}

const search = (rows) => {   
  // var _rt =  (requestFilter === "myRequests" || requestFilter === "watchingRequests") ? requestFilter : null ;  
  return rows.filter(row => (
  row.idNumber.toLowerCase().indexOf(searchText.toLowerCase()) > -1  ||
  row.applicantcategory.toLowerCase().indexOf(searchText.toLowerCase()) > -1  ||
  row.requestType.toLowerCase().indexOf(searchText.toLowerCase()) > -1  ||
  row.cfrstatus.toLowerCase().indexOf(searchText.toLowerCase()) > -1 ||
  (row.assignedministryperson && row.assignedministryperson.toLowerCase().indexOf(searchText.toLowerCase()) > -1) ||
  (!row.assignedministryperson && row.assignedministrygroup && row.assignedministrygroup.toLowerCase().indexOf(searchText.toLowerCase()) > -1)
  ) 
  // && (_rt !== null ? row.requestType === _rt : (row.requestType === "myRequests" || row.requestType === "watchingRequests") ) 
  );

}
 

const renderReviewRequest = (e) => {
  if (e.row.ministryrequestid) {
    dispatch(push(`/foi/foirequests/${e.row.id}/ministryrequest/${e.row.ministryrequestid}/${e.row.currentState}`));
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

export default MinistryDashboard;