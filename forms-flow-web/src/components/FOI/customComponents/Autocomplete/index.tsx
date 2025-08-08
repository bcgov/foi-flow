import React, { useState } from 'react';
import { Autocomplete, TextField } from '@mui/material';
import type { Template } from '../ContactApplicant/types';

const CustomAutocomplete = ({
    list,
    disabledValues,
    onChange,
    label,
    resetTemplateDropdownValue,
    setResetTemplateDropdownValue,
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

  React.useEffect(() => {
    if (resetTemplateDropdownValue) {
      setInputValue('');
      setSelectedOption(null);
      setResetTemplateDropdownValue(false);
    }
  }, [resetTemplateDropdownValue]);


  return (
    <Autocomplete
        size = "small"
        sx = {{ marginTop: '8px !important' }}
        options={list.sort((a: Template, b: Template) => a.templatetype === 'email' ? -1 : 1)}
        groupBy={(option) => option.templatetype == 'email' ? 'Email Templates' : 'Letter Templates'}
        getOptionDisabled={(option:any) => disabledValues.includes(option.value)}
        getOptionLabel={(option:any) => option.label}
        value={selectedOption}
        inputValue={inputValue}
        onInputChange={handleInputChange}
        onChange={handleChange}
        renderInput={(params:any) => <TextField {...params} label={label} variant="outlined" />}
    />
  );
};

export default CustomAutocomplete;
