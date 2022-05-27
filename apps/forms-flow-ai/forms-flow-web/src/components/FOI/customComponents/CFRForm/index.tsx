import TextField from '@mui/material/TextField';
import MenuItem from '@mui/material/MenuItem';
import './index.scss'
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Box from '@mui/material/Box';

type CFRForm = {
  requestNumber: string;
}

export const CFRForm = ({  
  requestNumber,  
}: CFRForm) => {

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
    <div className="foi-review-container">
    <Box
      component="form"
      sx={{
        '& .MuiTextField-root': { m: 1 },
      }}
      autoComplete="off"
    ><div className="foi-request-form">
    <div style={{marginTop: 20}}></div>
    <div className="container foi-review-request-container">
      <div className="foi-request-review-header-row1">
        <div className="col-9 foi-request-number-header">
          <h3 className="foi-review-request-text">{requestNumber}</h3>
        </div>      
        <div className="col-3">
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
      <div className='request-accordian'>
        <Accordion defaultExpanded={true}>
          <AccordionSummary className="accordionSummary" expandIcon={<ExpandMoreIcon />} id="applicantDetails-header">
            <Typography className="heading">OVERALL FEES ESTIMATE</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <div className="row foi-details-row">
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="amountpaid"
                  label="Amount Paid"
                  inputProps={{ "aria-labelledby": "amountpaid-label"}}
                  InputLabelProps={{ shrink: true }}
                  variant="outlined"
                  placeholder="hr"
                  // value={applicantFirstNameText}
                  fullWidth
                  // onChange={handleFirtNameChange}
                  // required={true}
                  // disabled={disableInput}
                  // error={applicantFirstNameText === ""}
                />
              </div>
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="totalamountdue"
                  label="Total Amount Due"
                  inputProps={{ "aria-labelledby": "totalamountdue-label"}}
                  InputLabelProps={{ shrink: true }}
                  // value={applicantMiddleNameText}
                  variant="outlined"
                  placeholder="hr"
                  fullWidth
                  // disabled={disableInput}
                  // onChange={handleMiddleNameChange}
                />
              </div>
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-5 foi-details-col">
                <span className="formLabel">Balance Remaining</span>
              </div>
              <div className="col-lg-2 foi-details-col">
                <span className="formLabel">$00.00</span>
              </div>
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-12 foi-details-col">
                <hr />
              </div>
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-12 foi-details-col">
                <div className="formLabel">Locating/Tetrieving - this includes searching all relevant sources.</div>
              </div>
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="estimatedlocating"
                  label="Estimated Hours"
                  inputProps={{ "aria-labelledby": "estimatedlocating-label"}}
                  InputLabelProps={{ shrink: true }}
                  // value={applicantLastNameText}
                  variant="outlined"
                  placeholder="hr"
                  fullWidth
                  // onChange={handleLastNameChange}
                  // required={true}
                  // disabled={disableInput}
                  // error={applicantLastNameText === ""}
                />
              </div>
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="actuallocating"
                  label="Actual Hours"
                  inputProps={{ "aria-labelledby": "actuallocating-label"}}
                  InputLabelProps={{ shrink: true }}
                  // value={organizationText}
                  variant="outlined"
                  placeholder="hr"
                  fullWidth
                  // disabled={disableInput}
                  // onChange={handleOrganizationChange}
                />
              </div>
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-12 foi-details-col">
                <div className="formLabel">
                  Producing - this only applies where you are creating records from other sources* (e.g. developing a program to create new records from a database)
                </div>
              </div>
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="estimatedproducing"
                  label="Estimated Hours"
                  inputProps={{ "aria-labelledby": "estimatedproducing-label"}}
                  InputLabelProps={{ shrink: true }}
                  // value={selectedCategory}
                  // onChange={handleCategoryOnChange}
                  // input={<Input />}
                  variant="outlined"
                  placeholder="hr"
                  fullWidth
                  // required
                  // disabled={disableInput || disableFieldForMinistryRequest}
                  // error={selectedCategory.toLowerCase().includes("select")}
                >
                  {/* {menuItems} */}
                </TextField>
              </div>
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="actualproducing"
                  label="Actual Hours"
                  inputProps={{ "aria-labelledby": "actualproducing-label"}}
                  InputLabelProps={{ shrink: true }}
                  // value={organizationText}
                  variant="outlined"
                  placeholder="hr"
                  fullWidth
                  // disabled={disableInput}
                  // onChange={handleOrganizationChange}
                />
              </div>
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-12 foi-details-col">
                <div className="formLabel">
                  Preparing - this may include time spent by IAO (for electronic records) or the Ministry (for hardcopy records)
                </div>
              </div>
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="estimatedpreparing"
                  label="Estimated Hours"
                  inputProps={{ "aria-labelledby": "estimatedpreparing-label"}}
                  InputLabelProps={{ shrink: true }}
                  // value={selectedCategory}
                  // onChange={handleCategoryOnChange}
                  // input={<Input />}
                  variant="outlined"
                  placeholder="hr"
                  fullWidth
                  // required
                  // disabled={disableInput || disableFieldForMinistryRequest}
                  // error={selectedCategory.toLowerCase().includes("select")}
                >
                  {/* {menuItems} */}
                </TextField>
              </div>
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="actualpreparing"
                  label="Actual Hours"
                  inputProps={{ "aria-labelledby": "actualpreparing-label"}}
                  InputLabelProps={{ shrink: true }}
                  // value={organizationText}
                  variant="outlined"
                  placeholder="hr"
                  fullWidth
                  // disabled={disableInput}
                  // onChange={handleOrganizationChange}
                />
              </div>
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-12 foi-details-col">
                <div className="formLabel">
                  Volume - for electronic records please provide the estimated number of files and for hardcopy records please continue to provide the number of pages
                </div>
              </div>
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="estimatedelectronic"
                  label="Electronic Estimated Pages"
                  inputProps={{ "aria-labelledby": "estimatedelectronic-label"}}
                  InputLabelProps={{ shrink: true }}
                  // value={selectedCategory}
                  // onChange={handleCategoryOnChange}
                  // input={<Input />}
                  variant="outlined"
                  placeholder="pgs"
                  fullWidth
                  // required
                  // disabled={disableInput || disableFieldForMinistryRequest}
                  // error={selectedCategory.toLowerCase().includes("select")}
                >
                  {/* {menuItems} */}
                </TextField>
                <TextField
                  id="estimatedhardcopy"
                  label="Hardcopy Estimated Pages"
                  inputProps={{ "aria-labelledby": "estimatedhardcopy-label"}}
                  InputLabelProps={{ shrink: true }}
                  // value={selectedCategory}
                  // onChange={handleCategoryOnChange}
                  // input={<Input />}
                  variant="outlined"
                  placeholder="pgs"
                  fullWidth
                  // required
                  // disabled={disableInput || disableFieldForMinistryRequest}
                  // error={selectedCategory.toLowerCase().includes("select")}
                >
                  {/* {menuItems} */}
                </TextField>
              </div>
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="actualelectronic"
                  label="Electronic Actual Pages"
                  inputProps={{ "aria-labelledby": "actualelectronic-label"}}
                  InputLabelProps={{ shrink: true }}
                  // value={organizationText}
                  variant="outlined"
                  placeholder="pgs"
                  fullWidth
                  // disabled={disableInput}
                  // onChange={handleOrganizationChange}
                />
                <TextField
                  id="actualhardcopy"
                  label="Hardcopy Actual Pages"
                  inputProps={{ "aria-labelledby": "actualhardcopy-label"}}
                  InputLabelProps={{ shrink: true }}
                  // value={organizationText}
                  variant="outlined"
                  placeholder="pgs"
                  fullWidth
                  // disabled={disableInput}
                  // onChange={handleOrganizationChange}
                />
              </div>
            </div>
          </AccordionDetails>
        </Accordion>
      </div> 
      <div className='request-accordian'>
        <Accordion defaultExpanded={true}>
          <AccordionSummary className="accordionSummary" expandIcon={<ExpandMoreIcon />} id="applicantDetails-header">
            <Typography className="heading">OVERALL CLARIFICATION SUGGESTIONS</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <div className="row foi-details-row">
              <div className="col-lg-12 foi-details-col">
                <TextField
                  id="combinedsuggestions"
                  // required={true}
                  label="Combined suggestions for futher clarifications   "
                  multiline
                  rows={4}
                  // value={requestDescriptionText}
                  variant="outlined"
                  InputLabelProps={{ shrink: true, }} 
                  // onChange={handleRequestDescriptionChange}
                  // error={requestDescriptionText===""}
                  fullWidth
                  // disabled={disableInput}
                />
              </div>
            </div>
          </AccordionDetails>
        </Accordion>
      </div> 
    </div>
  </div></Box>
  </div>
  );
}
