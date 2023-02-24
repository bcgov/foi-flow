import React, { useEffect } from 'react';
import { useDispatch, useSelector } from "react-redux";
import Container from '@mui/material/Container';
import { DataGrid } from '@material-ui/data-grid';

import { fetchProgramAreaDivisions } from '../../../apiManager/services/FOI/foiAdminServices';

import "./admin.scss";

const columns = [
  {
    field: 'divisionid',
    headerName: 'ID',
    type: 'number',
    width: 90
  },
  {
    field: 'programareaid',
    headerName: 'Area ID',
    type: 'number',
    width: 90
  },
  {
    field: 'name',
    headerName: 'Name',
    flex: 1
  },
];

const Admin = () => {
  let divisions = useSelector(
    (state) => state.foiRequests.foiProgramAreaDivisionList
  );

  const dispatch = useDispatch();

  useEffect(async () => {
    await Promise.all([dispatch(fetchProgramAreaDivisions())]);
  })

  return (
    <div className="admin-page">
      <Container>
        <h1>Test Admin</h1>
        <div style={{ height: 400, width: '100%' }}>
          <DataGrid
            getRowId={(row) => row.divisionid}
            rows={divisions}
            columns={columns}
            pageSize={8}
            checkboxSelection
            disableSelectionOnClick
          />
        </div>
      </Container>
    </div>
  );
};

export default Admin;
