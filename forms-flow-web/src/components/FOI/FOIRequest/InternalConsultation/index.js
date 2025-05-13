import React, { useEffect } from "react";
import Accordion from '@material-ui/core/Accordion';
// import ExtensionDetailsBox from "./ExtensionDetailsBox"
import { StateEnum } from "../../../../constants/FOI/statusEnum";
import { AccordionDetails, AccordionSummary, Input, TextField, Typography } from "@material-ui/core";
import { makeStyles } from '@material-ui/styles';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import MultiMinistrySelector from '../../customComponents/MultiMinistrySelector';
import CustomSwitch from "./CustomSwitch";
import './internalConsultation.scss';
import { useSelector } from "react-redux";
import FOI_COMPONENT_CONSTANTS from '../../../../constants/FOI/foiComponentConstants';
import {isValidMinistryCode, countOfMinistrySelected} from '../utils';
import { formatDate } from "../../../../helper/FOI/helper";

const useStyles = makeStyles((_theme) => ({
      headingError: {
        color: "#ff0000"    
      },
      headingNormal: {
        color: "000000"
      },
      btndisabled: { 
        color: "#808080"
      },
      heading: {
        color: '#FFF',
        fontSize: '16px !important',
        fontWeight: 'bold !important'
      },
      accordionSummary: {
        flexDirection: 'row-reverse'
      }
  }));

  
