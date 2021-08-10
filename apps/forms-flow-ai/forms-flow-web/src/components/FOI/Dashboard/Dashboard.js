import React, { useEffect, useState }  from 'react';
import { DataGrid } from '@material-ui/data-grid';
import "./dashboard.scss";
import useStyles from './CustomStyle';
import { useDispatch, useSelector } from "react-redux";
import {push} from "connected-react-router";
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';
import { fetchFOIRequestList, fetchFOIAssignedToList } from "../../../apiManager/services/FOI/foiRequestServices";

const Dashboard = React.memo((props) => {

  const dispatch = useDispatch();

  const rows = useSelector(state=> state.foiRequests.foiRequestsList);  
  const [filteredData, setFilteredData] = useState(rows);
  const [requestType, setRequestType] = useState("All");
  const [searchText, setSearchText] = useState("");
  

  const classes = useStyles(); 

  useEffect(()=>{
    dispatch(fetchFOIAssignedToList());
    dispatch(fetchFOIRequestList());
    setFilteredData( requestType === 'All'? rows:rows.filter(row => row.requestType === requestType))
  },[dispatch], [requestType]);

  const assignedToList = useSelector(state=> state.foiRequests.foiAssignedToList);
  const [selectedAssignedTo, setAssignedTo] = React.useState('Unassigned');

  function getFullName(params) {    
    return `${params.getValue(params.id, 'lastName') || ''}, ${
      params.getValue(params.id, 'firstName') || ''
    }`;
  }

  const getAssigneeFullName = (lastName, firstName, username) => {
    return  firstName !== "" ? `${lastName}, ${firstName}` : username;         
}

  //handle onChange event for assigned To
  const handleAssignedToOnChange = (event) => {
    setAssignedTo(event.target.value);    
}
const menuItems = assignedToList.map((item) => {    
  return ( <MenuItem key={item.id} value={item.username} disabled={item.username.toLowerCase().includes("unassigned")}>{getAssigneeFullName(item.lastname,item.firstname,item.username)}</MenuItem> )
});
   const columns = [    
    {
      field: 'applicantName',
      headerName: 'APPLICANT NAME',
      width: 170,      
      headerAlign: 'left',
      valueGetter: getFullName,     
    },
     { field: 'requestType', headerName: 'REQUEST TYPE',  width: 150, headerAlign: 'left',//width: 150,  
      sortable: false },
    { field: 'idNumber', headerName: 'ID NUMBER',
       width: 150, 
       headerAlign: 'left',      
    },
    { field: 'currentState', headerName: 'CURRENT STATUS', 
      
       headerAlign: 'left',
       width: 180 
     
    },
    {      
      field: 'assignedTo',
      headerName: 'ASSIGNED TO',
      width: 180,
      headerAlign: 'left',
      
    },
    { field: 'receivedDate', headerName: 'RECEIVED DATE', 
      width: 180,    
      headerAlign: 'left',
    },    
    { field: 'xgov', headerName: 'XGOV', 
      width: 100,      
      headerAlign: 'left',
    },
    { field: 'receivedDateUF', headerName: '', width: 0, hide: true, renderCell:(params)=>(<span></span>)}
    ];  
    
    const sortModel=[
      {
        field: 'currentState',
        sort: 'desc',
      },
      {
        field: 'receivedDateUF',
        sort: 'desc',
      }      
    ];

const requestTypeChange = (e) => { 
  setRequestType(e.target.value);
  
}

const setSearch = (e) => {
  setSearchText(e.target.value);
}

const search = (rows) => {   
  var _rt =  (requestType === "general" || requestType === "personal") ? requestType : null ;
  
  return rows.filter(row => ((row.firstName.toLowerCase().indexOf(searchText.toLowerCase()) > -1) || 
  (row.lastName.toLowerCase().indexOf(searchText.toLowerCase()) > -1) ||
  row.idNumber.toLowerCase().indexOf(searchText.toLowerCase()) > -1  ||
  row.currentState.toLowerCase().indexOf(searchText.toLowerCase()) > -1
  ) && (_rt !== null ? row.requestType === _rt : (row.requestType === "general" || row.requestType === "personal") ) );

}
 

const renderReviewRequest = (e) => {  
  dispatch(push(`/foi/reviewrequest/${e.row.id}`));
}
const createRequest = (e) => {
  dispatch(push(`/foi/createrequest`));
}

     return (  
               
        <div className="container foi-container">
           
          <div className="col-sm-12 col-md-12 foi-grid-container">
            <div className="foi-dashboard-row2">
              <h3 className="foi-request-queue-text">Your FOI Request Queue</h3>
              <button type="button" className="btn foi-btn-create" onClick={createRequest} >Create Request</button>
            </div>
            <div className="foi-dashboard-row2">             
              <div className="form-group has-search">
                <span className="fa fa-search form-control-search"></span>
                <input type="text" className="form-control" placeholder="Search . . ." onChange={setSearch} />
                {/* <button type="button" className="btn btn-primary apply-btn">Apply</button> */}
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
                rows={search(rows)} 
                columns={columns}                
                rowHeight={30}
                headerHeight={50}                
                pageSize={10}
                hideFooterSelectedRowCount={true}
                sortingOrder={['desc', 'asc']}
                sortModel={sortModel}
                sortingMode={'client'}
                getRowClassName={(params) =>
                  `super-app-theme--${params.getValue(params.id, 'currentState').replace(/ +/g, "")}`
                } 
                onRowClick={renderReviewRequest}
                />
            </div> 
          </div>
        </div> 
      
    );
  });

export default Dashboard;