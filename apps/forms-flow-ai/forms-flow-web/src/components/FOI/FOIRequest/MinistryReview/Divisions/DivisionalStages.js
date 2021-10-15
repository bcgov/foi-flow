import React, { useEffect, useState } from 'react';
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import './divisionstages.scss';
const DivisionalStages = React.memo((props) => {
    const [minDivStages, setMinDivStages] = React.useState([]);
    const divisionList = [{ id: "0", division: "Select Division to Send CFR" }, { id: "1", division: "Divison 1" }, { id: "2", division: "Divison 2" }]
    const divisionItems = divisionList.length > 0 && divisionList.map((item) => {

        let _mindivtem = minDivStages.filter(d=>d.division.toLowerCase() === item.division.toLowerCase())               
        return (
            <MenuItem disabled={_mindivtem.length > 0 } className="foi-division-menuitem" key={item.id} value={item.division} >
                <span className={`foi-menuitem-span ${item.division.toLowerCase().replace(/\s/g, '')}`} ></span>
                {item.division}
            </MenuItem>
        )
    });

    const divisionstageList = [{ id: "0", divisionstage: "Select Division Stage" }, { id: "1", divisionstage: "Clarification" }, { id: "2", divisionstage: "Assign to division" }]
    const divisionstageItems = divisionstageList.length > 0 && divisionstageList.map((item) => {

        return (
            <MenuItem className="foi-divisionstage-menuitem" key={item.id} value={item.divisionstage} >
                <span className={`foi-menuitem-span ${item.divisionstage.toLowerCase().replace(/\s/g, '')}`} ></span>
                {item.divisionstage}
            </MenuItem>
        )
    });

    const handleDivisionChange = (e,id)=> {

        console.log('handleDivisionChange')
        console.log(e)
        let arr = minDivStages;
        const exists = arr.filter(st=>st.division === e.target.value).length > 0
        if(!exists)
        {
            arr.push({id:id,division:e.target.value,stage:""})            
            setMinDivStages([...arr])
            appendstageIterator([...arr])
        }
        
        console.log(minDivStages)
    }
    const handleDivisionStageChange = (e,id)=> {

        let arr = minDivStages;
        const exists = arr.filter(st=>st.id === id).length > 0
        if(exists)
        {
            arr.filter(st=>st.id === id).forEach(item=>item.stage = e.target.value)

        }
        setMinDivStages([...arr])
        console.log('handleDivisionStageChange')    
        console.log(e)
        console.log(minDivStages)
    }

    console.log("Divstages")
    console.log(minDivStages)

    const deleteMinistryDivision = (id)=>{

        let existing = stageIterator;
        let updatedIterator = existing.filter(i=>i.id !== id);
       
        appendstageIterator([...updatedIterator])
        setMinDivStages([...updatedIterator])
       

    }

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

    var stageCounter = []
    stageCounter.push({id:0,division:"",stage:""})
    const [stageIterator, appendstageIterator] = React.useState(stageCounter);
    
    
    const addDivisionalStage = () => {

        let existing = stageIterator;
        var val = stageIterator[stageIterator.length - 1].id + 1
        if (divisionList.length >= val) {           
            existing.push({id:val,division:"",stage:""})
            appendstageIterator([...existing])
        }
        console.log(stageIterator)
    }


    return (
        <>
            <div id="divstages" >

                {
                    stageIterator.map((item) =>

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