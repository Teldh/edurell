import React from 'react';
import Container from '@mui/material/Container';
import { Autocomplete } from '@mui/material';
import { TextField } from '@material-ui/core';
import './Querybar.css';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';

export default function Listvideo(){

    return (
    <>
    <Container maxWidth = "xl" >

        <RowVideo/>
        <br/>
        <RowVideo/>
        <br/>
        <RowVideo/>
    </Container>
    </>
    );
}


function RowVideo(){
    return (
        <Grid container spacing={2}>
            <Grid item xs={2}>
                <Paper
                    sx={{
                    height: 300,
                    width: 200,
                    backgroundColor: (theme) =>
                        theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
                    }}
                />        
            </Grid>

            <Grid item xs={2}>
                <Paper
                    sx={{
                    height: 300,
                    width: 200,
                    backgroundColor: (theme) =>
                        theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
                    }}
                />        
            </Grid>

            <Grid item xs={2}>
                <Paper
                    sx={{
                    height: 300,
                    width: 200,
                    backgroundColor: (theme) =>
                        theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
                    }}
                />        
            </Grid>

            <Grid item xs={2}>
                <Paper
                    sx={{
                    height: 300,
                    width: 200,
                    backgroundColor: (theme) =>
                        theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
                    }}
                />        
            </Grid>

            <Grid item xs={2}>
                <Paper
                    sx={{
                    height: 300,
                    width: 200,
                    backgroundColor: (theme) =>
                        theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
                    }}
                />        
            </Grid>

            <Grid item xs={2}>
                <Paper
                    sx={{
                    height: 300,
                    width: 200,
                    backgroundColor: (theme) =>
                        theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
                    }}
                />        
            </Grid>
            
      
        </Grid>
    );
}