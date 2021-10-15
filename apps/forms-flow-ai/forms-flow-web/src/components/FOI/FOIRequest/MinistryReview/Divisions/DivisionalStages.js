import React, { useEffect, useState } from 'react';
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import './divisionstages.scss';
const DivisionalStages = React.memo((props) => {
    const divisionList = [{ id: "0", division: "Select Division to Send CFR" }, { id: "1", division: "Divison 1" }, { id: "2", division: "Divison 2" }]
    const divisionItems = divisionList.length > 0 && divisionList.map((item) => {

        return (
            <MenuItem className="foi-division-menuitem" key={item.id} value={item.division} >
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

    const handleDivisionChange = (e)=> {

        console.log('handleDivisionChange')
        console.log(e)
    }
    const handleDivisionStageChange = (e)=> {

        console.log('handleDivisionStageChange')    
        console.log(e)
    }

    var divisionalStagesRow = (_id) => {

        return (
            <div className="row foi-details-row" id={_id}>
                <div className="col-lg-5 foi-details-col">
                    <TextField
                        id="foi-division-dropdown"_id
                        className="foi-division-dropdown"
                        InputLabelProps={{ shrink: true, }}
                        select
                        input={<Input />}
                        variant="outlined"
                        onChange={handleDivisionChange}
                        fullWidth                        
                        label="Select Divison"
                    >
                        {divisionItems}
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
                        onChange={handleDivisionStageChange}
                    >
                        {divisionstageItems}
                    </TextField>
                </div>
                <div className="col-lg-2 foi-details-col">
                    <i class="fa fa-trash fa-3 foi-bin" aria-hidden="true"></i>
                </div>
            </div>
        )

    }

    var divstageslist = []
    divstageslist.push(1)
    const [divstages, setdivstages] = React.useState(divstageslist);





    const addDivisionalStage = () => {

        let existing = divstages;
        var val = divstages[divstages.length - 1] + 1
        if (divisionList.length >= val) {
            existing.push(val)
            setdivstages([...existing])
        }
        console.log(divstages)
    }


    return (
        <>
            <div id="divstages" >

                {
                    divstages.map((item) =>
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