import TextField from '@material-ui/core/TextField';
import MenuItem from '@mui/material/MenuItem';
import { makeStyles } from "@material-ui/core/styles";


const useStyles = makeStyles((_theme) => ({
  container: {
    paddingLeft: '5%',
    paddingRight: '5%',
    marginTop: '20px',
  },
}));

type CFRForm = {
  requestNumber: string;
}

export const CFRForm = ({  
  requestNumber,  
}: CFRForm) => {
  
  const classes = useStyles();
  const CFRStatuses = [
    {
      value: 'review',
      label: 'In Review'
    },
    {
      value: 'approved',
      label: 'Approved'
    },
    {
      value: 'clarification',
      label: 'Clarification'
    },
  ];
  
  return (    
    <div className={classes.container}>
      <div className="foi-request-review-header-row1">
        <div className="col-9 foi-request-number-header">
          <h3 className="foi-review-request-text">{requestNumber}</h3>
        </div>      
        <div className="col-3 addcommentBox">
          <TextField
            id="cfrStatus"
            label={"CFR Status"}
            inputProps={{ "aria-labelledby": "cfrStatus-label"}}
            InputLabelProps={{ shrink: true }}
            select
            // value={selectedAssignedTo}
            // onChange={handleAssignedToOnChange}
            variant="outlined"
            fullWidth
            required
            // disabled={disableInput}
            // error={selectedAssignedTo.toLowerCase().includes("unassigned")}
          >
            {CFRStatuses.map((option) => (
            <MenuItem key={option.value} value={option.value}>
              {option.label}
            </MenuItem>
            ))}
          </TextField>
        </div>

        
      </div>
    </div>
  );
}

export default CFRForm