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
import EastIcon from '@mui/icons-material/East';

export default function Querybar({ApplyFilters, searchClicked, listvideo, listconcepts, AddQueryElement, nomatch, location}){
    

    function GoToComparisonResult(){

    }

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
                  
                  
                    <Filters ApplyFilters={ApplyFilters}/>
                </Grid>
            </Container>
            <br/>
            <br/>
            {
                //searchClicked == false?
                listvideo.length == 0?
                <></>
                :



                <Container maxWidth = "xl">
                    <Stack
                        direction="row"
                        justifyContent="center"
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
                                <Grid
                                container
                                direction="column"
                                justifyContent="center"
                                alignItems="center"
                                sx={{width:"auto"}}
                                spacing={2}
                                >
                                    <Grid item>
                                        <Box sx={{paddingTop:1}}>
                                            {
                                                listvideo.length<4?<Chip sx={{backgroundColor:"rgb(198,203,239)"}}label={listvideo.length+"/4 video selected"} />:<Chip sx={{backgroundColor:"rgb(177,150,255)"}} label="4/4 max reached"  />
                                            }
                                        
                                        </Box>
                                    </Grid>
                                    <Grid item>
                                        {
                                            listvideo.length >1?
                                            <>
                                                <Typography variant="body2" display="block" gutterBottom>
                                                    Hai selezionato tutti i
                                                </Typography>
                                                <Typography variant="body2" display="block" gutterBottom>
                                                    video che ti interessano?
                                                </Typography>
                                            </>
                                            :
                                            <>
                                                <Typography variant="body2" display="block" gutterBottom sx={{pb:0, mb:0}}>
                                                    Seleziona almeno un altro 
                                                </Typography>
                                                <Typography variant="body2" display="block" gutterBottom sx={{pt:0, mt:0}}>
                                                    video per confrontarli
                                                </Typography>
                                            </>
                                        }
                                        
                                    </Grid>
                                    <Grid item>
                                        <Chip
                                        disabled={listvideo.length>1?false:true}
                                        label={<Typography variant="body2" gutterBottom sx={{pt:1}}>
                                       Vai al confronto
                                      </Typography>}
                                        onClick={GoToComparisonResult}
                                        onDelete={GoToComparisonResult}
                                        deleteIcon={<EastIcon />}
                                        sx={{backgroundColor:"white"}}
                                        />
                                    </Grid>

                                </Grid>
                                
                                </>
                                ) :
                                <>
                                {listvideo}
                                <Grid
                                container
                                direction="column"
                                justifyContent="center"
                                alignItems="center"
                                sx={{width:"auto"}}
                                spacing={2}
                                >
                                    <Grid item>
                                        <Box sx={{paddingTop:1}}>
                                            {
                                                listvideo.length<4?<Chip sx={{backgroundColor:"rgb(198,203,239)"}}label={listvideo.length+"/4 video selected"} />:<Chip sx={{backgroundColor:"rgb(177,150,255)"}} label="4/4 max reached"  />
                                            }
                                        
                                        </Box>
                                    </Grid>
                                    <Grid item>
                                        <Typography variant="body2" display="block" gutterBottom>
                                            Hai raggiunto il <b>numero</b> 
                                        </Typography>
                                        <Typography variant="body2" display="block" gutterBottom>
                                            <b>massimo</b> di video selezionabili
                                        </Typography>
                                    </Grid>
                                    <Grid item>
                                        <Chip
                                        label={<Typography variant="h6" gutterBottom>
                                       Vai al confronto
                                      </Typography>}
                                        onClick={GoToComparisonResult}
                                        onDelete={GoToComparisonResult}
                                        deleteIcon={<EastIcon />}
                                        />
                                    </Grid>

                                </Grid>
                                
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