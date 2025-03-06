import React, { useState } from "react";
import { useDispatch } from "react-redux";
import { push } from "connected-react-router";
import Grid from "@mui/material/Grid";
import Card from "@material-ui/core/Card";
import CardActionArea from "@material-ui/core/CardActionArea";
import CardContent from "@material-ui/core/CardContent";
import Typography from "@material-ui/core/Typography";
import {refreshRedisCacheForAdmin} from "../../../apiManager/services/FOI/foiMasterDataServices";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSyncAlt } from '@fortawesome/free-solid-svg-icons'; 
import {isFoiAdmin} from "../../../helper/FOI/helper";
import { toast } from "react-toastify";
import "./admin.scss";
import Loading from "../../../containers/Loading";

const Admin = ({userDetail}) => {

  const dispatch = useDispatch();
  const userGroups = userDetail?.groups?.map(group => group.slice(1));
  let isAdmin = isFoiAdmin(userGroups);
  const [disableCacheRefresh, setDisableCacheRefresh] = useState(false);

  const refreshRedisCache = () => {
      setDisableCacheRefresh(true);
      dispatch(refreshRedisCacheForAdmin((err, res) => {            
        if (!err && res) {
          toast.success(res.message?res.message : "Cache refreshed successfully.", {
            position: "top-right",
            autoClose: 3000,
            hideProgressBar: true,
            closeOnClick: true,
            pauseOnHover: true,
            draggable: true,
            progress: undefined,
          });
        } else {
          toast.error(
            "Temporarily unable refresh cache. Please try again in a few minutes.",
            {
              position: "top-right",
              autoClose: 3000,
              hideProgressBar: true,
              closeOnClick: true,
              pauseOnHover: true,
              draggable: true,
              progress: undefined,
            }
          );
        }
        setDisableCacheRefresh(false);
      }))
  };

  return (isAdmin ?
    <>
    <div className="container admin-container">
      <Grid
        container
        direction="row"
        className="admin-grid-container"
        spacing={3}
      >
        <Grid item xs={8} sm={8} md={8} lg={8}>
          <Typography variant="h4" component="h1" className="admin-title">
            Admin Dashboard
          </Typography>
          
        </Grid>
        <Grid item xs={4} sm={4} md={4} lg={4}>
          <button onClick={() => refreshRedisCache()} className="refresh-cache"
            disabled={disableCacheRefresh}>
          <FontAwesomeIcon icon={faSyncAlt} size='1x' style={{marginRight:'5px'}} />
           Refresh Cache  
          </button>
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={3} sx={{ m: 1 }}>
          <Card>
            <CardActionArea>
              <CardContent onClick={() => dispatch(push(`/foi/admin/divisions`))}>
                <Typography variant="h5" component="h2">
                  Divisions
                </Typography>
              </CardContent>
            </CardActionArea>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={3} sx={{ m: 1 }} className="disable-cursor">
          <Card>
            <CardActionArea>
              <CardContent onClick={() => console.log("manage stages")} disabled={true}>
                <Typography variant="h5" component="h2">
                  Stages
                </Typography>
              </CardContent>
            </CardActionArea>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={3} sx={{ m: 1 }} className="disable-cursor">
          <Card>
            <CardActionArea>
              <CardContent disabled={true}
                onClick={() => console.log("manage applicant categories")}
              >
                <Typography variant="h5" component="h2">
                  Applicant Categories
                </Typography>
              </CardContent>
            </CardActionArea>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={3} sx={{ m: 1 }} className="disable-cursor">
          <Card>
            <CardActionArea>
              <CardContent onClick={() => console.log("manage program areas")} disabled={true}>
                <Typography variant="h5" component="h2">
                  Program Areas
                </Typography>
              </CardContent>
            </CardActionArea>
          </Card>
        </Grid>
      </Grid>
    </div>
    </> : 
    <Loading />
  );
};

export default Admin;
