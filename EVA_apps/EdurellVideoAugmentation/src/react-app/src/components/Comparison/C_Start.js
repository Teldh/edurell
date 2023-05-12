import React from 'react';
import Container from '@mui/material/Container'
import '../Header/Header.css';
import './Comparison.css';
import { Autocomplete } from '@mui/material';
import { TextField } from '@material-ui/core';
import Stack from '@mui/material/Stack';
import './Queryinput.css';
import Typography from '@mui/material/Typography';
import InputAdornment from '@mui/material/InputAdornment'
import SearchRoundedIcon from '@mui/icons-material/SearchRounded';

export default function C_Start({Endcstart}){
    return (
        <>
        <Container maxWidth="false" 
            style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100vh',
            }}>
            <Stack spacing={2}>
                <Typography variant="h1" 
                    gutterBottom  
                    className="logofirstpage"
                    style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
        
                    }}>
                        Edurell
                </Typography>
                <TextField
                    style={{width: '700px'}}
 
                    className="backColor" 
                    variant="outlined" 
                
                    placeholder="Cerca i concetti che vuoi approfondire" 
                    InputProps={{
                        startAdornment: (
                            <InputAdornment position="start">
                                <SearchRoundedIcon sx={{color:"rgb(255,128,0)"}}/>
                            </InputAdornment>
                        )
                    }}
                    onChange={() => {
                        Endcstart();
                      }}
                />
            </Stack>
            
     
          
        
        
            
   
        </Container>



        </>
    );
}