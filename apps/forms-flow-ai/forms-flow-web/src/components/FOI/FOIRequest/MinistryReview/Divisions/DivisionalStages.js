import React, { useEffect, useState } from 'react';
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import './divisionstages.scss';
import { useDispatch, useSelector } from "react-redux";
import {
    fetchFOIMinistryDivisionalStages
  } from "../../../../../apiManager/services/FOI/foiRequestServices";
const DivisionalStages = React.memo((props) => {
    const [minDivStages, setMinDivStages] = React.useState([]);
    

    const handleDivisionChange = (e,id)=> {

        console.log('handleDivisionChange')
        console.log(e)
        let arr = minDivStages;
        const exists = arr.filter(st=>st.name === e.target.value).length > 0
        if(!exists)
        {
            arr.push({divisionid:id,name:e.target.value,stage:""})            
            setMinDivStages([...arr])
            appendstageIterator([...arr])
        }
        
        console.log(minDivStages)
    }
    const handleDivisionStageChange = (e,divisionid)=> {

        let arr = minDivStages;
        const exists = arr.filter(st=>st.divisionid === divisionid).length > 0
        if(exists)
        {
            arr.filter(st=>st.divisionid === divisionid).forEach(item=>item.stage = e.target.value)

        }
        setMinDivStages([...arr])
        console.log('handleDivisionStageChange')    
        console.log(e)
        console.log(minDivStages)
    }

    console.log("Divstages")
    console.log(minDivStages)

    const deleteMinistryDivision = (divisionid)=>{

        let existing = stageIterator;
        let updatedIterator = existing.filter(i=>i.divisionid !== divisionid);
       
        appendstageIterator([...updatedIterator])
        setMinDivStages([...updatedIterator])
       

    }

  

    var stageCounter = []
    stageCounter.push({divisionid:0,name:"",stage:""})
    const [stageIterator, appendstageIterator] = React.useState(stageCounter);
    
    
    const addDivisionalStage = () => {

        let existing = stageIterator;
        var val = stageIterator[stageIterator.length - 1].id + 1
        if (divisionList.length >= val) {           
            existing.push({divisionid:val,name:"",stage:""})
            appendstageIterator([...existing])
        }
        console.log(stageIterator)
    }
const bcgovcode ="EDUC"
    const dispatch = useDispatch();
  useEffect(() => {
    if (bcgovcode) {
      dispatch(fetchFOIMinistryDivisionalStages("EDUC"));      
    }       
  },[dispatch]);

  let divisionalstages = useSelector(state=> state.foiRequests.foiMinistryDivisionalStages);
  console.log("Division stage Data")
  console.log(divisionalstages)

  const divisionList = divisionalstages.divisions
    const divisionItems = divisionList !=undefined && divisionList.length > 0 && divisionList.map((item) => {

        let _mindivtem = minDivStages.filter(d=>d.name.toLowerCase() === item.name.toLowerCase())               
        return (
            <MenuItem disabled={_mindivtem.length > 0 } className="foi-division-menuitem" key={item.divisionid} value={item.name} >
                <span className={`foi-menuitem-span ${item.name.toLowerCase().replace(/\s/g, '')}`} ></span>
                {item.name}
            </MenuItem>
        )
    });

    const divisionstageList = divisionalstages.stages
    const divisionstageItems = divisionstageList!=undefined && divisionstageList.length > 0 && divisionstageList.map((item) => {

        return (
            <MenuItem className="foi-divisionstage-menuitem" key={item.stageid} value={item.name} >
                <span className={`foi-menuitem-span ${item.name.toLowerCase().replace(/\s/g, '')}`} ></span>
                {item.name}
            </MenuItem>
        )
    });

    var divisionalStagesRow = (row) => {

        let _id = row.id
        return (
            <div className="row foi-details-row" id="foi-division-row"_id>
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
                        value={row.division}
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