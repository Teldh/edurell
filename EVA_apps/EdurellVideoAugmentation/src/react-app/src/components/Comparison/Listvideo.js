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
import { useContext, forwardRef } from 'react';

const Listvideo = forwardRef(({setAnchor2, UpdateCatalogExtra, catalogExtra, catalog,loading, querylist, catalogoriginal}, ref)=>{
    
    
    const context = useContext(TokenContext);
    //console.log("listvideo querylist ",querylist)


      
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
            catalog.map((video,idx)=>{
                //console.log("LISTVIDEO: ",catalogExtra)
                let singlecatExtra = catalogExtra.filter(extra =>video.video_id == extra.video_id)
                //console.log(video.video_id," extra ",singlecatExtra)
                return(<>
                    {
                        idx==0?
                        <Grid key={video._id.$oid} item xs={12} xl={2} md={3} >
                        <VideoFiltered setAnchor2={setAnchor2} idx={idx} catalog={catalog} querylist={querylist} UpdateCatalogExtra={UpdateCatalogExtra} tottime={video.duration} conceptextra={singlecatExtra} titleurl={video.title} imageurl={video.video_id} idxurl={video._id.$oid} concepts={video.extracted_keywords} creator={video.creator}/>
                        </Grid>
                        :
                        <Grid key={video._id.$oid} item xs={12} xl={2} md={3} >
                        <VideoFiltered setAnchor2={setAnchor2} idx={idx} catalog={catalog} querylist={querylist} UpdateCatalogExtra={UpdateCatalogExtra} tottime={video.duration} conceptextra={singlecatExtra} titleurl={video.title} imageurl={video.video_id} idxurl={video._id.$oid} concepts={video.extracted_keywords} creator={video.creator}/>
                        </Grid>
                    }
                    </>
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
            <b>It looks like there are no more videos about this concept :&#40;</b> 
            </Typography>
            
        </Grid>
        <Grid item>
            <Typography variant="overline" display="block" gutterBottom sx={{color:"black"}}>
                Do you need anything else? Take a look at these other concepts from the videos we found!
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
});

export default Listvideo;


