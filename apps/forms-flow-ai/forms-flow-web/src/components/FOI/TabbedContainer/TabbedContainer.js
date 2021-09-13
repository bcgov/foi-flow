import React, { useEffect } from "react";
import PropTypes from 'prop-types';
import { makeStyles } from '@material-ui/core/styles';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import Typography from '@material-ui/core/Typography';
import Box from '@material-ui/core/Box';
import FOIRequest from "../FOIRequest";
import { StateDropDown } from '../customComponents';


import "./TabbedContainer.scss"

const TabbedContainer = React.memo((props) => {

  function TabPanel(props) {
    const { children, value, index, ...other } = props;

    return (
      <div
        role="tabpanel"
        hidden={value !== index}
        id={`vertical-tabpanel-${index}`}
        aria-labelledby={`vertical-tab-${index}`}
        {...other}
      >
        {value === index && (
          <Box p={3}>
            <Typography component={'span'}>{children}</Typography>
          </Box>
        )}
      </div>
    );
  }


  TabPanel.propTypes = {
    children: PropTypes.node,
    index: PropTypes.any.isRequired,
    value: PropTypes.any.isRequired,
  };

  function a11yProps(index) {
    return {
      id: `vertical-tab-${index}`,
      'aria-controls': `vertical-tabpanel-${index}`,
    };
  }

  const useStyles = makeStyles((theme) => ({
    root: {
      flexGrow: 1,
      backgroundColor: theme.palette.background.paper,
      display: 'flex',
      height: 224,
    },
    tabs: {
      borderRight: `1px solid ${theme.palette.divider}`,
    },
  }));

  const classes = useStyles();
  const [headerBG, setheaderBG] = React.useState("foitabheaderdefaultBG");
  const [_requestStatus, setRequestStatus] = React.useState("Unopened");

  const [value, setValue] = React.useState(0);

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  const foitabheaderBG = "foitabheadercollection "+ headerBG
  const handlestatusudpate = (_daysRemaining,_status)=>{  
    if(_status == "Open")
    {      
      setheaderBG("foitabheaderOpenBG");
      setRequestStatus(_daysRemaining +" Days Remaining")            
    }
    else{      
      setRequestStatus(_status)
    }
        
  }
  
  return (

    <div className="foiformcontent">
      <div className="foitabbedContainer">

        <div className={foitabheaderBG}>
          <div className="foileftpanelheader">
            <h1><a href="/foi/dashboard">FOI</a></h1>
          </div>
          <div className="foileftpaneldropdown">
            <StateDropDown requestStatus={_requestStatus}/>
          </div>
          <Tabs
            orientation="vertical"
            value={value}
            onChange={handleChange}
            aria-label="Vertical tabs example"
            className={classes.tabs}
          >

            <Tab label="Request" {...a11yProps(0)} />
            <Tab label="Correspondence Log" {...a11yProps(1)} />
            <Tab label="Option 3" {...a11yProps(2)} />
            <Tab label="Option 4" {...a11yProps(3)} />
            <Tab label="Option 5" {...a11yProps(4)} />
            
          </Tabs>
          <h4 className="foileftpanelstatus">{_requestStatus.toLowerCase().includes("days")? _requestStatus: ""}</h4>
        </div>
        <div className="foitabpanelcollection">
          <TabPanel value={value} index={0}>
            <FOIRequest handlestatusudpate={handlestatusudpate}/>
          </TabPanel>
          <TabPanel value={value} index={1}>
            
            <div className="container foi-review-request-container">
              <div className="foi-review-container">
                <form className="makeStyles-root-52 foi-request-form">
                  <div className="tabcontent">
                  </div>
                </form>


              </div>

            </div>
          </TabPanel>
          <TabPanel value={value} index={2}>
          <div className="container foi-review-request-container">
              <div className="foi-review-container">
                <form className="makeStyles-root-52 foi-request-form">
                  <div className="tabcontent">
                  </div>
                </form>


              </div>

            </div>
          </TabPanel>
          <TabPanel value={value} index={3}>
          <div className="container foi-review-request-container">
              <div className="foi-review-container">
                <form className="makeStyles-root-52 foi-request-form">
                  <div className="tabcontent">
                  </div>
                </form>


              </div>

            </div>
          </TabPanel>
          <TabPanel value={value} index={4}>
          <div className="container foi-review-request-container">
              <div className="foi-review-container">
                <form className="makeStyles-root-52 foi-request-form">
                  <div className="tabcontent">
                  </div>
                </form>


              </div>

            </div>
          </TabPanel>
        
        </div>
      </div>
    </div>

  );


});

export default TabbedContainer