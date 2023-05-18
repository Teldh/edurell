import React from 'react';
import Container from '@mui/material/Container';
import { Autocomplete } from '@mui/material';
import { TextField } from '@material-ui/core';
import './Querybar.css';
import Chip from '@mui/material/Chip';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Videoavailable from "./Videoavailable.js"
import VideoFiltered from "./VideoFiltered.js"
import {TokenContext} from '../account-management/TokenContext';
import { useContext } from 'react';

export default function Listvideo({catalogExtra, catalog,loading, querylist, catalogoriginal}){
    
    
    const context = useContext(TokenContext);
    console.log("listvideo querylist ",querylist)


      
    return (
    <>
    <Container maxWidth = "xl" >
            <Grid
        container
        direction="row"
        justifyContent="center"
        alignItems="center"
        spacing={2}
        sx={{p:5}}
        >


        {loading
              ? null
              :
            querylist.length > 0?
            catalog.map(video=>{
                console.log("LISTVIDEO: ",catalogExtra)
                let singlecatExtra = catalogExtra.filter(extra =>video.video_id == extra.video_id)
                console.log(video.video_id," extra ",singlecatExtra)
                return(
                    
                    <Grid key={video._id.$oid} item xs={12} xl={2} md={3} >
                        <VideoFiltered tottime={video.duration} conceptextra={singlecatExtra} titleurl={video.title} imageurl={video.video_id} idxurl={video._id.$oid} concepts={video.extracted_keywords} creator={video.creator}/>
                    </Grid>
                );
                
                
                
            })
            :
        catalog.map(video=>{
          
            return(
                
                <Grid key={video._id.$oid} item xs={12} xl={2} md={3} >
                    <Videoavailable titleurl={video.title} imageurl={video.video_id} idxurl={video._id.$oid} concepts={video.extracted_keywords} creator={video.creator}/>
                </Grid>
            );
            
            
            
        })}
        
        
        </Grid>

        <Grid
  container
  direction="column"
  justifyContent="center"
  alignItems="center"
  spacing={2}
>
        {
            querylist.length>0?<>
            <Grid item>
                <Box
                sx={{
                    m:0,
                    p:0,
                    width: '100px',
                    height: '2px',
                    backgroundColor: "#9BDDC1",
                }}
                />
        </Grid>
        <Grid item>
            <Typography variant="h6" gutterBottom>
                Sembra non ci siano altri video con il concetti che cerchi :&#40;
            </Typography>
            
        </Grid>
        <Grid item>
            <Typography variant="overline" display="block" gutterBottom sx={{color:"black"}}>
                Ti serve altro? Dai un'occhiata agli altri concetti presenti in questi video!
            </Typography>
        </Grid>
        <Grid item>
            {/*INSERT HERE MORE CONCEPTS */}
        </Grid>
        </>
        :
        <></>
        }
        </Grid>
    </Container>
    </>
    );
}


