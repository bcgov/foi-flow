import React, { useEffect, useState }  from 'react';
import { DataGrid } from '@material-ui/data-grid';
import "./dashboard.scss";

const Dashboard = React.memo(() => {
  let rows = [
    { id: 1, applicantName: "Joe, James", requestType: "Personal", idNumber: "00123", currentState: "UnOpened", assignedTo: "Unassigned", receivedDate: "2021 May 20", xgov: "No" },
    { id: 2, applicantName: "John, Walsh", requestType: "Personal", idNumber: "00124", currentState: "UnOpened", assignedTo: "Unassigned", receivedDate: "2021 May 20", xgov: "No" },
    { id: 3,  applicantName: "Bob, Herm", requestType: "Personal", idNumber: "00125", currentState: "UnOpened", assignedTo: "Unassigned", receivedDate: "2021 May 20", xgov: "No" },
    { id: 4,  applicantName: "James, Houston", requestType: "General", idNumber: "00126", currentState: "UnOpened", assignedTo: "Unassigned", receivedDate: "2021 May 20", xgov: "No" },
    { id: 5,  applicantName: "James, Houston", requestType: "General", idNumber: "00127", currentState: "UnOpened", assignedTo: "Unassigned", receivedDate: "2021 May 20", xgov: "No" },
    { id: 6,  applicantName: "James, Houston", requestType: "General", idNumber: "00128", currentState: "UnOpened", assignedTo: "Unassigned", receivedDate: "2021 May 20", xgov: "No" },
    { id: 7,  applicantName: "James, Houston", requestType: "General", idNumber: "00129", currentState: "UnOpened", assignedTo: "Unassigned", receivedDate: "2021 May 20", xgov: "No" },
    { id: 8,  applicantName: "James, Houston", requestType: "General", idNumber: "00130", currentState: "UnOpened", assignedTo: "Unassigned", receivedDate: "2021 May 20", xgov: "No" },
    { id: 9,  applicantName: "James, Houston", requestType: "General", idNumber: "00131", currentState: "UnOpened", assignedTo: "Unassigned", receivedDate: "2021 May 20", xgov: "No" },
    { id: 10,  applicantName: "James, Houston", requestType: "General", idNumber: "00132", currentState: "UnOpened", assignedTo: "Unassigned", receivedDate: "2021 May 20", xgov: "No" },
    { id: 11,  applicantName: "James, Houston", requestType: "General", idNumber: "00133", currentState: "UnOpened", assignedTo: "Unassigned", receivedDate: "2021 May 20", xgov: "No" },
    { id: 12,  applicantName: "James, Houston", requestType: "General", idNumber: "00134", currentState: "UnOpened", assignedTo: "Unassigned", receivedDate: "2021 May 20", xgov: "No" },
   ];
const [filteredData, setFilteredData] = useState(rows);
const [requestType, setRequestType] = useState("All");

useEffect(() => {       
    setFilteredData( requestType === 'All'? rows:rows.filter(row => row.requestType === requestType))
}, [requestType])

const columns = [
{ field: 'applicantName', headerName: 'APPLICANT NAME', width: 200 },
{ field: 'requestType', headerName: 'REQUEST TYPE', width: 200 },
{ field: 'idNumber', headerName: 'ID NUMBER', width: 200 },
{ field: 'currentState', headerName: 'CURRENT STATE', width: 200 },
{      
  field: 'assignedTo',
  headerName: 'ASSIGNED TO',
  width: 200,
  renderCell: (params) => (       
    <select>
        <option>1</option>
        <option>1</option>
        <option>1</option>
    </select>
  ),
  
},
{ field: 'receivedDate', headerName: 'RECEIVED DATE', width: 200 },
{ field: 'xgov', headerName: 'XGOV', width: 150 },
];  

const requestTypeChange = (e) => { 
  setRequestType(e.target.value);
}
     return (      
        <div className="foi-dashboard">
          <div className="col-md-12 foi-grid-container">
           <div>
            <input type="radio" value="General" name="requestType" onChange={requestTypeChange} /> General
            <input type="radio" value="Personal" name="requestType" onChange={requestTypeChange} /> Personal
            <input type="radio" value="All" name="requestType" onChange={requestTypeChange} defaultChecked  /> All
          </div>
          <div className="foi-grid">
            <DataGrid className="foi-data-grid" rows={filteredData} columns={columns} pageSize={5} />
          </div>
          </div>
        </div>
    );
  });

export default Dashboard;