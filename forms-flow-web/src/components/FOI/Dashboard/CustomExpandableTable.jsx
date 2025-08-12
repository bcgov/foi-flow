import React, { useState } from "react";
import {
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, TablePagination, Box, TextField
  } from "@mui/material";
import ExpandCircleDownRoundedIcon from "@mui/icons-material/ExpandCircleDownRounded";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import ArrowUpwardIcon from "@mui/icons-material/ArrowUpward";
import ArrowDownwardIcon from "@mui/icons-material/ArrowDownward";
import "./customExpandableTable.scss";
import { mergeSubConsultsWithRow } from "./utils";
import TablePaginationWrapper from './TablePaginationWrapper'

const CustomExpandableTable = ({
  columns,
  subConsultsColumns,
  rows,
  getRowId,
  renderExpandedRow,
  rowHeight = 30,
  headerHeight = 50,
  rowCount,
  page,
  pageSize,
  onPageChange,
  onPageSizeChange,
  sortModel,
  onSortModelChange,
  filterModel,
  onFilterChange,
  getRowClassName,
  onRowClick,
  onConsultRowClick,
  loading,
  FooterComponent,
}) => {
  const [expandedId, setExpandedId] = useState(null);
  const [localFilters, setLocalFilters] = useState({});
  const [localSortModel, setLocalSortModel] = useState(sortModel || null);

  const handleSort = (col) => {
    // Remove the sortable check to allow all columns to be sortable
    let direction = "asc";
    if (localSortModel && localSortModel.field === col.field && localSortModel.sort === "asc") {
      direction = "desc";
    }
    
    const newSortModel = { field: col.field, sort: direction };
    setLocalSortModel(newSortModel);
    
    // Call parent callback if provided
    onSortModelChange && onSortModelChange(newSortModel);
  };

  const handleFilter = (col, value) => {
    setLocalFilters((prev) => ({ ...prev, [col.field]: value }));
    onFilterChange && onFilterChange({ ...localFilters, [col.field]: value });
  };

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const getCellValue = (col, row) => {
    const baseValue = col.valueGetter ? col.valueGetter({ row }) : row[col.field];
  
    const params = { row, value: baseValue };
  
    if (col.renderCell) {
      return col.renderCell(params);
    }
  
    return baseValue ?? "";
  };
  

  return (
    <Box className="MuiDataGrid-root" sx={{ width: '100%', maxWidth: '100%', overflow: 'hidden' }}>
      <TableContainer 
        component={Paper} 
        className="MuiDataGrid-virtualScroller"
        sx={{ 
          position: "relative",
          borderRadius: "4px",
          borderLeft: 'none',
          borderRight: 'none',
          maxHeight: 'calc(100vh - 300px)',
        }}
      >
        <Table 
          size="small" 
          className="MuiDataGrid-virtualScrollerContent"
          sx={{
            borderCollapse: 'collapse',
            '& .MuiTableCell-root': {
              borderLeft: 'none',
              borderRight: 'none',
            }
          }}
        >
          <TableHead className="MuiDataGrid-columnHeaders">
            <TableRow className="MuiDataGrid-row">
              {columns.map((col) => (
                <TableCell
                  key={col.field}
                  className="MuiDataGrid-columnHeader"
                  align={col.align || "left"}
                  onClick={() => handleSort(col)}
                                      sx={{
                      cursor: "pointer", // Always show pointer cursor for sorting
                      width: col.width,
                      borderBottom: "2px solid #212529",
                      backgroundColor: "#fff",
                      fontWeight: 400,
                      fontSize: "0.875rem",
                      padding: "8px 16px",
                      "&:hover": {
                        backgroundColor: "#f5f5f5" // Always show hover effect
                      }
                    }}
                >
                  <Box className="MuiDataGrid-columnHeaderTitleContainer">
                    <span className="MuiDataGrid-columnHeaderTitle">
                      {col.headerName || col.field}
                      {localSortModel && localSortModel.field === col.field && (
                        <span style={{ marginLeft: '4px', display: 'inline-flex', alignItems: 'center' }}>
                          {localSortModel.sort === "asc" ? 
                            <ArrowUpwardIcon sx={{ fontSize: 16, color: '#666' }} /> : 
                            <ArrowDownwardIcon sx={{ fontSize: 16, color: '#666' }} />
                          }
                        </span>
                      )}
                    </span>
                  </Box>
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
                    <TableBody className="MuiDataGrid-virtualScrollerRenderZone">
            {loading ? (
              <TableRow>
                <TableCell colSpan={columns.length} align="center">
                  Loading...
                </TableCell>
              </TableRow>
            ) : (
              rows.slice(page * pageSize, (page + 1) * pageSize).map((row, rowIndex) => {
                const id = getRowId(row);
                const isExpandable = row.subConsults?.length > 0;
                const isExpanded = id === expandedId;
                const rowClass = getRowClassName ? getRowClassName({ row }) : "";
                const displaySubConsults = mergeSubConsultsWithRow(row);
                const actualRowIndex = page * pageSize + rowIndex; 
                return (
                  <React.Fragment key={id}>
                    <TableRow
                      className={`MuiDataGrid-row ${rowClass}`}
                      hover
                      sx={{ 
                        height: rowHeight,
                        "&:hover": {
                          backgroundColor: "#f5f5f5"
                        },
                        "&.Mui-selected": {
                          backgroundColor: "#e3f2fd"
                        }
                      }}
                      onClick={() => onRowClick?.({ row })}
                    >
                      {columns.map((col, colIdx) => (
                        <TableCell 
                          key={col.field} 
                          className="MuiDataGrid-cell"
                          align={col.align || "left"}
                          sx={{
                            borderLeft: 'none',
                            borderRight: 'none',
                            borderBottom: rowIndex === Math.min(pageSize - 1, rows.length - page * pageSize - 1) ? 'none' : "1px solid #e0e0e0",
                            padding: "8px 16px",
                            maxWidth: col.width | 200 ,
                            fontSize: "0.875rem",
                            whiteSpace: "nowrap",
                            overflow: "hidden",  
                            textOverflow: "ellipsis",      
                            "&:focus": {
                              outline: "none"
                            }
                          }}
                        >
                          <Box display="flex" alignItems="center" justifyContent="space-between">
                            <span>
                                {/* {col.renderCell ? col.renderCell({ row }) : row[col.field] ?? ""} */}
                                {getCellValue(col, row)}
                            </span>
                            {colIdx === columns.length - 1 && isExpandable && (
                                <IconButton
                                size="small"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    toggleExpand(id);
                                }}
                                sx={{
                                    color: "#666",
                                    padding: "2px",
                                    marginLeft: "8px",
                                    width: "18px",
                                    height: "18px",
                                    "& .MuiSvgIcon-root": {
                                    fontSize: "16px",
                                    }
                                }}
                                >
                                {isExpanded ? <ExpandLessIcon /> : <ExpandCircleDownRoundedIcon />}
                                </IconButton>
                            )}
                            </Box>
                        </TableCell>
                      ))}
                    </TableRow>
                    {isExpanded && (
                      <TableRow className="MuiDataGrid-row subconsults-container">
                        <TableCell 
                          colSpan={columns.length} 
                          className="MuiDataGrid-cell"
                          sx={{ 
                            padding: "0",
                            borderBottom: "none",
                            backgroundColor: "#fafafa"
                          }}
                        >
                          <Box sx={{ padding: "8px 16px" }}>
                            {Array.isArray(subConsultsColumns.current) && displaySubConsults.map((consult, idx) => {
                              return (
                              <Box 
                                key={consult.consultid || idx} 
                                className="MuiDataGrid-row subconsults-row"
                                hover 
                                sx={{ 
                                  display: "flex",
                                  alignItems: "center",
                                  height: rowHeight,
                                  backgroundColor: "#fafafa",
                                  "&:hover": {
                                    backgroundColor: "#f0f0f0"
                                  }
                                }}
                              >
                                {(subConsultsColumns.current).map(col => {
                                  return (
                                  <TableCell 
                                    key={col.field} 
                                    className="MuiDataGrid-cell"
                                    align={col.align || "left"}
                                    sx={{
                                      borderLeft: 'none',
                                      borderRight: 'none',
                                      borderBottom: displaySubConsults.indexOf(consult) === displaySubConsults.length - 1 ? 'none' : "1px solid #e0e0e0",
                                      padding: "8px 16px",
                                      fontSize: "0.875rem",
                                      cursor: "pointer",
                                      width: col.width || 'auto',
                                      minWidth: col.width || 100,
                                      maxWidth: col.width || 200,
                                      whiteSpace: "nowrap",
                                      overflow: "hidden",  
                                      textOverflow: "ellipsis"
                                    }}
                                    onClick={(e) => {
                                      e.stopPropagation();
                                       
                                      // Pass the consult data with proper ID and parent row information
                                      const consultData = {
                                        ...consult,
                                        consultid: consult.id || consult.consultid || consult.requestId,
                                        // Add parent row information for navigation
                                        id: row.id, // Request ID
                                      };
                 
                                      if (onConsultRowClick) {
                                        onConsultRowClick({ row: consultData });
                                      } 
                                    }}
                                  >
                                    {/* {col.renderCell ? col.renderCell({ row: consult }) : consult[col.field] ?? ""} */}
                                    {getCellValue(col, consult)}
                                  </TableCell>
                                  );
                              })}
                              </Box>
                              );
                            })}
                          </Box>
                        </TableCell>
                      </TableRow>
                    )}
                  </React.Fragment>
                );
              })
            )}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePaginationWrapper
        rowCount={rowCount}
        page={page}
        pageSize={pageSize}
        onPageChange={onPageChange}
        onPageSizeChange={onPageSizeChange}
      />
    </Box>
  );
};

export default CustomExpandableTable;