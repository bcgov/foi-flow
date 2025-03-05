import React, { useState } from 'react';
import { Autocomplete, TextField } from '@mui/material';
import type { Template } from '../ContactApplicant/types';

const CustomAutocomplete = ({
    list,
    onChange,
    label
}: any) => {
  const [inputValue, setInputValue] = useState<string>('');
  const [selectedOption, setSelectedOption] = useState<Template | null>(null);

  const handleInputChange = (event: React.ChangeEvent<{}>, value: string) => {
    setInputValue(value);
  };

  const handleChange = (event: React.ChangeEvent<{}>, value: Template | null) => {
    setSelectedOption(value);
    onChange(event, value);
  };

  return (
    <Autocomplete
        size = "small"
        sx = {{ marginTop: '8px !important' }}
        options={list}
        getOptionLabel={(option) => option.label}
        value={selectedOption}
        inputValue={inputValue}
        onInputChange={handleInputChange}
        onChange={handleChange}
        renderInput={(params) => <TextField {...params} label={label} variant="outlined" />}
    />
  );
};

export default CustomAutocomplete;
