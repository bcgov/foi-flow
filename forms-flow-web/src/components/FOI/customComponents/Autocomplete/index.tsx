import React, { useState } from 'react';
import { Autocomplete, TextField } from '@mui/material';

export interface OptionType {
  label: string;
  value: string;
}

const options: OptionType[] = [
  { label: 'Option 1', value: 'option1' },
  { label: 'Option 2', value: 'option2' },
  { label: 'Option 3', value: 'option3' }
];

const CustomAutocomplete = ({
    list,
    onChange,
    label
}: any) => {
  const [inputValue, setInputValue] = useState<string>('');
  const [selectedOption, setSelectedOption] = useState<OptionType | null>(null);

  const handleInputChange = (event: React.ChangeEvent<{}>, value: string) => {
    setInputValue(value);
  };

  const handleChange = (event: React.ChangeEvent<{}>, value: OptionType | null) => {
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