const InternalConsultation = React.memo(
  ({
    programAreaList,
    requestDetails,
    requestState,
    handleInternalConsultationValues,
    handleInternalConsultInitialValues,
    createSaveRequestObject,
    disableInput
  }) => {
    const classes = useStyles();
    const [isChecked, setIsChecked] = React.useState(false);
    const [validation, setValidation] = React.useState({});
    var masterProgramAreaList = useSelector(state=> state.foiRequests.foiProgramAreaList);
    const [localProgramAreaList, setLocalProgramAreaList] = React.useState([])
    const [selectedSubjectCode, setSelectedSubjectCode] = React.useState("test");
    const [dueDate, setDueDate] = React.useState(!!requestDetails.toDate ? formatDate(new Date(requestDetails.toDate)): "");
    const subjectCodeList = useSelector(state=> state.foiRequests.foiSubjectCodeList);
    const handleSwitchChange = (checked) => {
      setIsChecked(checked);
    };

    useEffect(() => {
      setSelectedSubjectCode(getSubjectCode())  
      if(Object.entries(requestDetails).length !== 0){
        setSelectedMinistries();
      }
    },[requestDetails])

    const getSubjectCode = () => {
      if (requestDetails?.subjectCode)
        return requestDetails.subjectCode;
      return "Select Subject Code (if required)"
    }

  
    const handleUpdatedMasterProgramAreaList = (updatedProgramAreaList) => {
      handleInternalConsultationValues(countOfMinistrySelected(updatedProgramAreaList) === 1 && updatedProgramAreaList.some(programArea =>
        (programArea.isChecked && isValidMinistryCode(programArea.bcgovcode, masterProgramAreaList))), 
        FOI_COMPONENT_CONSTANTS.IS_PROGRAM_AREA_SELECTED);     //event bubble up- update the required fields to validate later
      //handleUpdatedProgramAreaList(updatedProgramAreaList);    //event bubble up - Updated program area list
      createSaveRequestObject(FOI_COMPONENT_CONSTANTS.PROGRAM_AREA_LIST, updatedProgramAreaList);
    }

    const handleSubjectCodeChange = (e) => {
      setSelectedSubjectCode(e.target.value);
      handleInternalConsultationValues(e.target.checked, FOI_COMPONENT_CONSTANTS.SUBJECT_CODE)
      createSaveRequestObject(FOI_COMPONENT_CONSTANTS.SUBJECT_CODE, e.target.value);
    }
    
    const handleInternalConsultDueDateChange = (event) => {
      setDueDate(event.target.value);
      //event bubble up- update the required fields to validate later
      handleInternalConsultationValues(event.target.value, FOI_COMPONENT_CONSTANTS.TO_DATE);
      createSaveRequestObject(FOI_COMPONENT_CONSTANTS.TO_DATE, event.target.value);
  };

    useEffect(() => {
    
          setSelectedMinistries();
          
    
        }, [programAreaList, masterProgramAreaList]);
        
    const setSelectedMinistries = () => {
      //if updated program area list not exists then, update the master list with selected ministries
      if (Object.entries(programAreaList).length === 0) {
        const selectedMinistries = !!requestDetails.selectedMinistries? requestDetails.selectedMinistries
          : "";
        if (selectedMinistries !== "" && Object.entries(masterProgramAreaList).length !== 0) {
          const selectedList = selectedMinistries.map(
            (element) => element.code
          );
          masterProgramAreaList = masterProgramAreaList?.map((programArea) => {
            programArea.isChecked = !!selectedList.find(
              (selectedMinistry) => selectedMinistry === programArea.bcgovcode
            );
            return programArea;
          });
        } else {
          //if it is add request then keep all check boxes unchecked
          masterProgramAreaList = masterProgramAreaList?.map((programArea) => {
            programArea.isChecked = false;
            return programArea;
          });
        }
      }
      //if updated program area list exists then use that list instead of master data
      else {
        masterProgramAreaList = programAreaList;
      }
      setLocalProgramAreaList(masterProgramAreaList);
  }
        
    const statusesToNotAppearIn = [
      StateEnum.unopened.name.toLowerCase(),
      StateEnum.intakeinprogress.name.toLowerCase(),
      StateEnum.redirect.name.toLowerCase(),
    ];

    if (!requestState || !!statusesToNotAppearIn.find(status => status === requestState.toLowerCase())) {
      return null;
    }

    console.log("localProgramAreaList:", localProgramAreaList);

    return (
      <div className='request-accordian' >
      <Accordion defaultExpanded={true}>
      <AccordionSummary className={classes.accordionSummary} expandIcon={<ExpandMoreIcon />} id="internalConsultation-header">
      <Typography className={classes.heading}>INTERNAL CONSULTATION</Typography>
      </AccordionSummary>
      <AccordionDetails>    
        <div className="row foi-details-row foi-request-description-row switch-text-row">
            <div className="col-lg-10 foi-details-col d-flex align-items-center">
                <h5 className="foi-internal-consultation-step1-text-h5">Do you require to create an internal consultation for this request?</h5>
            <div className="col-lg-3 foi-details-col foi-request-dates">    
                <CustomSwitch
                  checked={isChecked}
                  onChange={(e) => setIsChecked(e.target.checked)}
                />
            </div>
            </div>
          </div>
          {isChecked &&(
        <div className="">
        { (Object.entries(localProgramAreaList).length !== 0  
        /* && (!requestDetails.currentState   || statesBeforeOpen.includes(requestDetails.currentState?.toLowerCase()) )*/
          ) &&
        <MultiMinistrySelector masterProgramAreaList={localProgramAreaList} handleUpdatedMasterProgramAreaList={handleUpdatedMasterProgramAreaList} disableInput={disableInput} />
        }                                                        

        <div className="row foi-details-row foi-request-description-row">
            <div className="col-lg-6 foi-details-col">
                <h5 className="foi-date-range-h5">Select Request Subject Code (if required)</h5>
            </div>
            <div className="col-lg-6 foi-details-col">
                <h5 className="foi-date-range-h5">Select Consult Due Date</h5>
            </div>
                                                                                
        </div>
        <div className="row foi-details-row foi-request-description-row">
          <div className="col-lg-6 foi-details-col">
                <TextField
                        id="internalConsultSubjectCode"
                        label="Subject Code*"
                        inputProps={{ "aria-labelledby": "subjectCode-label"}}
                        InputLabelProps={{ shrink: true, className: "internal-consultation-subject-code-label"}}
                        select
                        value={selectedSubjectCode}
                        onChange={handleSubjectCodeChange}
                        input={<Input />}
                        variant="outlined"
                        fullWidth
                        //disabled={"disableInput"}
                    >
                    {"Subject Code"}
                  </TextField> 
           </div>
           <div className="col-lg-6 foi-details-col foi-request-dates">
              <TextField  
                  id="internalConsultDueDate"              
                  label="Select Due Date*"
                  type="date"
                  value={dueDate}
                  className={classes.textField}
                  onChange={handleInternalConsultDueDateChange}
                  InputLabelProps={{
                  shrink: true,
                  className: "internal-consultation-due-date-label"
                  }} 
                  InputProps={{inputProps: { max: formatDate(new Date())} }}   
                  variant="outlined"
                  fullWidth
                  //disabled={disableInput}
              />  
            </div>    
        </div>
      </div>  
      )}  
        </AccordionDetails>
    </Accordion>
  </div>
    );
  }
);

export default InternalConsultation;