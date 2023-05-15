import React from 'react';
import Container from '@mui/material/Container';
import './Querybar.css';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Queryinput from './Queryinput.js'
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import Secondarybutton from './Buttonsecondary.js'
import Videoselected from './Videoselected';
import Divider from '@mui/material/Divider';
import Skeleton from '@mui/material/Skeleton';
import { Typography } from '@mui/material';
import Chip from '@mui/material/Chip';
import Box from '@mui/material/Box';
import Filters from './Filters.js'

export default function Querybar({setfilter, searchClicked, listvideo, listconcepts, AddQueryElement, nomatch, location}){
 
    listvideo = listvideo.map((video,index) =>
    
        <>
        <Videoselected imageurl={video.img} title={video.title} idx={video.idx} setAdd={video.setAdd}/>
        {index<3?
        <Divider orientation="vertical" flexItem>
                            vs
                        </Divider>:null
        }
                        </>
    );
    return(
        <>
        <Container maxWidth="false" className="containerBig">
            <Container 
                maxWidth = "xl" 
                sx={{
                    display: 'flex',
                    alignItems: 'center',
                    }}>
              
            
                <Grid
          
                container
                direction="column"
                    
                alignItems="center"
                >
                    <Queryinput listconcepts={listconcepts} AddQueryElement={AddQueryElement} nomatch={nomatch} location={location}/>
                  
                  
                    <Filters setfilter={setfilter}/>
                </Grid>
                <Box sx={{paddingTop:1}}>
                    {
                        listvideo.length<4?<Chip label={listvideo.length+"/4 video selected"} size="small" />:<Chip color="error" label="4/4 max reached" size="small" />
                    }
                
                </Box>
            </Container>
            <br/>
            <br/>
            {
                searchClicked == false?
                <></>
                :



                <Container maxWidth = "xl">
                    <Stack
                        direction="row"
                        justifyContent="flex-start"
                        alignItems="center"
                        spacing={2}
                    >
                        {listvideo.length < 4? 
                                ( <>
                                {listvideo}
                                <Stack spacing={0}>
                                
                                <Skeleton variant="rounded" width={200} height={110} />
                                <Skeleton variant="text" sx={{ fontSize: '1rem' ,marginTop: 1}} />
                                <Skeleton variant="text" sx={{ fontSize: '1rem' ,width: "69%"/* xd */}} />
                                
                                </Stack>
                                
                                </>
                                ) :
                                <>
                                {listvideo}
                                
                                </>
                            }
                        
                    </Stack>
                    <br/>
                    <br/>
                    <br/>
                
                    
                </Container>





            }
            
        </Container>


        

        </>
    );
}