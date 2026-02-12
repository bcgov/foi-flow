import React, { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Link,
  Typography,
} from "@mui/material";
import CancelIcon from '@mui/icons-material/Cancel';

export const LinkedRequestsTable = ({
    linkedRequestsInfo,
    linkedRequests,
    renderReviewRequest,
    removeLinkedRequest,
    isMinistry
}) => {
    const [page, setPage] = useState(0);
    const MAX_ROWS_PER_PAGE = 7;

    return (
        <>
            {linkedRequests.length > 0 &&
            <>
            <TableContainer sx={{display:"flex", flexDirection: "row", justifyContent: "center"}}>
                <Table sx={{width: "75%", border: 2, borderColor: 'divider', '& td, & th': {border: 2, borderColor: 'divider'}, borderCollapse: 'collapse'}} size="small">
                    <TableHead>
                        <TableRow>
                            <TableCell sx={{backgroundColor: "#003366", fontWeight: "bold",  color: "#FFF",}} align="center">MIN</TableCell>
                            <TableCell sx={{backgroundColor: "#003366", fontWeight: "bold",  color: "#FFF",}} align="center">Request ID</TableCell>
                            <TableCell sx={{backgroundColor: "#003366", fontWeight: "bold",  color: "#FFF",}} align="center">Request State</TableCell>
                            {!isMinistry && <TableCell sx={{backgroundColor: "#003366", fontWeight: "bold",  color: "#FFF",}} align="center">Remove</TableCell>}
                        </TableRow>
                    </TableHead>
                    <TableBody>
                    {linkedRequestsInfo?.
                    slice(page * MAX_ROWS_PER_PAGE, page * MAX_ROWS_PER_PAGE + MAX_ROWS_PER_PAGE)
                    .map((reqObj, idx) => {
                        return (
                        <TableRow key={idx}>
                        <TableCell align="center" component="th" scope="row">{linkedRequests[idx]?.govcode}</TableCell>
                        <TableCell align="center">
                            {!isMinistry ?
                                <Link
                                    component="button"
                                    sx={{ color: "#38598A", cursor: "pointer", textDecoration: "underline"}}
                                    onClick={(e) => renderReviewRequest(e, reqObj)}
                                    className="linked-request-link"
                                >
                                {reqObj.axisrequestid}
                                </Link>
                                : <Typography>{reqObj.axisrequestid}</Typography>
                            }
                        </TableCell>
                        <TableCell align="center">{reqObj.requeststatus}</TableCell>
                        {!isMinistry &&
                            <TableCell align="center">
                                <button
                                    className="btn btn-link text-danger"
                                    aria-label={`Remove linked request ${reqObj.axisrequestid}`}
                                    onClick={() => removeLinkedRequest(reqObj)}
                                >
                                <CancelIcon
                                    fontSize="small"
                                    sx={{ color: "#038 !important" }}
                                />
                                </button>
                            </TableCell>
                        }
                        </TableRow>
                    )})}
                    </TableBody>
                </Table>
            </TableContainer>
            <TablePagination
                component="div"
                count={linkedRequests?.length}
                rowsPerPage={MAX_ROWS_PER_PAGE}
                rowsPerPageOptions={[]}
                page={page}
                onPageChange={(e, newPage) => setPage(newPage)}
                sx={{display: "flex", flexDirection: "row", justifyContent: "center"}}
            />
            </>
            }
        </>
    );
}