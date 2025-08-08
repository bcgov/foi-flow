import { Box, Typography, TablePagination } from "@mui/material";
import IconButton from "@mui/material/IconButton";
import KeyboardArrowLeft from "@mui/icons-material/KeyboardArrowLeft";
import KeyboardArrowRight from "@mui/icons-material/KeyboardArrowRight";

const TablePaginationWrapper = ({
    rowCount,
    page,
    pageSize,
    onPageChange,
    onPageSizeChange
  }) => {
    const totalPages = Math.ceil(rowCount / pageSize);
    return (
      <Box
        display="flex"
        alignItems="center"
        justifyContent="space-between"
        padding="8px 16px"
        bgcolor="#fff"
        // borderTop="1px solid #e0e0e0"
      >
        <Typography variant="body2">
          Total # of Request in Queue: {rowCount}
        </Typography>
        
        {/* <Box display="flex" alignItems="center" gap={1}>
            <IconButton
            onClick={() => onPageChange && onPageChange(Math.max(0, page - 1))}
            disabled={page === 0}
            size="small"
            >
            <KeyboardArrowLeft fontSize="small" />
            </IconButton>
            <Typography variant="body2">{page + 1}</Typography>
            <IconButton
            onClick={() =>
                onPageChange &&
                onPageChange(Math.min(totalPages - 1, page + 1))
            }
            disabled={page >= totalPages - 1}
            size="small"
            >
            <KeyboardArrowRight fontSize="small" />
            </IconButton>
        </Box> */}

        <Box display="flex" alignItems="center" gap={1}>
        <IconButton
            onClick={() => onPageChange(Math.max(0, page - 1))}
            disabled={page === 0}
            size="small"
        >
            <KeyboardArrowLeft fontSize="small" />
        </IconButton>
        <Typography variant="body2">{page + 1}</Typography>
        <IconButton
            onClick={() => onPageChange(Math.min(totalPages - 1, page + 1))}
            disabled={page >= totalPages - 1}
            size="small"
        >
            <KeyboardArrowRight fontSize="small" />
        </IconButton>
        </Box>
      
        <TablePagination
          component="div"
          count={rowCount}
          page={page}
          onPageChange={(e, newPage) => onPageChange && onPageChange(newPage)}
          rowsPerPage={pageSize}
          onRowsPerPageChange={e => onPageSizeChange && onPageSizeChange(parseInt(e.target.value, 10))}
          rowsPerPageOptions={[10, 20, 50, 100]}
          ActionsComponent={() => null}
          labelDisplayedRows={() => ''}
          sx={{
            '.MuiTablePagination-toolbar': {
              paddingLeft: 0,
              paddingRight: 0,
            },
          }}
        />
      </Box>
    );
  };


  export default TablePaginationWrapper;