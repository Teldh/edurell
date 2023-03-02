import React from 'react';
import Container from '@mui/material/Container';
import { Autocomplete } from '@mui/material';
import { TextField } from '@material-ui/core';
import './Querybar.css';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
export default function Querybar(){
    const options = ['Option 1', 'Option 2', 'Option 3', 'Option 4'];
    return(
        <>
        <Container maxWidth="false" className="containerBig">
            <Container maxWidth = "xl" >

      
                <Autocomplete
                    multiple
                    limitTags={2}
                    id="multiple-limit-tags"
                    options={options}
                    getOptionLabel={(option) => option}
                    renderInput={(params) => (
                        <TextField {...params} label="select the concepts" placeholder="Concepts" />
                    )}
                    sx={{ width: '500px' }}
                />
            </Container>
            <br/>
            <br/>
            <Container maxWidth = "xl">
                <Grid item xs={12}>
                    <Grid container justifyContent="left" spacing={2}>
                    {[0, 1, 2].map((value) => (
                        <Grid key={value} item>
                        <Paper
                            sx={{
                            height: 140,
                            width: 100,
                            backgroundColor: (theme) =>
                                theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
                            }}
                        />
                        </Grid>
                    ))}
                    </Grid>
                </Grid>
            </Container>
        </Container>


        

        </>
    );
}