import React, { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import {
  ClickableChip  
} from "../../Dashboard/utils";
import "../FileUpload/FileUpload.scss";
import Grid from "@material-ui/core/Grid";
import Paper from "@mui/material/Paper";
import SearchIcon from "@material-ui/icons/Search";
import InputAdornment from "@mui/material/InputAdornment";
import InputBase from "@mui/material/InputBase";
import IconButton from "@material-ui/core/IconButton";
import _ from 'lodash';
import { MSDPopularSections } from "../../../../constants/FOI/enum";

const MSDPersonal = ({
    setNewDivision,
    tagValue,
    divisionModalTagValue,
    divisions = []
}) => {
    const [searchValue, setSearchValue] = useState("");
    const [additionalTagList, setAdditionalTagList] = useState([]);
    const [showChildTags, setShowChildTags] = useState(false);
    const [showAdditionalTags, setShowAdditionalTags] = useState(false);
    const [newDivisions, setNewDivisions] = useState([]);

    const MSDSections = useSelector((state) => state.foiRequests.foiPersonalDivisionsAndSections);
    const [tagList, setTagList] = useState(MSDSections?.divisions[0]?.sections?.slice(0, MSDPopularSections-1));
    const [otherTagList, setOtherTagList] = useState(MSDSections?.divisions[0]?.sections?.slice(MSDPopularSections));
    
    useEffect(() => {
      setTagList(MSDSections?.divisions[0]?.sections?.slice(0, MSDPopularSections-1));
      setOtherTagList(MSDSections?.divisions[0]?.sections?.slice(MSDPopularSections));
    },[MSDSections])

    const searchSections = (_sectionArray, _keyword, _selectedSectionValue) => {
      let newSectionArray = [];
      if(_keyword || _selectedSectionValue) {
        _sectionArray.map((section) => {
          if(_keyword && section.name.toLowerCase().includes(_keyword.toLowerCase())) {
            newSectionArray.push(section);
          } else if(section.divisionid === _selectedSectionValue) {
            newSectionArray.unshift(section);
          }
        });
      }

      if(newSectionArray.length > 0) {
        setShowAdditionalTags(true);
      } else {
        setShowAdditionalTags(false);
      }
      return newSectionArray;
    }

    let divs = [];
    useEffect(() => {
      if(divisions?.length > 0) {
        divs = [];
        divisions.forEach(division => {
          if(division.display == "SDD Document Tracking") {
            setShowChildTags(true);
          } else {
            divs.push(
              {
                divisionid: division.name,
                divisionname: division.display,
              }
            );
          }
        });
        setNewDivisions(divs);
      }
    },[divisions])

    useEffect(() => {
      setAdditionalTagList(searchSections(otherTagList, searchValue, tagValue));
    },[searchValue, otherTagList, tagValue])

    return (
    <>
      <div>
        <div className="tagtitle" style={{paddingTop: "15px"}}>
          <span>Personals Divisional Tracking: </span>
        </div>
        <div className="taglist">
          {newDivisions.filter(div => {
            return div.divisionid !== tagValue;
          }).map(tag =>
            <ClickableChip
              id={`${tag.divisionid}Tag`}
              key={`${tag.divisionid}-tag`}
              label={tag.divisionname.toUpperCase()}
              sx={{width: "fit-content", marginRight: "8px", marginBottom: "8px"}}
              color="primary"
              size="small"
              onClick={()=>{setNewDivision(tag.divisionid)}}
              clicked={tag.divisionid == divisionModalTagValue}
            />
          )}
        </div>
        {showChildTags === true && (<>
        <div className="tagtitle">
          <span>SDD Document Tracking: </span>
        </div>
        <div className="taglist">
          {tagList.filter(div => {
            return div.divisionid !== tagValue;
          }).map(tag =>
            <ClickableChip
              id={`${tag.divisionid}Tag`}
              key={`${tag.divisionid}-tag`}
              label={tag.name.toUpperCase()}
              sx={{width: "fit-content", marginRight: "8px", marginBottom: "8px"}}
              color="primary"
              size="small"
              onClick={()=>{setNewDivision(tag.divisionid)}}
              clicked={tag.divisionid == divisionModalTagValue}
            />
          )}
        </div>
        <div className="taglist">
          <Grid
            container
            item
            direction="row"
            justify="flex-start"
            alignItems="flex-start"
            xs={12}
            sx={{
              marginTop: "1em",
            }}
          >
            <Paper
              component={Grid}
              sx={{
                border: "1px solid #38598A",
                color: "#38598A",
                maxWidth:"100%",
                backgroundColor: "rgba(56,89,138,0.1)",
                borderBottomLeftRadius: 0,
                borderBottomRightRadius: 0
              }}
              alignItems="center"
              justifyContent="center"
              direction="row"
              container
              item
              xs={12}
              elevation={0}
            >
              <Grid
                item
                container
                alignItems="center"
                direction="row"
                xs={true}
                className="search-grid"
              >
                <label className="hideContent">Search any additional sections here</label>
                <InputBase
                  id="foirecordsfilter"
                  placeholder="Search any additional sections here"
                  defaultValue={""}
                  onChange={(e)=>{setSearchValue(e.target.value.trim())}}
                  sx={{
                    color: "#38598A",
                  }}
                  value={searchValue}
                  startAdornment={
                    <InputAdornment position="start">
                      <IconButton
                        aria-label="Search Icon"
                        className="search-icon"
                      >
                        <span className="hideContent">Search any additional sections here</span>
                        <SearchIcon />
                      </IconButton>
                    </InputAdornment>
                  }
                  fullWidth
                />
              </Grid>
            </Paper>
            {showAdditionalTags === true && (<Paper
              component={Grid}
              sx={{
                border: "1px solid #38598A",
                color: "#38598A",
                maxWidth:"100%",
                padding: "8px 15px 0 15px",
                borderTopLeftRadius: 0,
                borderTopRightRadius: 0,
                borderTop: "none",
                maxHeight:"120px",
                overflowY:"auto"
              }}
              alignItems="center"
              justifyContent="flex-start"
              direction="row"
              container
              item
              xs={12}
              elevation={0}
            >
              {additionalTagList.filter(div => {
                return div.divisionid !== tagValue;
              }).map(tag =>
                <ClickableChip
                  id={`${tag.divisionid}Tag`}
                  key={`${tag.divisionid}-tag`}
                  label={tag.name.toUpperCase()}
                  sx={{width: "fit-content", marginRight: "8px", marginBottom: "8px"}}
                  color="primary"
                  size="small"
                  onClick={()=>{setNewDivision(tag.divisionid)}}
                  clicked={divisionModalTagValue == tag.divisionid}
                />
              )}
            </Paper>)}
          </Grid>
        </div></>)}
      </div>
    </>
    );
};

export default MSDPersonal;