import React from 'react';
import './datetimewithlegend.scss';

import { makeStyles } from '@material-ui/core/styles';
import TextField from '@material-ui/core/TextField';
import moment from 'moment';

const useStyles = makeStyles((theme) => ({
  container: {
    display: 'flex',
    flexWrap: 'wrap',
  },
  textField: {
    marginLeft: theme.spacing(1),
    marginRight: theme.spacing(1),
    width: 200,
  },
}));


const DateTimeWithLegend = React.memo((props) => {
  const classes = useStyles();
   const dateData = props.dateData;
   const labelValue = dateData.label;   
   const [selectedDate, setSelectedDate] = React.useState(moment(new Date(dateData.value)).format("YYYY-MM-DD"));
  
   const handleDateChange = (event) => {
     setSelectedDate(event.target.value);
   };    
     return (
        // <form className={classes.container} noValidate>
            <TextField                
                label={labelValue}
                type="date"                
                // defaultValue={dateData.value}                
                value={selectedDate}        
                className={classes.textField}
                onChange={handleDateChange}
                InputLabelProps={{
                shrink: true,
                }}
                InputProps={{inputProps: { min: "2001-04-21", max: "2020-05-04"} }}
                variant="outlined"
                disabled={dateData.disabled}
                required={dateData.required}
            />
    // </form>

    
    );
  });

export default DateTimeWithLegend;