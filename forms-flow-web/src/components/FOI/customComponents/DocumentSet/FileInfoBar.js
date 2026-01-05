import React from "react";
import Grid from "@material-ui/core/Grid";
import Typography from "@material-ui/core/Typography";
import FolderIcon from "@material-ui/icons/Folder";

export default function FileInfoBar({ size }) {
  // If size is a number (bytes), convert to MB
  const formattedSize =
    typeof size === "number"
      ? `${(size / 1024).toFixed(2)} KB`
      : size; // assume it's already formatted

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
              <strong>Files size:</strong> {formattedSize}
            </Typography>
          </Grid>
        </Grid>
      </Grid>
    </Grid>
  );
}
