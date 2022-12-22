import React, { useEffect, useState }  from 'react';
import { useParams } from 'react-router-dom';
import { useSelector, useDispatch } from "react-redux";
import OutlinedInput from '@material-ui/core/OutlinedInput';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import Select from '@material-ui/core/Select';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFlag } from '@fortawesome/free-regular-svg-icons'; 
import { faFlag  as faSolidFlag} from '@fortawesome/free-solid-svg-icons'; 
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import CloseIcon from '@material-ui/icons/Close';
import IconButton from '@material-ui/core/IconButton';
import TextField from '@mui/material/TextField';
import './requestrestriction.scss';
import {restrictRequest, fetchFOIRequestDetailsWrapper} from '../../../apiManager/services/FOI/foiRequestServices';


const RequestRestriction= ({isiaorestricted, userDetail, requestDetails}) =>{ 

    const [restrictionType, setRestrictionType] = useState("unrestricted");
    const [isRestricted, setIsRestricted] = useState(isiaorestricted);
    const [modalOpen, setModalOpen] = useState(false);
    const [modalMessage, setModalMessage] = useState(<></>);    
    const [modalDescription, setModalDescription] = useState(<></>);
    const { requestId, ministryId } = useParams();
    const dispatch = useDispatch();


    useEffect(() => {
        setIsRestricted(isiaorestricted);
        if(isiaorestricted){
            setRestrictionType("restricted");
        }else{
            setRestrictionType("unrestricted");
        }
    }, []);

    const isIAORestrictedFileManager = () => {
        return userDetail?.role?.includes("IAORestrictedFilesManager");
    }

    const isRequestAssignedToTeam = () => {
        return (!requestDetails?.assignedTo && requestDetails?.assignedGroup);
    }

    const restriction = [
        {
          value: 'unrestricted',
          label: 'Unrestricted',
          disabled: false // To Do : Add condition
        },
        {
          value: 'restricted',
          label: 'Restricted',
          disabled: false,
        }
    ];

    const handleValueChange = (e) => {
        setModalOpen(true);
        if(e.target.value?.toLowerCase() == 'restricted'){
            if(isIAORestrictedFileManager()){
                if(!isRequestAssignedToTeam()){
                    setIsRestricted('True');
                    setModalMessage("Are you sure you want to flag this as a restricted file ?");
                    setModalDescription("If you change this to be a restrcited file only the Intake Manager and any user assigned or selected as watchers will be able to view this request content.");
                }
                else{
                    setModalMessage("A request can only be restricted when it is assigned to one team member, not a team queue.");
                }
            }
            else{
                setModalMessage("Only the Intake Manager can restrict a request.");
            }
        }
        else {
            if(isIAORestrictedFileManager()){
                setIsRestricted('False');
                setModalMessage("Are you sure you want to remove the restricted file flag on this request ?");
                setModalDescription("If you restrcit this file only all IAO users will be able to search and find the request, and all users "+
                "on the respective Ministry will be able to see this request.");
            }
            else{
                setModalMessage("Only the Intake Manager can remove the restricted flag on a request");
                setModalDescription("If you would like to have this request unrestricted please contact the Intake Manager as they are the original user"+
                " who flagged this as a restricted request.");
            }
        }
       
    }

    const handleSave = () => {
        setModalOpen(false);
        save();
    };

    const handleClose = () => {
        setModalOpen(false);
    };

    const save = () => {
        let type = "iao";
        let data = {
            "isrestricted": isRestricted
        }
        dispatch(restrictRequest(data, requestId, ministryId, type,(err, data) => {
            if(!err){
                fetchFOIRequestDetailsWrapper(requestId, ministryId);
                if(isRestricted == 'True')
                    setRestrictionType("restricted");
                else
                    setRestrictionType("unrestricted");
            }
        }))
      };


    return (  
        <>
        <div className="requestRestriction">
            <div className="restrict-dropdown-all">
                <div className="restrict-select" style={{background: restrictionType == 'restricted'? 'linear-gradient(to right, rgba(160,25,47,0.32) 80%, #a0192f 0%)' : 'linear-gradient(to right, #fff 80%, #a0192f 0%)'}}>
                    { restrictionType?.toLowerCase() == 'restricted'?
                        <FontAwesomeIcon icon={faSolidFlag} size='2x' className='restrict-icon' />:
                        <FontAwesomeIcon icon={faFlag} size='2x' className='restrict-icon' />      
                    }       
                    {/* <InputLabel id="restrict-dropdown-label">
                    Unrestricted
                    </InputLabel> */}
                    <TextField
                    id="restrict-dropdown"
                    className="restrict-dropdown"
                    select
                    value={restrictionType}
                    onChange={handleValueChange}
                    inputProps={{'aria-labelledby': 'restrict-dropdown-label'}}
                    input={<OutlinedInput label="Tag" />}
                    disabled = {false}
                    >
                    {restriction.map((option) => (
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
            </div>
        </div> 
        <div className="state-change-dialog">
            <Dialog
            open={modalOpen}
            onClose={handleClose}
            aria-labelledby="state-change-dialog-title"
            aria-describedby="restricted-modal-text"
            maxWidth={'md'}
            fullWidth={true}
            // id="state-change-dialog"
            >
            <DialogTitle disableTypography id="state-change-dialog-title">
                <h2 className="state-change-header">Restricted File</h2>
                <IconButton className="title-col3" onClick={handleClose}>
                    <i className="dialog-close-button">Close</i>
                    <CloseIcon />
                </IconButton>
                </DialogTitle>
            <DialogContent>
                <DialogContentText id="restricted-modal-text" component={'span'}>
                <div className="modal-msg">
                    <div className="confirmation-message">
                        {modalMessage}
                    </div>
                    <div className='modal-msg-description'>
                        <i>{modalDescription}</i>
                    </div>
                </div>
            </DialogContentText>
            </DialogContent>
            <DialogActions>
                <button
                className={`btn-bottom btn-save btn`}
                onClick={handleSave}
                disabled={!isIAORestrictedFileManager()}
                >
                Save Change
                </button>
                <button className="btn-bottom btn-cancel" onClick={handleClose}>
                Cancel
                </button>
            </DialogActions>
            </Dialog>
        </div>
        </>
    );
};

export default RequestRestriction;