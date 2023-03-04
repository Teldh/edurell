import React from 'react';
import { Autocomplete } from '@mui/material';
import { TextField } from '@material-ui/core';
import './Queryinput.css';


export default function Queryinput(){
    const options = ['Option 1', 'Option 2', 'Option 3', 'Option 4'];
    return(<>
        <Autocomplete
            multiple
            limitTags={2}
            id="multiple-limit-tags "
            options={options}
            getOptionLabel={(option) => option}
            renderInput={(params) => (
                <TextField className="backColor" id="outlined-basic" variant="outlined" {...params} label="select the concepts" placeholder="Concepts" />
            )}
            sx={{ width: '500px' }}
        />
        
      </>
    );
}