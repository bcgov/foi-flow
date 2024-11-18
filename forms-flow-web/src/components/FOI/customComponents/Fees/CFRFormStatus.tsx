import { MenuItem, TextField } from "@mui/material"
import Tooltip from '../../customComponents/Tooltip/Tooltip';

export const CFRFormStatus = ({
  formData,
  handleStatusChange,
  cfrStatusDisabled,
  isNewCFRForm,
  formHistory,
  handleTextChanges,
  isMinistry,
  requestState,
  StateEnum
}: any) => {
  const CFRStatuses = [
    {
      value: 'init',
      label: 'Select CFR Form Status',
      disabled: true,
    },
    {
      value: 'review',
      label: 'In Review with IAO',
      disabled: false,
    },
    {
      value: 'clarification',
      label: 'Needs Clarification with Ministry',
      disabled: isMinistry
    },
    {
      value: 'approved',
      label: 'Approved',
      disabled: isMinistry,
    },
  ];

  const reasons = [
    {
      value: 'init',
      label: 'Select Reason',
      disabled: true
    },
    {
      value: 'narrowedrequest',
      label: 'Narrowed Request',
      disabled: false,
    },
    {
      value: 'revisedfeeestimate',
      label: 'Revised Fee Estimate',
      disabled: false,
    }
  ];

  const tooltipReasons = {
    "title": "Reasons",
    "content": [
      <div className="toolTipContent">
        <p>Select 'Narrowed Request' when the applicant has narrowed their request. Select 'Revised Fee Estimate'
          when the request has not been narrowed but the estimated hours have changed.</p>
      </div>]
  };
  return (
    <>
      {<div className='foi-assigned-to-container'>
                    <div className='foi-assigned-to-inner-container' id="cfrstatuscontainer">
                      <TextField
                        id="cfrStatus"
                        label={"CFR Status"}
                        inputProps={{ "aria-labelledby": "cfrStatus-label"}}
                        InputLabelProps={{ shrink: true }}
                        select
                        name="formStatus"
                        value={formData?.formStatus}
                        onChange={handleStatusChange}
                        variant="outlined"
                        fullWidth
                        required
                        disabled={cfrStatusDisabled()}
                      >
                        {CFRStatuses.map((option: any) => (
                        <MenuItem
                          key={option.value}
                          value={option.value}
                          disabled={option.disabled}
                        >
                          {option.label}
                        </MenuItem>
                        ))}
                      </TextField>
                    </div>
                    {(isNewCFRForm || (formHistory?.length > 0 && (formData?.cfrfeeid !== formHistory[0]?.cfrfeeid)) || formHistory?.length > 1)  &&
                    <>
                      <div className='foi-assigned-to-inner-container'>
                        <TextField
                          id="reasons"
                          label={"Reason for Creating New CFR Form"}
                          inputProps={{ "aria-labelledby": "reasons-label"}}
                          InputLabelProps={{ shrink: true }}
                          placeholder={"Select Reason"}
                          select
                          name="reason"
                          value={formData?.reason}
                          onChange={handleTextChanges}
                          variant="outlined"
                          fullWidth
                          required
                          error={formData?.reason === 'init'}
                          disabled={!isMinistry || requestState === StateEnum.peerreview.name || formData?.formStatus === 'approved'}
                        >
                          {reasons.map((option: any) => (
                          <MenuItem
                            key={option.value}
                            value={option.value}
                            disabled={option.disabled}
                          >
                            {option.label}
                          </MenuItem>
                          ))}
                        </TextField>
                        <div className="cfrform-floatRight cfrform-reasons">
                          <Tooltip content={tooltipReasons} position={""}/>
                          <p className="hideContent" id="popup-7">Information7</p>
                        </div>
                      </div>
                    </>
                    }
                  </div>}
    </>
  )
}