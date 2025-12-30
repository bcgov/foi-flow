import React from "react";
import "./DocumentSetWrapper.css";
import Grid from "@material-ui/core/Grid";

export default function DocumentSetWrapper({ title, size, children }) {
  return (
    <div className="docset-wrapper">

      <div className="docset-header">
        <span className="docset-title">{title}</span>
        <span className="docset-size">Files size: {size}</span>
      </div>

      <Grid container item xs={12} className="docset-body">
        {children}
      </Grid>

    </div>
  );
}
