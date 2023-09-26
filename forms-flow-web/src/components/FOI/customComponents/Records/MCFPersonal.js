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

const MCFPersonal = ({
    setNewDivision,
    tagValue,
    divisionModalTagValue
}) => {

    const [searchValue, setSearchValue] = useState("");
    const [showAdditionalTags, setShowAdditionalTags] = useState(false);
    const [additionalTagList, setAdditionalTagList] = useState([]);

    const MCFSections = useSelector((state) => state.foiRequests.foiPersonalSections);
    const [tagList, setTagList] = useState(MCFSections?.sections?.slice(0, 30));
    const [otherTagList, setOtherTagList] = useState(MCFSections?.sections?.slice(31));
    
    useEffect(() => {
      setTagList(MCFSections?.sections?.slice(0, 30));
      setOtherTagList(MCFSections?.sections?.slice(31));
    },[MCFSections])

    useEffect(() => {
      setAdditionalTagList(searchSections(otherTagList, searchValue, tagValue));
    },[searchValue, otherTagList, tagValue])

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

    return (
    <>
      <div>
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
              clicked={divisionModalTagValue == tag.divisionid}
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
        </div>
      </div>
    </>
    );
};

export default MCFPersonal;