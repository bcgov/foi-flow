import React, { useEffect, useState }  from 'react';
import { DataGrid } from '@material-ui/data-grid';
import "./dashboard.scss";
import useStyles from './CustomStyle';
import { useDispatch, useSelector } from "react-redux";
import {push} from "connected-react-router";
import { fetchFOIRequestList } from "../../../apiManager/services/FOI/foiRequestServices";

const Dashboard = React.memo((props) => {

  const dispatch = useDispatch();

  const rows = useSelector(state=> state.foiRequests.foiRequestsList)
  const [filteredData, setFilteredData] = useState(rows);
  const [requestType, setRequestType] = useState("All");
  const [searchText, setSearchText] = useState("");
  const classes = useStyles();
  

  useEffect(()=>{    
    dispatch(fetchFOIRequestList());
    setFilteredData( requestType === 'All'? rows:rows.filter(row => row.requestType === requestType))
  },[dispatch], [requestType]);

  function getFullName(params) {   
    return `${params.getValue(params.id, 'lastName') || ''}, ${
      params.getValue(params.id, 'firstName') || ''
    }`;
  }
   
   const columns = [
    
    {
      field: 'applicantName',
      headerName: 'APPLICANT NAME',
      width: 170,      
      headerAlign: 'left',
      valueGetter: getFullName,     
    },
     { field: 'requestType', headerName: 'REQUEST TYPE',  flex: 1, headerAlign: 'left',//width: 150,  
      sortable: false },
    { field: 'idNumber', headerName: 'ID NUMBER',
       flex: 1, 
       headerAlign: 'left',      
    },
    { field: 'currentState', headerName: 'CURRENT STATUS', 
      
       headerAlign: 'left',
       width: 160 
    },
    {      
      field: 'assignedTo',
      headerName: 'ASSIGNED TO',
      flex: 1,
      headerAlign: 'left',     
      renderCell: (params) => (       
        <select>
            <option>Unassigned</option>
            <option>Intake team</option>
            <option>Program area</option>
        </select>
      ),
      
    },
    { field: 'receivedDate', headerName: 'RECEIVED DATE', 
      flex: 1,     
      headerAlign: 'left',
    },    
    { field: 'xgov', headerName: 'XGOV', 
      flex: 1,      
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
  row.idNumber.toLowerCase().indexOf(searchText.toLowerCase()) > -1 ) && (_rt !== null ? row.requestType === _rt : (row.requestType === "general" || row.requestType === "personal") ) );

}
 

const renderReviewRequest = (e) => {  
  dispatch(push(`/foi/reviewrequest/${e.row.id}`));
}

     return (  
               
        <div className="container foi-container">
           
          <div className="col-sm-12 col-md-12 foi-grid-container">
            <h3 className="foi-request-queue-text">Your FOI Request Queue</h3>
           
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