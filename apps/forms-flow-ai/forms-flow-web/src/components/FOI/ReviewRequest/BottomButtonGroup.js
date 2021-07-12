import React from 'react';
import './bottombuttongroup.scss';
import { makeStyles } from '@material-ui/core/styles';
import { useDispatch } from "react-redux";
import {push} from "connected-react-router";

const useStyles = makeStyles((theme) => ({
    root: {
      width: '100%',
      marginTop:'30px',
      marginBottom:'50px'
    },
    heading: {
      fontSize: theme.typography.pxToRem(15),
      fontWeight: theme.typography.fontWeightRegular,
    },
    btndisabled: {
      border: 'none',
      backgroundColor: '#eceaea',
      color: '#FFFFFF'
    },
    btnenabled: {
      border: 'none',
      backgroundColor: '#38598A',
      color: '#FFFFFF'
    },
    btnsecondaryenabled: {
      border: '1px solid #38598A',
      backgroundColor: '#FFFFFF',
      color: '#38598A'
    }
  }));

const BottomButtonGroup = React.memo(({selectedCategory}) => {
    const classes = useStyles();
    const dispatch = useDispatch();
    const returnToQueue = () => {
      dispatch(push(`/foi/dashboard`));
    }
     return (
    <div className={classes.root}>
      <div className="foi-bottom-button-group">
      <button type="button" className={`btn btn-bottom ${selectedCategory === '' ? classes.btndisabled : classes.btnenabled}`} disabled={selectedCategory===''} >Open Request</button>
      
      <button type="button" className={`btn btn-bottom ${selectedCategory === '' ? classes.btndisabled : classes.btnsecondaryenabled}`} disabled={selectedCategory===''}>Save</button>
      <button type="button" className={`btn btn-bottom ${classes.btnsecondaryenabled}`} onClick={returnToQueue} >Return to Queue</button>
      
      </div>
    </div>
    );
  });

export default BottomButtonGroup;