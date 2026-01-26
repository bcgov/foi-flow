import React from "react";
import Grid from "@material-ui/core/Grid";
import Typography from "@material-ui/core/Typography";
import FolderIcon from "@material-ui/icons/Folder";
import {formatBytes} from "../Records/util";

export default function FileInfoBar({ size }) {

  return (
    <Grid
      container
      spacing={2}
      alignItems="center"
      style={{
        padding: "10px 20px",
      }}
    >

      {/* File size */}
      <Grid item>
        <Grid container direction="row" alignItems="center" spacing={1}>
          <Grid item>
            <FolderIcon fontSize="small" color="primary" />
          </Grid>
          <Grid item>
            <Typography variant="body2">
              <strong>Total size:</strong> {formatBytes(size ?? 0)}
            </Typography>
          </Grid>
        </Grid>
      </Grid>
    </Grid>
  );
}
