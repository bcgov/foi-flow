import React from "react";
import { useDispatch } from "react-redux";
import { push } from "connected-react-router";
import Grid from "@mui/material/Grid";
import Card from "@material-ui/core/Card";
import CardActionArea from "@material-ui/core/CardActionArea";
import CardContent from "@material-ui/core/CardContent";
import Typography from "@material-ui/core/Typography";

import "./admin.scss";

const Admin = () => {
  const dispatch = useDispatch();

  return (
    <div className="container admin-container">
      <Grid
        container
        direction="row"
        className="admin-grid-container"
        spacing={3}
      >
        <Grid item xs={12}>
          <Typography variant="h4" component="h1" className="admin-title">
            Admin Dashboard
          </Typography>
        </Grid>
        <Grid item component={Card} xs={12} sm={6} md={4} lg={3} sx={{ m: 1 }}>
          <CardActionArea>
            <CardContent onClick={() => dispatch(push(`/admin/divisions`))}>
              <Typography gutterBottom variant="h5" component="h2">
                Manage Divisions
              </Typography>
            </CardContent>
          </CardActionArea>
        </Grid>
        <Grid item component={Card} xs={12} sm={6} md={4} lg={3} sx={{ m: 1 }}>
          <CardActionArea>
            <CardContent onClick={() => console.log("manage stages")}>
              <Typography gutterBottom variant="h5" component="h2">
                Manage Stages
              </Typography>
            </CardContent>
          </CardActionArea>
        </Grid>
        <Grid item component={Card} xs={12} sm={6} md={4} lg={3} sx={{ m: 1 }}>
          <CardActionArea>
            <CardContent
              onClick={() => console.log("manage applicant categories")}
            >
              <Typography gutterBottom variant="h5" component="h2">
                Manage Applicant Categories
              </Typography>
            </CardContent>
          </CardActionArea>
        </Grid>
        <Grid item component={Card} xs={12} sm={6} md={4} lg={3} sx={{ m: 1 }}>
          <CardActionArea>
            <CardContent onClick={() => console.log("manage program areas")}>
              <Typography gutterBottom variant="h5" component="h2">
                Manage Program Areas
              </Typography>
            </CardContent>
          </CardActionArea>
        </Grid>
      </Grid>
    </div>
  );
};

export default Admin;
