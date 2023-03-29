import React, { useState } from "react";
import Autocomplete from "@mui/material/Autocomplete";
import InputBase from "@mui/material/InputBase";
import Paper from "@mui/material/Paper";
import IconButton from "@mui/material/IconButton";
import SearchIcon from "@material-ui/icons/Search";

const SearchBar = ({ autocompleteOptions, items, setSearchResults }) => {
  const [keywords, setKeywords] = useState(null);

  const handleSubmit = (event) => {
    event.preventDefault();
    handleSearch();
  }
  const handleSearch = () => {
    let searchKeywords = keywords ? keywords.toLowerCase().split(" ") : [];

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

    console.log(items);
    console.log(results);
    setSearchResults(results);
  };

  return (
    <Paper
      fullWidth
      component="form"
      onSubmit={handleSubmit}
      className="search-bar-wrapper"
    >
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
