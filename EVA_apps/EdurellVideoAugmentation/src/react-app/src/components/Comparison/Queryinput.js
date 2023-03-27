import React from 'react';
import { Autocomplete } from '@mui/material';
import { TextField } from '@material-ui/core';
import './Queryinput.css';
import {useState} from 'react'


export default function Queryinput({listconcepts,AddQueryElement, nomatch}){
    const options = listconcepts;//['Option 1', 'Option 2', 'Option 3', 'Option 4'];
    return(<>
        <Autocomplete
            
            multiple
            limitTags={2}
            id="multiple-limit-tags "
            options={options}
            getOptionLabel={(option) => option}
            renderInput={(params) => (
                <TextField error={nomatch}
                           className="backColor" 
                           id="outlined-basic" 
                           variant="outlined" {...params} 
                           label={nomatch?"No match. Try new concepts.":"select the concepts" }
                           placeholder="Concepts" />
            )}
            sx={{ width: '500px' }}
            onChange={(event, value) => {
                AddQueryElement(value);
              }}
        
        />
        
      </>
    );
}