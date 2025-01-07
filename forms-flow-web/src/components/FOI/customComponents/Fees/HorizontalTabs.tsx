import { Grid, Paper, Stack } from '@mui/material';
import { ClickableChip } from '../../Dashboard/utils';
import { FeesSubtabValues } from './types';

export const HorizontalTabs = ({ selectedSubtab, handleSubtabChange, showApplicationFeeTab, showCFRTab }: {selectedSubtab: string, handleSubtabChange: (arg0: FeesSubtabValues) => void, showApplicationFeeTab: boolean, showCFRTab: boolean,}) => {
    return (
      <Grid item container alignItems="center" xs={12} sx={{ display: "inline-block"}}>
        <Paper
            component={Grid}
            sx={{
                border: "1px solid #38598A",
                color: "#38598A", 
                maxWidth:"100%",
                padding: "0.5em"
            }}
            direction="row"
            container
            item
            xs={12}
            elevation={0}
        >
          <Grid
              item
              container
              alignItems="flex-start"
              xs={true}
              sx={{
                  width: "300px",
                  maxWidth: "300px !important",
              }}
          >
            <Stack direction="row" sx={{ overflowX: "hidden" }} spacing={1}>
              {showApplicationFeeTab && <ClickableChip
                  id="applicationFee"
                  key={`application-fee`}
                  label={"APPLICATION FEE"}
                  color="primary"
                  size="small"
                  onClick={()=>{handleSubtabChange(FeesSubtabValues.APPLICATIONFEE)}}
                  clicked={selectedSubtab == FeesSubtabValues.APPLICATIONFEE}
              />}
              {(showCFRTab && <ClickableChip
                  id="cfr-form"
                  key={`cfr-form`}
                  label={"PROCESSING FEE"}
                  color="primary"
                  size="small"
                  onClick={()=>{handleSubtabChange(FeesSubtabValues.CFRFORM)}}
                  clicked={selectedSubtab == FeesSubtabValues.CFRFORM}
              />)}
            </Stack>
          </Grid>
        </Paper>
      </Grid>)
  }