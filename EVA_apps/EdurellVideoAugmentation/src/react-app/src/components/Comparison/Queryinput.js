import React from 'react';
import { Autocomplete } from '@mui/material';
import { TextField } from '@material-ui/core';
import './Queryinput.css';
import {useState, useEffect} from 'react'
import Secondarybutton from './Buttonsecondary.js'
import ButtonGroup from '@mui/material/ButtonGroup';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import InputAdornment from '@mui/material/InputAdornment'
import SearchRoundedIcon from '@mui/icons-material/SearchRounded';
import Popper from '@mui/material/Popper';
import Stack from '@mui/material/Stack';
import { useContext } from 'react';
import { ContextComparison } from './ContextComparison';
export default function Queryinput({listconcepts,AddQueryElement, nomatch, location}){
    const options = listconcepts;//['Option 1', 'Option 2', 'Option 3', 'Option 4'];
    const [valac, SetValac] = useState([location]);
    console.log("queryinput: ",location," ",location[0].trim().length);
  
    const setSearchFilterClicked = useContext(ContextComparison)[2];


    return(<>{
        location!=null && location[0].trim().length!=0?  
        <Stack
        direction="row"
        spacing={0}
    >
        <Autocomplete
            
            className="bg-primary"
            defaultValue={[location]}
            freeSolo
            multiple
            limitTags={1}
            id="multiple-limit-tags "
            options={options}
      
            renderInput={(params) => (
                <TextField error={nomatch}
                           className="backColor " 
                           id="outlined-basic" 
                     
                            variant='outlined'
                            {...params}
                           placeholder="Concepts" 
                           InputProps={{
                            ...params.InputProps,
                      
                            startAdornment: (
                                <>
                                <InputAdornment position="start">
                                    <SearchRoundedIcon sx={{color:"rgb(255,128,0)"}}/>
                                </InputAdornment>
                                {params.InputProps.startAdornment}
                                </>
                            )
                        }}
                        />
            )}
            sx={{ width: '500px' }}
            onChange={(event,value)=>{
                SetValac(value)
                console.log("autocomplete: ",value)
                setSearchFilterClicked(false)
            }}
         
        
        />
        <Secondarybutton AddQueryElement={AddQueryElement} cs={valac}/>
                </Stack>

              :
              
              <Stack
              direction="row"
              spacing={0}
          >
              <Autocomplete
                        size="large"
                        freeSolo
                        multiple
                        limitTags={1}
                        id="multiple-limit-tags "
                        options={options}
                  
                        renderInput={(params) => (
                            <TextField error={nomatch}
                                        className="backColor" 
                                        id="outlined-basic" 
                                    
                                          {...params}
                                        variant='outlined'
                                        placeholder="Concepts"
                                        InputProps={{
                                            ...params.InputProps,
                                
                                            startAdornment: (
                                                <>
                                                <InputAdornment position="start">
                                                    <SearchRoundedIcon sx={{color:"rgb(255,128,0)"}}/>
                                                </InputAdornment>
                                                {params.InputProps.startAdornment}
                                                </>
                                            )
                                        }}
                                         />
                        )}
                        sx={{ width: '500px' }}
                        onChange={(event,value)=>{
                            SetValac(value)
                            console.log("autocomplete: ",value)
                            setSearchFilterClicked(false)
                        }}
                    
                    />
    <Secondarybutton AddQueryElement={AddQueryElement} cs={valac}/>

                </Stack>
      
            }
        
            </>
    );
}


/*
OLD AUTOCOMPLETE
<Autocomplete
            className="bg-primary"
            defaultValue={[location]}
            freeSolo
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
                           label={nomatch?"No match. Try new concepts.":"search" }
                           placeholder="Concepts" />
            )}
            sx={{ width: '500px' }}
            onChange={(event, value) => {
                AddQueryElement(value);
              }}
        
        />

*/