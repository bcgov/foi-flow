import React, { useState } from 'react';
import { Autocomplete, TextField } from '@mui/material';
import type { Template } from '../ContactApplicant/types';

const CustomAutocomplete = ({
    list,
    disabledValues,
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
const emailTemplatesGroup = ['A - Applicant Cover Email', 'Fee Estimate', 'Outstanding Fee']

  return (
    <Autocomplete
        size = "small"
        sx = {{ marginTop: '8px !important' }}
        options={list.sort((a: Template, b: Template) => emailTemplatesGroup.includes(a.label) ? -1 : 0)}
        groupBy={(option) => emailTemplatesGroup.includes(option.label) ? 'Email Templates' : 'Letter Templates'}
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
