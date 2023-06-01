import React from 'react';
import TuneRoundedIcon from '@mui/icons-material/TuneRounded';
import Container from '@mui/material/Container';
import './Querybar.css';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Queryinput from './Queryinput.js'
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import Secondarybutton from './Buttonsecondary.js'
import { grey } from '@mui/material/colors';
import Videoselected from './Videoselected';
import Divider from '@mui/material/Divider';
import Skeleton from '@mui/material/Skeleton';
import HelpIcon from '@mui/icons-material/Help';
import { Typography } from '@mui/material';
import Chip from '@mui/material/Chip';
import Box from '@mui/material/Box';
import Filters from './Filters.js'
import EastIcon from '@mui/icons-material/East';
import { useHistory } from "react-router-dom";
import { useContext ,useState, forwardRef} from 'react';
import { ContextComparison } from './ContextComparison';
import IconButton from '@mui/material/IconButton';
import { styled } from '@mui/material/styles';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
const ExpandMore = styled((props) => {
    const { expand, ...other } = props;
    return <IconButton {...other} />;
})(({ theme, expand }) => ({
    transform: !expand ? 'rotate(0deg)' : 'rotate(180deg)',
    margin: '0',
    padding:'0',
    transition: theme.transitions.create('transform', {
      duration: theme.transitions.duration.shortest,
    }),
}));


const Querybar = forwardRef(({ openTutorial,querylist, catalog, catalogExtra, ApplyFilters, searchClicked, listvideo, listconcepts, AddQueryElement, nomatch, location}, ref) => {
    const [expanded, setExpanded] = useState(false);
    const handleExpandClick = () => {
        setExpanded(!expanded);
    };
    
    const listConcepts = useContext(ContextComparison)[3];
    const history = useHistory();
    function GoToComparisonResult(){
        
        history.push({
            pathname: '/comparisonResult',
            state: { 
                concept: querylist[0],
                catalog: catalog.filter(video=>{
                    if(listvideo.filter(lv=>lv.img==video.video_id).length > 0){
                        return video.video_id == listvideo.filter(lv=>lv.img == video.video_id)[0].img
                    }else{
                        return false
                    }
                    }),
                catalogExtra: catalogExtra.filter(video=>{
                    if(listvideo.filter(lv=>lv.img==video.video_id).length > 0){
                        return video.video_id == listvideo.filter(lv=>lv.img == video.video_id)[0].img
                    }else{
                        return false
                    }
                    }),
                listConcepts: listConcepts
            },
        });
    }

    let videos = listvideo.map((video,index) =>
    
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
                justifyContent="center"
                alignItems="center"
                >
                    <Grid item>
                            <Grid
                            container
                            direction="row"
                            justifyContent="center"
                            alignItems="center"
                            >
                                {
                                    querylist.length > 0 && querylist[0]!=null?
                                    <Grid item sx={{mr:1}}>
                                    <Chip 
                                        
                                        label={<Typography variant="caption" display="block" gutterBottom sx={{color:"white",mt:1}}>
                                            <b>Help</b>
                                            </Typography>}
                                        deleteIcon={<HelpIcon style={{fill:"white"}}/>}
                                        onClick={openTutorial}
                                        onDelete={openTutorial}
                                        sx={{
                                            backgroundColor:"#FFA825"
                                        }}
                                    />

                                        
                              
                                </Grid>
                                :
                                <></>
                                }
                                
                            
                               
                                <Grid item>
                                    <Queryinput listconcepts={listconcepts} AddQueryElement={AddQueryElement} nomatch={nomatch} location={location}/>
                                </Grid>
                                <Grid item>
                                    <div style={{zIndex:1, position:"relative"}} ref={ref}>
                                {
                                    querylist.length > 0 && querylist[0]!=null?
                                  
                                       
                                        
                                    <Chip 
                                        clickable={false}
                                        sx={expanded?{width:'auto', margin:'5px',backgroundColor:'white'}:{width:'auto',margin:'5px', backgroundColor:"#c6ebdc"}}
                                        
                                        avatar={<TuneRoundedIcon/>}
                                        label={<Typography variant="caption" display="block" gutterBottom sx={{m:0.5}}>
                                        Filters
                                    </Typography>} 
                                        onClick={handleExpandClick}
                                        onDelete={handleExpandClick}
                                        deleteIcon={
                                            <ExpandMore
                                            expand={expanded}
                                    
                                            aria-expanded={expanded}
                                            aria-label="show more"
                                            >
                                                <ExpandMoreIcon />
                                            </ExpandMore>
                                        }
                                    />
                              
                                   
                                :
                                <></>
                                }
                               
                                </div>
                                </Grid>
                                
                            </Grid>
                    </Grid>
                    <Grid item>
                        <Filters ApplyFilters={ApplyFilters} expanded={expanded} />
                    </Grid>
                </Grid>
            </Container>
            <br/>
            <br/>
            {
                //searchClicked == false?
                videos.length == 0?
                <></>
                :



                <Container maxWidth = "xl">
                    <Stack
                        direction="row"
                        justifyContent="center"
                        alignItems="center"
                        spacing={2}
                    >
                        {videos.length < 4? 
                                ( <>
                                {videos}
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
                                                videos.length<4?<Chip sx={{backgroundColor:"rgb(198,203,239)"}}label={videos.length+"/4 video selected"} />:<Chip sx={{backgroundColor:"rgb(177,150,255)"}} label="4/4 max reached"  />
                                            }
                                        
                                        </Box>
                                    </Grid>
                                    <Grid item>
                                        {
                                            videos.length >1?
                                            <>
                                                <Typography variant="body2" display="block" gutterBottom>
                                                    Did you pick all of the
                                                </Typography>
                                                <Typography variant="body2" display="block" gutterBottom>
                                                    videos you are interested in?
                                                </Typography>
                                            </>
                                            :
                                            <>
                                                <Typography variant="body2" display="block" gutterBottom sx={{pb:0, mb:0}}>
                                                    <b>Choose</b> at least <b>one more</b>
                                                </Typography>
                                                <Typography variant="body2" display="block" gutterBottom sx={{pt:0, mt:0}}>
                                                    <b>video</b> to compare them
                                                </Typography>
                                            </>
                                        }
                                        
                                    </Grid>
                                    <Grid item>
                                        <Chip
                                        disabled={videos.length>1?false:true}
                                        label={<Typography variant="body2" gutterBottom sx={{pt:1}}>
                                       Compare these videos
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
                                {videos}
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
                                                videos.length<4?<Chip sx={{backgroundColor:"rgb(198,203,239)"}}label={videos.length+"/4 video selected"} />:<Chip sx={{backgroundColor:"rgb(177,150,255)"}} label="4/4 max reached"  />
                                            }
                                        
                                        </Box>
                                    </Grid>
                                    <Grid item>
                                        <Typography variant="body2" display="block" gutterBottom>
                                            You reached the <b>max</b> 
                                        </Typography>
                                        <Typography variant="body2" display="block" gutterBottom>
                                            <b>number</b> of comparable videos
                                        </Typography>
                                    </Grid>
                                    <Grid item>
                                        <Chip
                                        label={<Typography variant="h6" gutterBottom>
                                       Compare these videos
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
});

export default Querybar;