import React, { useEffect } from 'react';
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import './statedropdown.scss';
import { StateList, StateEnum } from '../../../constants/FOI/statusEnum';
import { isMinistryCoordinator } from '../../../helper/FOI/helper';
import MINISTRYGROUPS from '../../../constants/FOI/foiministrygroupConstants';
import { useParams } from 'react-router-dom';
import { useSelector } from "react-redux";

export default function StateDropDown({requestStatus, handleStateChange,requestDetail}) {

    const {requestState} = useParams();

    let userDetail = useSelector(state=> state.user.userDetail);
   
    let _isMinistryCoordinator =''

    if(requestDetail.selectedMinistries!=undefined && userDetail!=undefined)
    {
        var ministrycode = requestDetail.selectedMinistries[0]
        _isMinistryCoordinator = isMinistryCoordinator(userDetail,MINISTRYGROUPS[ministrycode.code])
    }
        
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
        switch(_state.toLowerCase()) {
            case StateEnum.unopened.name.toLowerCase(): 
                return StateList.unopened;
            case StateEnum.intakeinprogress.name.toLowerCase():
                return StateList.intakeinprogress;
            case StateEnum.open.name.toLowerCase():
                return StateList.open;
            case StateEnum.closed.name.toLowerCase():
                return StateList.closed; 
            case StateEnum.redirect.name.toLowerCase():
                return StateList.redirect; 
            case StateEnum.callforrecords.name.toLowerCase():
                return StateList.callforrecords; 
            case StateEnum.review.name.toLowerCase():
                return StateList.review;
            case StateEnum.consult.name.toLowerCase():
                return StateList.consult;
            case StateEnum.signoff.name.toLowerCase():
                return StateList.signoff;
            case StateEnum.feeassessed.name.toLowerCase():
                return StateList.feeassessed;                                        
            default:
                return [];
        }
    }
    
    const statusList = getStatusList(status);    
    const menuItems = statusList.length > 0 && statusList.map((item) => {
        return (        
        <MenuItem disabled={(_isMinistryCoordinator && (item.status.toLowerCase().includes(StateEnum.open.name.toLowerCase()) || item.status.toLowerCase().includes(StateEnum.closed.name.toLowerCase()) ||  item.status.toLowerCase().includes(StateEnum.feeassessed.name.toLowerCase()) ||  item.status.toLowerCase().includes(StateEnum.review.name.toLowerCase()))) || item.status.toLowerCase().includes(StateEnum.unopened.name.toLowerCase())} className="foi-state-menuitem" key={item.status} value={item.status} >
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