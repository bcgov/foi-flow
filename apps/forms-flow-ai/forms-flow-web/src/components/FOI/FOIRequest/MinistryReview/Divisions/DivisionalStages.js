import React, { useEffect, useState } from 'react';
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import './divisionstages.scss';
import { useDispatch, useSelector } from "react-redux";

const DivisionalStages = React.memo(({divisionalstages,existingDivStages,popselecteddivstages}) => {
    var stageCounter = []
    if(existingDivStages.length === 0 || existingDivStages == undefined)
    {
        stageCounter.push({id:0,divisionid:-1,name:"",stage:"",stagename:""})
    }
    else{
       
        stageCounter=existingDivStages
    }
    
    const [minDivStages, setMinDivStages] = React.useState(stageCounter);
    

    const handleDivisionChange = (e,id)=> {                
        let arr = minDivStages;        
        //const divisionnotexists = arr.filter(st=>st.divisionid === e.target.value).length === 0;
        const idexists = arr.filter(st=>st.id === id).length > 0;
        if(idexists)
        {           
            arr.filter(item=>item.id === id).forEach(item=> {item.divisionid = e.target.value;item.name = e.target.name})            
            setMinDivStages([...arr])
            appendstageIterator([...arr])            
        }
        else{
            console.log("No Id found - handleDivisionChange ")
        }        
    }
    const handleDivisionStageChange = (e,id)=> {          
        let arr = minDivStages;       
        const exists = arr.filter(st=>st.id === id).length > 0
        if(exists)
        {
            arr.filter(st=>st.id === id).forEach(item=>{item.stage = e.target.value;item.stagename=e.target.name})
            
        }
        else{
            console.log("No Id found - handleDivisionStageChange ")
        }
        setMinDivStages([...arr])                            
    }
   
    popselecteddivstages(minDivStages)

    const deleteMinistryDivision = (id)=>{
       
        let existing = stageIterator;
        let updatedIterator = existing.filter(i=>i.id !== id);
        
        setMinDivStages([...updatedIterator])
        appendstageIterator([...updatedIterator])
               
    }
      
    const [stageIterator, appendstageIterator] = React.useState(stageCounter);
        
    const addDivisionalStage = () => {

        let existing = stageIterator;
        var val = stageIterator.length > 0 ?  stageIterator[stageIterator.length - 1].id + 1 :0
        if (divisionList.length >= stageIterator.length) {           
            existing.push({id:val,divisionid:-1,name:"",stage:"",stagename:""})
            setMinDivStages([...existing]) 
            appendstageIterator([...existing])
        }        
    }


    const divisionList = divisionalstages.divisions
    const divisionItems = divisionList !=undefined && divisionList.length > 0 && divisionList.map((item) => {

        let _mindivtem = minDivStages.filter(d=>d.divisionid === item.divisionid)               
        return (
            <MenuItem disabled={_mindivtem.length > 0 } className="foi-division-menuitem" key={item.divisionid} name= {item.name} value={item.divisionid} >
                <span className={`foi-menuitem-span ${item.name.toLowerCase().replace(/\s/g, '')}`} ></span>
                {item.name}
            </MenuItem>
        )
    });

    const divisionstageList = divisionalstages.stages
    const divisionstageItems = divisionstageList!=undefined && divisionstageList.length > 0 && divisionstageList.map((item) => {

        return (
            <MenuItem className="foi-divisionstage-menuitem" key={item.stageid} value={item.stageid} name= {item.name}  >
                <span className={`foi-menuitem-span ${item.name.toLowerCase().replace(/\s/g, '')}`} ></span>
                {item.name}
            </MenuItem>
        )
    });

    var divisionalStagesRow = (row) => {

        let _id = row.id
       
        return (
            <div className="row foi-details-row" id={`foi-division-row${_id}`}>
                <div className="col-lg-5 foi-details-col">
                    <TextField
                        id="foi-division-dropdown"_id
                        className="foi-division-dropdown"
                        InputLabelProps={{ shrink: true, }}
                        select
                        input={<Input />}
                        variant="outlined"
                        onChange={e => handleDivisionChange(e,_id)}
                        fullWidth                        
                        label="Select Divison"
                        value={row.divisionid}                        
                    >
                        {[...divisionItems]}
                    </TextField>

                </div>
                <div className="col-lg-5 foi-details-col">
                    <TextField
                        id="foi-divisionstage-dropdown"_id
                        className="foi-divisionstage-dropdown"
                        InputLabelProps={{ shrink: true, }}
                        select
                        input={<Input />}
                        variant="outlined"
                        fullWidth                        
                        label="Select Divison Stage"
                        onChange={e => handleDivisionStageChange(e,_id)} 
                        value={row.stage}                      
                    >
                        {divisionstageItems}
                    </TextField>
                </div>
                <div className="col-lg-2 foi-details-col">
                    <i class="fa fa-trash fa-3 foi-bin" aria-hidden="true" onClick={e=>deleteMinistryDivision(_id)}></i>
                </div>
            </div>
        )

    }

    return (
        <>
            <div id="divstages" >

                {
                   divisionstageList!=undefined && divisionstageList!=undefined && stageIterator.map((item) =>

                        divisionalStagesRow(item)
                    )
                }

            </div>
            <div className="row foi-details-row">
                <div className="col-lg-7 foi-details-col">
                    <i class="fa fa-plus-circle fa-3 foi-add" aria-hidden="true"></i>  <a href="#" onClick={addDivisionalStage}>Add division to track</a>
                </div>

            </div>
        </>
    )
})

export default DivisionalStages