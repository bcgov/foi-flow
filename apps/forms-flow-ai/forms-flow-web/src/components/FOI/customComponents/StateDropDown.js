import React, { useEffect } from 'react';
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import './statedropdown.scss';
import { StateList, MinistryStateList, StateEnum } from '../../../constants/FOI/statusEnum';
import { isMinistryCoordinator } from '../../../helper/FOI/helper';
import MINISTRYGROUPS from '../../../constants/FOI/foiministrygroupConstants';
import { useParams } from 'react-router-dom';
import { useSelector } from "react-redux";

export default function StateDropDown({requestStatus, handleStateChange, isMinistryCoordinator, isValidationError}) {

    const {requestState} = useParams();

    let userDetail = useSelector(state=> state.user.userDetail);
   
    const _isMinistryCoordinator = isMinistryCoordinator;

    const [status, setStatus] = React.useState(requestState ? requestState : StateEnum.unopened.name);
    useEffect (() => {
        setStatus(requestState ? requestState : StateEnum.unopened.name);
    },[requestState])
    
    const handleChange = (event) => {
        setStatus(event.target.value);
        handleStateChange(event.target.value); 
    };

    const getStatusList = (_status) => {        
        let  _state =  requestState ? requestState : requestStatus.toLowerCase().includes("days")? "Open": requestStatus;
        let _stateList = StateList;
        if(_isMinistryCoordinator) {
            _stateList = MinistryStateList;
        }
        switch(_state.toLowerCase()) {
            case StateEnum.unopened.name.toLowerCase(): 
                return _stateList.unopened;
            case StateEnum.intakeinprogress.name.toLowerCase():
                return _stateList.intakeinprogress;
            case StateEnum.open.name.toLowerCase():
                return _stateList.open;
            case StateEnum.closed.name.toLowerCase():
                return _stateList.closed; 
            case StateEnum.redirect.name.toLowerCase():
                return _stateList.redirect; 
            case StateEnum.callforrecords.name.toLowerCase():
                return _stateList.callforrecords; 
            case StateEnum.review.name.toLowerCase():
                return _stateList.review;
            case StateEnum.onhold.name.toLowerCase():
                return _stateList.onhold;
            case StateEnum.consult.name.toLowerCase():
                return _stateList.consult;
            case StateEnum.signoff.name.toLowerCase():
                return _stateList.signoff;
            case StateEnum.feeassessed.name.toLowerCase():
                return _stateList.feeassessed;                                        
            case StateEnum.onhold.name.toLowerCase():
                return _stateList.onhold;  
            case StateEnum.deduplication.name.toLowerCase():
                return _stateList.deduplication;  
            case StateEnum.harms.name.toLowerCase():
                return _stateList.harms;    
            case StateEnum.response.name.toLowerCase():
                return _stateList.response;  
            default:
                return [];
        }
    }
    
    const statusList = getStatusList(status);    
    const menuItems = statusList.length > 0 && statusList.map((item, index) => {

        return (        
        <MenuItem disabled={index>0 && isValidationError} className="foi-state-menuitem" key={item.status} value={item.status} >
            <span className={`foi-menuitem-span ${item.status.toLowerCase().replace(/\s/g, '')}`} ></span>
            {item.status}
        </MenuItem> 
        )
     });
    return (  
        
            <TextField
                id="foi-status-dropdown"
                className="foi-state-dropdown"
                InputLabelProps={{ shrink: false, }}          
                select
                value={status}
                onChange={handleChange}
                input={<Input />} 
                variant="outlined"
                fullWidth
                
            >                
            
                {menuItems}
            </TextField>  
           
    );
  }