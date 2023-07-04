import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import Grid from "@mui/material/Grid";
import {
    gridPageCountSelector,
    gridPageSelector,
    useGridApiContext,
    useGridSelector,
    gridPageSizeSelector,
  } from "@mui/x-data-grid";
import Pagination from "@mui/material/Pagination";
import NativeSelect from '@mui/material/NativeSelect';
import { setResumeDefaultSorting } from "../../../actions/FOI/foiRequestActions";
import { Typography } from "@mui/material";

const CustomPagination = ({apiRef, page, pageCount}) => {
    return (
        <Pagination
        count={pageCount}
        page={page + 1}
        onChange={(_event, value) => apiRef.current.setPage(value - 1)}
        className="footerContent"
        />
    );
};
  
const CustomPageSize = ({apiRef, pageSize}) => {
    return (
      <Grid
        item
        xs={12}
        // lg={3}
        alignItems="center"
        className="footerContent"
      >
        Rows per page: 
        <NativeSelect
          defaultValue={pageSize}
          inputProps={{
            name: 'pagesize',
            id: 'uncontrolled-native',
          }}
          sx={{
            paddingLeft: "5px",
          }}
          onChange={(_event) => apiRef.current.setPageSize(_event.target.value)}
        >
          <option value={10}>10</option>
          <option value={20}>20</option>
          <option value={50}>50</option>
          <option value={100}>100</option>
        </NativeSelect>
      </Grid>
    );
};
  
export const CustomFooter = ({rowCount, defaultSortModel, footerFor}) => {
    const dispatch = useDispatch();
  
    const apiRef = useGridApiContext();
    const page = useGridSelector(apiRef, gridPageSelector);
    const pageCount = useGridSelector(apiRef, gridPageCountSelector);
    const pageSize = useGridSelector(apiRef, gridPageSizeSelector);
  
    const resumeDefaultSorting = useSelector((state) => state.foiRequests.resumeDefaultSorting)
    const showAdvancedSearch = useSelector((state) => state.foiRequests.showAdvancedSearch)
  
    //apply default sorting model
    useEffect(() => {
      if(resumeDefaultSorting) {
        if((showAdvancedSearch && footerFor == 'advancedsearch') || (!showAdvancedSearch && footerFor != 'advancedsearch')) {
          apiRef.current.setSortModel(defaultSortModel);
          dispatch(setResumeDefaultSorting(false));
        }
      }
    }, [resumeDefaultSorting]);
  
    return (
      <Grid
        container
        direction="row"
        // className="foi-grid-container"
        spacing={1}
      >
        <Grid
          item
          xs={3}
          // lg={3}
          alignItems="center"
        >
          <Typography className="footerContent">Total # of Request in Queue: {rowCount}</Typography>
        </Grid>
        <Grid
          item
          xs={6}
          // lg={3}
          alignItems="center"
        >
          <CustomPagination apiRef={apiRef} page={page} pageCount={pageCount}></CustomPagination>
        </Grid>
        <Grid
          item
          xs={3}
          // lg={3}
          // alignItems="center"
          textAlign="right"
        >
          <CustomPageSize apiRef={apiRef} pageSize={pageSize}></CustomPageSize>
        </Grid>
      </Grid>
    );
};