import React, { useEffect } from 'react';
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import './statedropdown.scss';
import { StateList } from '../../../constants/FOI/statusEnum';
import { isMinistryCoordinator } from '../../../helper/FOI/helper';
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';
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
        console.log(ministrycode.code)
        console.log(MINISTRYGROUPS[ministrycode.code])
        console.log(isMinistryCoordinator(userDetail,MINISTRYGROUPS[ministrycode.code]))
        _isMinistryCoordinator = isMinistryCoordinator(userDetail,MINISTRYGROUPS[ministrycode.code])
    }
        
    const [status, setStatus] = React.useState(requestState ? requestState : "Unopened");
    useEffect (() => {
        setStatus(requestState ? requestState : "Unopened");
    },[requestState])
    
    const handleChange = (event) => {
        setStatus(event.target.value);
        handleStateChange(event.target.value); 
    };

    const getStatusList = (_status) => {        
        let  _state =  requestState ? requestState : requestStatus.toLowerCase().includes("days")? "Open": requestStatus;              
        switch(_state.toLowerCase()) {
            case FOI_COMPONENT_CONSTANTS.UNOPENED.toLowerCase(): 
                return StateList.unopened;
            case FOI_COMPONENT_CONSTANTS.INTAKEINPROGRESS.toLowerCase():
                return StateList.intakeinprogress;
            case FOI_COMPONENT_CONSTANTS.OPEN.toLowerCase():
                return StateList.open;
            case FOI_COMPONENT_CONSTANTS.CLOSED.toLowerCase():
                return StateList.closed; 
            case FOI_COMPONENT_CONSTANTS.REDIRECT.toLowerCase():
                return StateList.redirect; 
            case FOI_COMPONENT_CONSTANTS.CallFORRECORDS.toLowerCase():
                return StateList.callforrecords; 
            case FOI_COMPONENT_CONSTANTS.REVIEW.toLowerCase():
                return StateList.review;
            case FOI_COMPONENT_CONSTANTS.CONSULT.toLowerCase():
                return StateList.consult;
            case FOI_COMPONENT_CONSTANTS.SIGNOFF.toLowerCase():
                return StateList.signoff;                                        
            default:
                return [];
        }
    }
    
    console.log(`_isMinistryCoordinator ${_isMinistryCoordinator}`);
    const statusList = getStatusList(status);    
    const menuItems = statusList.length > 0 && statusList.map((item) => {
        return (        
        <MenuItem disabled={(_isMinistryCoordinator && (item.status.toLowerCase().includes("open") || item.status.toLowerCase().includes("closed") ||  item.status.toLowerCase().includes("fee assessed") ||  item.status.toLowerCase().includes("review"))) || item.status.toLowerCase().includes("unopened")} className="foi-state-menuitem" key={item.status} value={item.status} >
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