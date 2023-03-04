import React from 'react';
import Container from '@mui/material/Container';
import { Autocomplete } from '@mui/material';
import { TextField } from '@material-ui/core';
import './Querybar.css';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Videoavailable from "./Videoavailable.js"


export default function Listvideo(){

    return (
    <>
    <Container maxWidth = "xl" >

        <RowVideo/>
 
    </Container>
    </>
    );
}


function RowVideo(){
    return (
        <>
  
        <Grid  align = "center" justify = "center" alignItems = "center" container spacing={2}>
        <Grid  item xs={12} xl={2} md={3} >
            <Videoavailable/>
        </Grid>
        <Grid  item xs={12} xl={2} md={3} >
            <Videoavailable/>
        </Grid>
        <Grid  item xs={12} xl={2} md={3} >
            <Videoavailable/>
        </Grid>
        <Grid  item xs={12} xl={2} md={3} >
            <Videoavailable/>
        </Grid>
        <Grid  item xs={12} xl={2} md={3} >
            <Videoavailable/>
        </Grid>
        <Grid  item xs={12} xl={2} md={3} >
            <Videoavailable/>
        </Grid>
       
        
      
        </Grid>
        

        </>
    );
}