import React, { useEffect, useState }  from 'react';
import { DataGrid } from '@material-ui/data-grid';
import "./dashboard.scss";
import useStyles from './CustomStyle';
import { useDispatch, useSelector } from "react-redux";
import {push} from "connected-react-router";

import { fetchFOIRequestList } from "../../../apiManager/services/FOI/foiRequestServices";

const Dashboard = React.memo((props) => {

  //START to uncomment from here - once the api is up

  // const rows = useSelector(state=> state.foiRequests.foiRequestsList)

  // useEffect(()=>{    
  //   dispatch(fetchFOIRequestList());
  // },[dispatch]);

  //END

  function getFullName(params) {   
    return `${params.getValue(params.id, 'lastName') || ''}, ${
      params.getValue(params.id, 'firstName') || ''
    }`;
  }
  //Comment/remove rows
  let rows = [
    { id: 1, firstName: "Joe",  lastName: "James", requestType: "Personal", idNumber: "00123", currentState: "Open", assignedTo: "Unassigned", receivedDate: "2021 May 20", xgov: "No" },
    { id: 2, firstName: "John",  lastName: "Walsh", requestType: "Personal", idNumber: "00124", currentState: "UnOpened", assignedTo: "Unassigned", receivedDate: "2021 May 20", xgov: "No" },
    { id: 3, firstName: "Bob",  lastName: "Herm", requestType: "Personal", idNumber: "00125", currentState: "UnOpened", assignedTo: "Unassigned", receivedDate: "2021 May 20", xgov: "No" },
    { id: 4, firstName: "James",  lastName: "Houston", requestType: "General", idNumber: "00126", currentState: "UnOpened", assignedTo: "Unassigned", receivedDate: "2021 May 20", xgov: "No" },
    { id: 5, firstName: "James",  lastName: "Houston", requestType: "General", idNumber: "00127", currentState: "UnOpened", assignedTo: "Unassigned", receivedDate: "2021 May 20", xgov: "No" },
    { id: 6, firstName: "James",  lastName: "Houston", requestType: "General", idNumber: "00128", currentState: "UnOpened", assignedTo: "Unassigned", receivedDate: "2021 May 20", xgov: "No" },
    { id: 7, firstName: "James",  lastName: "Houston", requestType: "General", idNumber: "00129", currentState: "UnOpened", assignedTo: "Unassigned", receivedDate: "2021 May 20", xgov: "No" },
    { id: 8, firstName: "James",  lastName: "Houston", requestType: "General", idNumber: "00130", currentState: "UnOpened", assignedTo: "Unassigned", receivedDate: "2021 May 20", xgov: "No" },
    { id: 9, firstName: "James",  lastName: "Houston", requestType: "General", idNumber: "00131", currentState: "UnOpened", assignedTo: "Unassigned", receivedDate: "2021 May 20", xgov: "No" },
    { id: 10, firstName: "James",  lastName: "Houston", requestType: "General", idNumber: "00132", currentState: "UnOpened", assignedTo: "Unassigned", receivedDate: "2021 May 20", xgov: "No" },
    { id: 11, firstName: "James",  lastName: "Houston", requestType: "General", idNumber: "00133", currentState: "Open", assignedTo: "Unassigned", receivedDate: "2021 May 20", xgov: "No" },
    { id: 12, firstName: "James",  lastName: "Houston", requestType: "General", idNumber: "00134", currentState: "Open", assignedTo: "Unassigned", receivedDate: "2021 May 20", xgov: "No" },
   ];
   const columns = [
    // { field: 'applicantName', headerName: 'APPLICANT NAME', width: 200 },
    // { field: 'firstName', headerName: 'First name', width: 130 },
    // { field: 'lastName', headerName: 'Last name', width: 130 },
    {
      field: 'applicantName',
      headerName: 'APPLICANT NAME',
      width: 200,
      valueGetter: getFullName,     
    },
    { field: 'requestType', headerName: 'REQUEST TYPE', width: 200, sortable: false },
    { field: 'idNumber', headerName: 'ID NUMBER', width: 200 },
    { field: 'currentState', headerName: 'CURRENT STATE', width: 200 },
    {      
      field: 'assignedTo',
      headerName: 'ASSIGNED TO',
      width: 200,
      renderCell: (params) => (       
        <select>
            <option>Unassigned</option>
            <option>Intake team</option>
            <option>Program area</option>
        </select>
      ),
      
    },
    { field: 'receivedDate', headerName: 'RECEIVED DATE', width: 200 },
    { field: 'xgov', headerName: 'XGOV', width: 150 },
    ];  
    
    const sortModel=[
      {
        field: 'currentState',
        sort: 'desc',
      },
      {
        field: 'applicantName',
        sort: 'desc',
      },
      {
        field: 'idNumber',
        sort: 'desc',
      },
      {
        field: 'assignedTo',
        sort: 'desc',
      },
      {
        field: 'receivedDate',
        sort: 'desc',
      },
      {
        field: 'xgov',
        sort: 'desc',
      },
    ];

const [filteredData, setFilteredData] = useState(rows);
const [requestType, setRequestType] = useState("All");
const [searchText, setSearchText] = useState("");
const classes = useStyles();

useEffect(() => {
    setFilteredData( requestType === 'All'? rows:rows.filter(row => row.requestType === requestType))
}, [requestType])


const requestTypeChange = (e) => {
  setRequestType(e.target.value);
}

const setSearch = (e) => {
  setSearchText(e.target.value);
}

const search = (rows) => { 
  return rows.filter(row => (row.firstName.toLowerCase().indexOf(searchText.toLowerCase()) > -1) || 
  (row.lastName.toLowerCase().indexOf(searchText.toLowerCase()) > -1) ||
  row.idNumber.toLowerCase().indexOf(searchText.toLowerCase()) > -1)
}
 const dispatch = useDispatch();
 
const renderReviewRequest = () => { 
  dispatch(push('/foi/reviewrequest')); 
}
     return (      
        <div className="container">
          <div className="col-md-12 foi-grid-container">
            <h3 className="foi-request-queue-text">Your FOI Request Queue</h3>
            <div className="foi-dashboard-row2">             
              <div className="form-group has-search">
                <span className="fa fa-search form-control-search"></span>
                <input type="text" className="form-control" placeholder="Search . . ." onChange={setSearch} />
                {/* <button type="button" className="btn btn-primary apply-btn">Apply</button> */}
              </div>
             
              <div className="foi-request-type">
                <input className="foi-general-radio" type="radio" value="General" name="requestType" onChange={requestTypeChange} /> General
                <input className="foi-personal-radio" type="radio" value="Personal" name="requestType" onChange={requestTypeChange} /> Personal
                <input className="foi-all-radio" type="radio" value="All" name="requestType" onChange={requestTypeChange} defaultChecked  /> All              
              </div>            
              
            </div>
            <div style={{ height: 410, width: '90%' }} className={classes.root}>
              <DataGrid 
                className="foi-data-grid" 
                rows={search(filteredData)} 
                columns={columns}
                rowHeight={30}
                headerHeight={50}                
                pageSize={10}
                hideFooterSelectedRowCount={true}
                sortingOrder={['desc', 'asc']}
                sortModel={sortModel}
                sortingMode={'client'}
                getRowClassName={(params) =>
                  `super-app-theme--${params.getValue(params.id, 'currentState')}`
                } 
                onRowClick={renderReviewRequest}
                />
            </div>
          </div>
        </div>
    );
  });

export default Dashboard;