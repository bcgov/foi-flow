import React, { useEffect, useState  } from "react";
import Accordion from '@material-ui/core/Accordion';
// import ExtensionDetailsBox from "./ExtensionDetailsBox"
import { StateEnum } from "../../../../constants/FOI/statusEnum";
import { AccordionDetails, AccordionSummary, TextField, Input, Typography } from "@material-ui/core";
import { makeStyles } from '@material-ui/styles';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import InputAdornment from "@material-ui/core/InputAdornment";
import MenuItem from '@material-ui/core/MenuItem';
// import MultiMinistrySelector from '../../customComponents/MultiMinistrySelector';
import { MinistriesList } from "../../customComponents";
import CustomSwitch from "./CustomSwitch";
import './InternalConsultation.scss';
import { useSelector } from "react-redux";
import FOI_COMPONENT_CONSTANTS from '../../../../constants/FOI/foiComponentConstants';
import {isValidMinistryCode, countOfMinistrySelected} from '../utils';
import { formatDate } from "../../../../helper/FOI/helper";
import clsx from "clsx";
import SvgIcon from "./SvgIcon";
import InternalConsultConfirmationModal from "./InternalConsultConfirmationModal";
import { ConsultTransactionResponse } from "./types";

const useStyles = makeStyles((_theme) => ({
  headingError: {
    color: "#ff0000"
  },
  headingNormal: {
    color: "#000000"
  },
  btndisabled: {
    color: "#808080"
  },
  btnenabled: {
    border: "none",
    backgroundColor: "#38598A",
    color: "#FFFFFF",
  },
  heading: {
    color: '#FFF',
    fontSize: '16px',
    fontWeight: 'bold'
  },
  accordionSummary: {
    flexDirection: 'row-reverse'
  },
  showDueDateFieldValidation: {
    color: "#CE3E39",
    fontStyle: 'italic'
  },
  hideDueDateFieldValidation: {
    visibility: 'hidden'
  },
  showDueDateIcon: {
    position: 'absolute',
    right: 40,
    transform: 'translateY(-1%)',
    color: '#CE3E39',
    pointerEvents: 'none',
  },
  hideDueDateIcon: {
    visibility: 'hidden'
  }
}));

  
const InternalConsultation = ({
    requestId,
    ministryId,
    programAreaList,
    requestDetails,
    requestConsults,
    requestState,
    disableInput,
    setUnSavedRequest,
  }:any) => {
    const classes = useStyles();
    const MinistriesListTyped = MinistriesList as React.FC<any>;
    let foiConsultTransactionData = useSelector((state: any) => state.foiRequests.foiRequestConsults);
    const [consultData, setConsultData] = useState<ConsultTransactionResponse[]>(foiConsultTransactionData);
    const [isChecked, setIsChecked] = React.useState(false);
    const [validation, setValidation] = React.useState({});
    var masterProgramAreaList = useSelector((state: any) => state.foiRequests.foiProgramAreaList);
    const [localProgramAreaList, setLocalProgramAreaList] = React.useState([])
    const [dueDate, setDueDate] = React.useState(!!requestDetails.toDate ? formatDate(new Date(requestDetails.toDate)): "");
    const [dueDateError, setDueDateError] = React.useState("");
    const subjectCodeList = useSelector((state: any) => state.foiRequests.foiSubjectCodeList);
    const [isMinistryValid, setIsMinistryValid] = React.useState(false);
    const [isDueDateValid, setIsDueDateValid] = React.useState(false);
    const [saveModal, setSaveModal] = useState({
      show: false,
      title: "",
      description: "",
      descriptionDetail: "",
      message: "",
      confirmButtonTitle: ""
    });

    const getSubjectCode = () => {
      if (requestConsults?.subjectCode)
        return requestConsults.subjectCode;
      return "Select Subject Code (if required)"
    }

    const [selectedSubjectCode, setSelectedSubjectCode] = React.useState(getSubjectCode());

    useEffect(() => {
      setSelectedSubjectCode(getSubjectCode())  
      if(Object.entries(requestDetails).length !== 0){
        setSelectedConsultMinistries();
      }
    },[requestDetails])

    useEffect(() => {
      setConsultData(foiConsultTransactionData);
    }, [foiConsultTransactionData]);


    const subjectCodes = subjectCodeList.map((item:any) => {
      return ( <MenuItem key={item.name} value={item.name} disabled={item.name.toLowerCase().includes("select")}>{item.name}</MenuItem> )
    });

    const handleUpdatedMasterProgramAreaList = (updatedProgramAreaList:any) => {
      //validate the program area list
      const isMinistrySelected = updatedProgramAreaList.some((programArea:any) => programArea.isChecked);
      setIsMinistryValid(isMinistrySelected);
      setUnSavedRequest(true);
      
      // handleInternalConsultationValues(countOfMinistrySelected(updatedProgramAreaList) === 1 && updatedProgramAreaList.some((programArea:any) =>
      //   (programArea.isChecked && isValidMinistryCode(programArea.bcgovcode, masterProgramAreaList))), 
      //   FOI_COMPONENT_CONSTANTS.IS_PROGRAM_AREA_SELECTED);     //event bubble up- update the required fields to validate later
      //handleUpdatedProgramAreaList(updatedProgramAreaList);    //event bubble up - Updated program area list
      //createSaveRequestObject(FOI_COMPONENT_CONSTANTS.PROGRAM_AREA_LIST, updatedProgramAreaList);
    }

    const handleSubjectCodeChange = (e:any) => {
      setSelectedSubjectCode(e.target.value);
      setUnSavedRequest(true);
      //handleInternalConsultationValues(e.target.checked, FOI_COMPONENT_CONSTANTS.SUBJECT_CODE)
      //createSaveRequestObject(FOI_COMPONENT_CONSTANTS.SUBJECT_CODE, e.target.value);
    }
    
    const handleInternalConsultDueDateChange = (event:any) => {
      const newDueDate = event.target.value;
      setDueDate(newDueDate);

      // Validate the due date
      const isValid = newDueDate && new Date(newDueDate) >= new Date(requestDetails.receivedDate);
      setIsDueDateValid(isValid);
      setUnSavedRequest(true);
      //event bubble up- update the required fields to validate later
      //handleInternalConsultationValues(event.target.value, FOI_COMPONENT_CONSTANTS.TO_DATE);
      // createSaveRequestObject(FOI_COMPONENT_CONSTANTS.TO_DATE, event.target.value);
  };

    useEffect(() => {
    
          setSelectedConsultMinistries();
          
    
        }, [programAreaList, masterProgramAreaList]);
        
    const setSelectedConsultMinistries = () => {
      //if updated program area list not exists then, update the master list with selected ministries
      if (Object.entries(programAreaList).length === 0) {
        const selectedMinistries = !!requestConsults?.selectedMinistries? requestConsults.selectedMinistries : "";
        if (selectedMinistries !== "" && Object.entries(masterProgramAreaList).length !== 0) {
          const selectedList = selectedMinistries.map((element:any) => element.code);
          
          masterProgramAreaList = masterProgramAreaList?.map((programArea:any) => {
            programArea.isChecked = !!selectedList.find(
              (selectedMinistry:any) => selectedMinistry === programArea.bcgovcode
            );
            return programArea;
          });
         
        } else {
          //if it is add request then keep all check boxes unchecked
          masterProgramAreaList = masterProgramAreaList?.map((programArea:any) => {
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

    const validateInternalConsultation = () => {
      const isMinistrySelected = localProgramAreaList.some((programArea:any) => programArea.isChecked);
      const isDueDateValid = dueDate && new Date(dueDate) >= new Date(requestDetails.receivedDate);
    
      return isMinistrySelected && isDueDateValid;
    };
        
    const statusesToNotAppearIn = [
      StateEnum.unopened.name.toLowerCase(),
      StateEnum.intakeinprogress.name.toLowerCase(),
      StateEnum.redirect.name.toLowerCase(),
    ];

    if (!requestState || !!statusesToNotAppearIn.find(status => status === requestState.toLowerCase())) {
      return null;
    }

    const handleInternalConsultSaveRequest = () => {
      if (validateInternalConsultation()) {
        const selectedMinistries = localProgramAreaList.filter((programArea:any) => programArea.isChecked); 
        const finalSubjectCode = selectedSubjectCode.toLowerCase().includes("select") ? null : selectedSubjectCode;
        setUnSavedRequest(true);
        setSaveModal((prev: any) => ({
          ...prev,
          show: true,
          title: "Internal Consultation",
          description: "Are you sure you want to add an internal consultation for this request?",
          descriptionDetail: "Please confirm your recipients selection to create your internal consultation.",
          message: "",
          confirmButtonTitle: "Create new consultation",
          confirmationData: {
            selectedMinistries,
            subjectCode: finalSubjectCode,
            dueDate: dueDate,
          },
        }));
      }
    };

    const saveData = () => {
      // actually save the data
      setSaveModal((prev) => ({ ...prev, show: false }));
    };

    return (
      <div className='request-accordian internal-consultation-div'>
      <Accordion defaultExpanded={true}>
      <AccordionSummary className={classes.accordionSummary} expandIcon={<ExpandMoreIcon />} id="internalConsultation-header">
      <Typography className={classes.heading}>INTERNAL CONSULTATION</Typography>
      </AccordionSummary>
      <AccordionDetails>    
        {consultData && consultData.length > 0 ? (
        <div className="row foi-details-row foi-request-description-row consult-tracking-row">
          <span className="consult-tracking-details col-6 text-left">
            <h4 className="consult-tracking-title">Consultation Tracking:</h4>
            </span>
          {consultData.map(item => (
            <div key={item.id} className="col-lg-10 text-left d-flex align-items-center consult-row-600">
              <div className="consult-tracking-details consult-tracking-left col-6 text-left">
                <span className="program-area-name">{item.programAreaName}</span>
                <div className="arrow-flex-fill">
                  <svg xmlns="http://www.w3.org/2000/svg" className="program-arrow" width="" height="13" viewBox="0 0 281 13" fill="none">
                    <path d="M280.5 6.68457L270.5 0.911067V12.4581L280.5 6.68457ZM0.5 7.68457H271.5V5.68457H0.5V7.68457Z" fill="#9F9D9C"/>
                  </svg>
                </div>
                </div>
                 <span className="consult-tracking-details col-6 text-right">
                  <strong>{item.requestStatusName}</strong>
                </span>
            </div>
          ))}
        </div>
        ) : (
        <>
        <div className="row foi-details-row foi-request-description-row switch-text-row">
            <div className="col-lg-10 foi-details-col d-flex align-items-center">
                <h5 className="foi-internal-consultation-step1-text-h5">Do you require to create an internal consultation for this request?</h5>
            <div className="col-lg-3 foi-details-col foi-request-dates">    
                <CustomSwitch
                  checked={isChecked}
                  onChange={(e:any) => setIsChecked(e.target.checked)}
                />
            </div>
            </div>
          </div>
          {isChecked &&(
        <div className="intel-consultation-ministries-list">
        { (Object.entries(localProgramAreaList).length !== 0  
        /* && (!requestDetails.currentState   || statesBeforeOpen.includes(requestDetails.currentState?.toLowerCase()) )*/
          ) &&
        <MinistriesListTyped masterProgramAreaList={localProgramAreaList as any} handleUpdatedMasterProgramAreaList={handleUpdatedMasterProgramAreaList} disableInput={false} isMultiSelectMode={true} showOnlySelected={false} isInternalConsultValidationError={!isMinistryValid}/>
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
                        label="Subject Code"
                        inputProps={{ "aria-labelledby": "subjectCode-label"}}
                        InputLabelProps={{ shrink: true, className: "internal-consultation-subject-code-label"}}
                        select
                        value={selectedSubjectCode}
                        onChange={handleSubjectCodeChange}
                        //input={<Input />}
                        variant="outlined"
                        fullWidth
                        //disabled={"disableInput"}
                    >
                    {subjectCodes}
                  </TextField> 
           </div>
           <div className="col-lg-6 foi-details-col foi-request-dates">
              <TextField  
                  id="internalConsultDueDate"              
                  label="Select Due Date*"
                  type="date"
                  value={dueDate}
                  //className={classes.textField}
                  onChange={handleInternalConsultDueDateChange}
                  InputLabelProps={{
                  shrink: true,
                  className: "internal-consultation-due-date-label"
                  }} 
                  InputProps={{
                    endAdornment: (
                    <InputAdornment position="start">
                      <SvgIcon
                        className={clsx({
                          [classes.showDueDateIcon]: !isDueDateValid,
                          [classes.hideDueDateIcon]: isDueDateValid,
                        })}
                        paths={[
                          {
                            d: "M18.335 15.5312C18.835 16.4062 18.21 17.5 17.1787 17.5H3.83499C2.80374 17.5 2.17874 16.4062 2.64749 15.5312L9.33499 4.15625C9.61624 3.71875 10.0537 3.5 10.5225 3.5C10.96 3.5 11.3975 3.71875 11.6787 4.15625L18.335 15.5312ZM4.14749 16H16.8663L10.4912 5.15625L4.14749 16ZM10.5225 13.0625C11.0537 13.0625 11.4912 13.5 11.4912 14.0312C11.4912 14.5625 11.0537 15 10.5225 15C9.95998 15 9.52249 14.5625 9.52249 14.0312C9.52249 13.5 9.95998 13.0625 10.5225 13.0625ZM9.77249 8.25C9.77249 7.84375 10.085 7.5 10.5225 7.5C10.9287 7.5 11.2725 7.84375 11.2725 8.25V11.25C11.2725 11.6875 10.9287 12 10.5225 12C10.085 12 9.77249 11.6875 9.77249 11.25V8.25Z",
                            fill: "#CE3E39",
                          },
                        ]}
                      />
                    </InputAdornment>
                  ),inputProps: { min: formatDate(new Date(requestDetails.receivedDate)) } }}   
                  variant="outlined"
                  fullWidth
                  //disabled={disableInput}
              />  
              <h5
                  className={clsx({
                    [classes.showDueDateFieldValidation]: !isDueDateValid,
                    [classes.hideDueDateFieldValidation]: isDueDateValid,
                  })}
               >This field is required</h5>
            </div>  
            <div className="col-lg-7 foi-details-col foi-request-dates">
              <button
                          type="button"
                          className={clsx("btn", "btn-bottom", "consult-save-button", {
                            [classes.btndisabled]: (!isMinistryValid || !isDueDateValid),
                            [classes.btnenabled]: (isMinistryValid && isDueDateValid),
                          })}
                          disabled={!isMinistryValid || !isDueDateValid }
                          onClick={handleInternalConsultSaveRequest}
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" width="21" height="20" viewBox="0 0 21 20" fill="none">
                      <path d="M16.625 7.27734L9.1875 14.7148C9.07812 14.8516 8.91406 14.9062 8.75 14.9062C8.55859 14.9062 8.39453 14.8516 8.28516 14.7148L4.34766 10.7773C4.07422 10.5312 4.07422 10.1211 4.34766 9.875C4.59375 9.60156 5.00391 9.60156 5.25 9.875L8.75 13.3477L15.7227 6.375C15.9688 6.10156 16.3789 6.10156 16.625 6.375C16.8984 6.62109 16.8984 7.03125 16.625 7.27734Z" fill="white"/>
                      </svg> Save Consultation
                </button>
                {saveModal.show && (
                <InternalConsultConfirmationModal
                  requestId={requestId}
                  ministryId={ministryId}
                  modal={saveModal}
                  confirm={() => saveData()}
                  setModal={setSaveModal}
                  masterProgramAreaList={localProgramAreaList}
                  handleUpdatedMasterProgramAreaList={handleUpdatedMasterProgramAreaList}
                  requestDetails={requestDetails}
                  requestConsults={requestConsults}
                  setUnSavedRequest={setUnSavedRequest}
                />
                )}
              </div>  
        </div>
      </div>  
      )}  
      </>
      )}
        </AccordionDetails>
    </Accordion>
  </div>
    );
  };

export default InternalConsultation;