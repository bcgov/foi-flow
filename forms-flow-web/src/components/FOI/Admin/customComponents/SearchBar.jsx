import React, { useState, useEffect } from "react";
import Autocomplete from "@mui/material/Autocomplete";
import InputBase from "@mui/material/InputBase";
import Paper from "@mui/material/Paper";
import IconButton from "@mui/material/IconButton";
import SearchIcon from "@material-ui/icons/Search";

const SearchBar = ({  items, setSearchResults }) => {
  const [keywords, setKeywords] = useState(null);

  useEffect(async () => {
    handleSearch();
  }, [items]);

  const handleSubmit = (event) => {
    event.preventDefault();
    handleSearch();
  };

  const handleSearch = () => {
    let searchKeywords = keywords ? keywords.toLowerCase().split(" ") : [];

    if (searchKeywords.length == 0) {
      setSearchResults(null);
      return;
    }

    let results = items.reduce((found, item) => {
      let matches = 0;
      searchKeywords.forEach((keyword) => {
        let props = 0;
        for (let prop in item) {
          if (
            typeof item[prop] == "string" &&
            item[prop].toLowerCase().indexOf(keyword) > -1
          ) {
            props++;
          }
        }
        if (props >= 1) {
          matches++;
        }
      });
      if (matches == searchKeywords.length) {
        found.push(item);
      }
      return found;
    }, []);
    setSearchResults(results.length != items.length ? results : []);
  };

  return (
    <Paper
      fullWidth
      component="form"
      onSubmit={handleSubmit}
      className="search-bar-wrapper"
    >
      <InputBase
        id="filter"
        placeholder="Search Keywords"
        value={keywords}
        onChange={(e) => setKeywords(e?.target?.value)}
        sx={{
          color: "#38598A",
        }}
        // startAdornment={
        //   <InputAdornment position="start">
        //     <IconButton sx={{ color: "#38598A" }}>
        //       <span className="hideContent">Search with keyword</span>
        //       <SearchIcon />
        //     </IconButton>
        //   </InputAdornment>
        // }
        fullWidth
      />
      {/* {autocompleteOptions && 
        <Autocomplete
          freeSolo
          fullWidth
          className="search-bar-autocomplete"
          options={autocompleteOptions}
          onChange={(e, value) => setKeywords(value)}
          renderInput={(params) => (
            <InputBase
              {...params}
              ref={params.InputProps.ref}
              inputProps={params.inputProps}
              placeholder="Search Divisions"
              fullWidth
              value={keywords}
            />
          )}
        />
        } */}
      <IconButton
        type="button"
        size="small"
        sx={{ p: "5px" }}
        onClick={() => handleSearch()}
      >
        <SearchIcon />
      </IconButton>
    </Paper>
  );
};

export default SearchBar;
