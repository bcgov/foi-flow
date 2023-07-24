import React from 'react';
import Dialog from '@material-ui/core/Dialog';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import type { modalParams } from './types';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import TextField from '@mui/material/TextField';
import InputAdornment from "@mui/material/InputAdornment";
import { paymentMethods } from './util';
import MenuItem from '@mui/material/MenuItem';

export const CFRFormHistoryModal = React.memo(({
  modalOpen,
  handleClose,
  formHistory,
  isMinistry
}: modalParams) => {

  return (

    <Dialog
      open={modalOpen}
      onClose={handleClose}
      aria-labelledby="state-change-dialog-title"
      aria-describedby="state-change-dialog-description"
      maxWidth={'md'}
      fullWidth={true}
      // id="state-change-dialog"
      >
      <DialogTitle disableTypography id="state-change-dialog-title">
        <h2 className="state-change-header cfr-history-modal-header">Form History</h2>
        <IconButton className="title-col3" onClick={handleClose}>
          <i className="dialog-close-button">Close</i>
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      <DialogContent className={'dialog-content-nomargin'}>
        {formHistory.map((entry: any, index: number) => {
          return <div className='request-accordian' key={entry.cfrfeeid}>
            <Accordion defaultExpanded={false} className='history-entry-accordion'>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography className="history-entry-title">CFR Form - Version {formHistory.length - index} - {entry['cfrformreason.description'] ? entry['cfrformreason.description'] : 'Original'} 
                </Typography>
                <Typography className="history-entry-username"> {entry.version_createdby} - {entry.version_created_at}</Typography>
              </AccordionSummary>

                <AccordionDetails
                  sx={{
                    '& .MuiTextField-root': { my: 1, mx: 0 },
                  }}
                >
                  <div className="row foi-details-row">
                    <div className="col-lg-12 foi-details-col">
                      <div className="historyLabel">
                        OVERALL FEE ESTIMATE
                      </div>
                    </div>
                  </div>
                  {!isMinistry && <div className="row foi-details-row">
                    <div className="col-lg-6 foi-details-col">
                      <TextField
                        id="estimatePaymentMethod"
                        label="Estimate Payment Method"
                        inputProps={{
                          "aria-labelledby": "estimatePaymentMethod-label"
                        }}
                        InputLabelProps={{ shrink: true }}
                        variant="outlined"
                        select
                        name="estimatePaymentMethod"
                        value={entry.feedata.estimatepaymentmethod}
                        fullWidth
                        disabled={true}
                      >
                        {paymentMethods.map((option) => (
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
                    <div className="col-lg-6 foi-details-col">
                      <TextField
                        id="balancePaymentMethod"
                        label="Balance Payment Method"
                        inputProps={{
                          "aria-labelledby": "balancePaymentMethod-label"
                        }}
                        InputLabelProps={{ shrink: true }}
                        select
                        variant="outlined"
                        name="balancePaymentMethod"
                        value={entry.feedata.balancepaymentmethod}
                        fullWidth
                        disabled={true}
                        >
                          {paymentMethods.map((option) => (
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
                  </div>}
                  <div className="row foi-details-row">
                    <div className="col-lg-6 foi-details-col">
                      <TextField
                        id="amountpaid"
                        label="Amount Paid"
                        inputProps={{
                          "aria-labelledby": "amountpaid-label"
                        }}
                        InputProps={{
                          startAdornment: <InputAdornment position="start">$</InputAdornment>
                        }}
                        InputLabelProps={{ shrink: true }}
                        variant="outlined"
                        name="amountPaid"
                        type="number"
                        value={parseFloat(entry.feedata.amountpaid).toFixed(2)}
                        fullWidth
                        disabled={true}
                      />
                    </div>
                    <div className="col-lg-6 foi-details-col">
                      <TextField
                        id="balanceremaining"
                        label="Balance Remaining"
                        inputProps={{
                          "aria-labelledby": "balanceremaining-label"
                        }}
                        InputProps={{
                          startAdornment: <InputAdornment position="start">$</InputAdornment>
                        }}
                        InputLabelProps={{ shrink: true }}
                        name="balanceRemaining"
                        value={parseFloat(entry.feedata.balanceremaining).toFixed(2)}
                        variant="outlined"
                        placeholder="0"
                        fullWidth
                        disabled={true}
                      />
                    </div>
                  </div>
                  <div className="row foi-details-row">
                    <div className="col-lg-4 foi-details-col">
                      <span className="formLabel">Estimated Total</span>
                    </div>
                    <div className="col-lg-2 foi-details-col">
                      <span className="formLabel">{"$"+parseFloat(entry.feedata.estimatedtotaldue).toFixed(2)}</span>
                    </div>
                    <div className="col-lg-4 foi-details-col">
                      <span className="formLabel">Actual Total</span>
                    </div>
                    <div className="col-lg-2 foi-details-col">
                      <span className="formLabel">{"$"+parseFloat(entry.feedata.actualtotaldue).toFixed(2)}</span>
                    </div>
                  </div>
                  <div className="row foi-details-row">
                    <div className="col-lg-6 foi-details-col">
                      <TextField
                        id="feewaiver"
                        label="Fee Waiver Amount"
                        inputProps={{
                          "aria-labelledby": "feewaiver-label"
                        }}
                        InputProps={{
                          startAdornment: <InputAdornment position="start">$</InputAdornment>
                        }}
                        InputLabelProps={{ shrink: true }}
                        variant="outlined"
                        name="feewaiverAmount"
                        type="number"
                        value={parseFloat(entry.feedata.feewaiveramount).toFixed(2)}
                        fullWidth
                        disabled={true}
                      />
                    </div>
                    <div className="col-lg-6 foi-details-col">
                      <TextField
                        id="refund"
                        label="Refund Amount"
                        inputProps={{
                          "aria-labelledby": "refund-label"
                        }}
                        InputProps={{
                          startAdornment: <InputAdornment position="start">$</InputAdornment>
                        }}
                        InputLabelProps={{ shrink: true }}
                        name="refundAmount"
                        value={parseFloat(entry.feedata.refundamount).toFixed(2)}
                        variant="outlined"
                        placeholder="0"
                        fullWidth
                        disabled={true}
                      />
                    </div>
                  </div>
                  <div className="row foi-details-row">
                    <div className="col-lg-12 foi-details-col">
                      <hr />
                    </div>
                  </div>
                  <div className="row foi-details-row">
                    <div className="col-lg-12 foi-details-col">
                      <div className="historyLabel">LOCATING/RETRIEVING</div>
                    </div>
                  </div>
                  <div className="row foi-details-row">
                    <div className="col-lg-6 foi-details-col">
                      <TextField
                        id="estimatedlocating"
                        label="Estimated Hours"
                        inputProps={{
                          "aria-labelledby": "estimatedlocating-label"
                        }}
                        InputProps={{
                          endAdornment: <InputAdornment position="end">hr(s)</InputAdornment>
                        }}
                        InputLabelProps={{ shrink: true }}
                        name="locating"
                        value={entry.feedata.estimatedlocatinghrs}
                        variant="outlined"
                        fullWidth
                        type="number"
                        disabled={true}
                      />
                    </div>
                    <div className="col-lg-6 foi-details-col">
                      <TextField
                        id="actuallocating"
                        label="Actual Hours"
                        inputProps={{
                          "aria-labelledby": "actuallocating-label"
                        }}
                        InputProps={{
                          endAdornment: <InputAdornment position="end">hr(s)</InputAdornment>
                        }}
                        InputLabelProps={{ shrink: true }}
                        name="locating"
                        value={entry.feedata.actuallocatinghrs}

                        variant="outlined"
                        fullWidth
                        type="number"
                        disabled={true}
                      />
                    </div>
                  </div>
                  <div className="row foi-details-row">
                    <div className="col-lg-12 foi-details-col">
                      <div className="historyLabel">
                        PRODUCING
                      </div>
                    </div>
                  </div>
                  <div className="row foi-details-row">
                    <div className="col-lg-6 foi-details-col">
                      <TextField
                        id="estimatedproducing"
                        label="Estimated Hours"
                        inputProps={{
                          "aria-labelledby": "estimatedproducing-label"
                        }}
                        InputProps={{
                          endAdornment: <InputAdornment position="end">hr(s)</InputAdornment>
                        }}
                        InputLabelProps={{ shrink: true }}
                        name="producing"
                        value={entry.feedata.estimatedproducinghrs}

                        variant="outlined"
                        fullWidth
                        type="number"
                        disabled={true}
                      >
                      </TextField>
                    </div>
                    <div className="col-lg-6 foi-details-col">
                      <TextField
                        id="actualproducing"
                        label="Actual Hours"
                        inputProps={{
                          "aria-labelledby": "actualproducing-label"
                        }}
                        InputProps={{
                          endAdornment: <InputAdornment position="end">hr(s)</InputAdornment>
                        }}
                        InputLabelProps={{ shrink: true }}
                        name="producing"
                        value={entry.feedata.actualproducinghrs}
                        variant="outlined"
                        fullWidth
                        type="number"
                        disabled={true}
                      />
                    </div>
                  </div>
                  <div className="row foi-details-row">
                    <div className="col-lg-12 foi-details-col">
                      <div className="historyLabel">
                        PREPARING
                      </div>
                    </div>
                  </div>
                  <div className="row foi-details-row">
                    <div className="col-lg-3 foi-details-col">
                      <TextField
                        id="estimatediaopreparing"
                        label="Estimated Hours IAO"
                        inputProps={{
                          "aria-labelledby": "estimatedpreparing-label"
                        }}
                        InputProps={{
                          endAdornment: <InputAdornment position="end">hr(s)</InputAdornment>
                        }}
                        InputLabelProps={{ shrink: true }}
                        name="iaoPreparing"
                        value={entry.feedata.estimatediaopreparinghrs}
                        variant="outlined"
                        fullWidth
                        type="number"
                        disabled={true}
                      >
                        {/* {menuItems} */}
                      </TextField>
                    </div>
                    <div className="col-lg-3 foi-details-col">
                      <TextField
                        id="estimatedministrypreparing"
                        label="Estimated Hours Ministry"
                        inputProps={{
                          "aria-labelledby": "estimatedministrypreparing-label"
                        }}
                        InputProps={{
                          endAdornment: <InputAdornment position="end">hr(s)</InputAdornment>
                        }}
                        InputLabelProps={{ shrink: true }}
                        name="ministryPreparing"
                        value={entry.feedata.estimatedministrypreparinghrs}

                        variant="outlined"
                        fullWidth
                        type="number"
                        disabled={true}
                      >
                        {/* {menuItems} */}
                      </TextField>
                    </div>
                    <div className="col-lg-3 foi-details-col">
                      <TextField
                        id="actualiaopreparing"
                        label="Actual Hours IAO"
                        inputProps={{
                          "aria-labelledby": "actualiaopreparing-label"
                        }}
                        InputProps={{
                          endAdornment: <InputAdornment position="end">hr(s)</InputAdornment>
                        }}
                        InputLabelProps={{ shrink: true }}
                        name="iaoPreparing"
                        value={entry.feedata.actualiaopreparinghrs}
                        variant="outlined"
                        fullWidth
                        type="number"
                        disabled={true}
                      />
                    </div>
                    <div className="col-lg-3 foi-details-col">
                      <TextField
                        id="actualministrypreparing"
                        label="Actual Hours Ministry"
                        inputProps={{
                          "aria-labelledby": "actualministrypreparing-label"
                        }}
                        InputProps={{
                          endAdornment: <InputAdornment position="end">hr(s)</InputAdornment>
                        }}
                        InputLabelProps={{ shrink: true }}
                        name="ministryPreparing"
                        value={entry.feedata.actualministrypreparinghrs}
                        variant="outlined"
                        fullWidth
                        type="number"
                        disabled={true}
                      />
                    </div>
                  </div>
                  <div className="row foi-details-row">
                    <div className="col-lg-12 foi-details-col">
                      <div className="historyLabel">
                        VOLUME
                      </div>
                    </div>
                  </div>
                  <div className="row foi-details-row">
                    <div className="col-lg-6 foi-details-col">
                      <TextField
                        id="estimatedelectronic"
                        label="Electronic Estimated Files"
                        inputProps={{
                          "aria-labelledby": "estimatedelectronic-label"
                        }}
                        InputProps={{
                          endAdornment: <InputAdornment position="end">file(s)</InputAdornment>
                        }}
                        InputLabelProps={{ shrink: true }}
                        name="electronicPages"
                        value={entry.feedata.estimatediaopreparinghrs}
                        variant="outlined"
                        fullWidth
                        type="number"
                        disabled={true}
                      >
                      </TextField>
                      <TextField
                        id="estimatedhardcopy"
                        label="Hardcopy Estimated Pages"
                        inputProps={{
                          "aria-labelledby": "estimatedelectronic-label"
                        }}
                        InputProps={{
                          endAdornment: <InputAdornment position="end">pg(s)</InputAdornment>
                        }}
                        InputLabelProps={{ shrink: true }}
                        name="hardcopyPages"
                        value={entry.feedata.estimatediaopreparinghrs}
                        variant="outlined"
                        fullWidth
                        type="number"
                        disabled={true}
                      >
                      </TextField>
                    </div>
                    <div className="col-lg-6 foi-details-col">
                      <TextField
                        id="actualelectronic"
                        label="Electronic Actual Files"
                        inputProps={{
                          "aria-labelledby": "estimatedelectronic-label"
                        }}
                        InputProps={{
                          endAdornment: <InputAdornment position="end">file(s)</InputAdornment>
                        }}
                        InputLabelProps={{ shrink: true }}
                        name="electronicPages"
                        value={entry.feedata.estimatedelectronicpages}
                        variant="outlined"
                        fullWidth
                        type="number"
                        disabled={true}
                      />
                      <TextField
                        id="actualhardcopy"
                        label="Hardcopy Actual Pages"
                        inputProps={{
                          "aria-labelledby": "estimatedelectronic-label"
                        }}
                        InputProps={{
                          endAdornment: <InputAdornment position="end">pg(s)</InputAdornment>
                        }}
                        InputLabelProps={{ shrink: true }}
                        name="hardcopyPages"
                        value={entry.feedata.estimatedelectronicpages}
                        variant="outlined"
                        fullWidth
                        type="number"
                        disabled={true}
                      />
                    </div>
                  </div>
                </AccordionDetails>
            </Accordion>
          </div>

        })}
        {/* <span className="confirmation-message">
          {modalMessage}
        </span> */}
      </DialogContent>
    </Dialog>
  )
})
