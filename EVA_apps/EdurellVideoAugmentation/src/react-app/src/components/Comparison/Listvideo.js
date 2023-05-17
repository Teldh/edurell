import React from 'react';
import Container from '@mui/material/Container';
import { Autocomplete } from '@mui/material';
import { TextField } from '@material-ui/core';
import './Querybar.css';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Videoavailable from "./Videoavailable.js"
import VideoFiltered from "./VideoFiltered.js"
import {TokenContext} from '../account-management/TokenContext';
import { useContext } from 'react';

export default function Listvideo({catalogExtra, catalog,loading, searchFilterClicked, catalogoriginal}){
    
    
    const context = useContext(TokenContext);
    


      
    return (
    <>
    <Container maxWidth = "xl" >
        <Grid  align = "center" justify = "center" alignItems = "center" container spacing={2}>


        {loading
              ? null
              :
            searchFilterClicked?
            catalog.map(video=>{
                console.log("LISTVIDEO: ",catalogExtra)
                let singlecatExtra = catalogExtra.filter(extra =>video.video_id == extra.video_id)
                console.log(video.video_id," extra ",singlecatExtra)
                return(
                    
                    <Grid key={video._id.$oid} item xs={12} xl={2} md={3} >
                        <VideoFiltered conceptextra={singlecatExtra} titleurl={video.title} imageurl={video.video_id} idxurl={video._id.$oid} concepts={video.extracted_keywords} creator={video.creator}/>
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
    </Container>
    </>
    );
}


