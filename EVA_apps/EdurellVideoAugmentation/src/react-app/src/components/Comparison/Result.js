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
import Chip from '@mui/material/Chip';
import Box from '@mui/material/Box';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Filters from './Filters.js'
import EastIcon from '@mui/icons-material/East';
import '../Header/Header.css';
import './Comparison.css';
import Links from '@mui/material/Link';
import { TextField } from '@material-ui/core';
import './Queryinput.css';
import Typography from '@mui/material/Typography';
import InputAdornment from '@mui/material/InputAdornment'
import SearchRoundedIcon from '@mui/icons-material/SearchRounded';
import Header from '../Header/Header';
import { useContext,useState,useEffect } from 'react';
import AddCircleIcon from '@mui/icons-material/AddCircle';
import {TokenContext} from '../account-management/TokenContext';
import handleFetchHttpErrors from '../../helpers/handleFetchHttpErrors';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';

import {
    Link,
    Redirect,
    Switch, 
    Route,
    useLocation
} from "react-router-dom";
import Autocomplete from '@mui/material/Autocomplete';
import Popper from '@mui/material/Popper';
import { useHistory } from "react-router-dom";
import NetworkGraph from './NetworkGraph.js';
import Barro from './BarroGraph.js';
export default function Result(){
    
    //for second graph
    const [graphcontrol2, setGraphControl2] = useState("one");
    const handleChange = (event, newValue) => {
        setGraphControl2(newValue);
      };

    const context = useContext(TokenContext);
    const nameSurname  = context.nameSurname;
    //get from the previous page the data of the video selected for comparison
    let location = useLocation();
    useEffect(() => {
        if(location.state != undefined)
        console.log("data from previous search comparison: ", location.state.concept," ",location.state.catalog," ",location.state.catalogExtra);
      }, [location]);



    return(<>
        <Header page="dashboard" login={nameSurname}/>
        {/*TOP BAR */}
        <Grid
        container
        direction="row"
        justifyContent="space-between"
        alignItems="center"
        id="BARRA ALTO"
        sx={{backgroundColor: "rgb(198,235,220)"}}
        >
            <Grid item>
                <Autocomplete
                
                className="bg-primary"
                defaultValue={[location.state.concept]}
                freeSolo
                multiple
                limitTags={1}
                id="multiple-limit-tags "

        
                renderInput={(params) => (
                    <TextField 
                            className="backColor " 
                            id="outlined-basic" 
                        
                                variant='outlined'
                                {...params}
                            placeholder="Concepts" 
                            InputProps={{
                                ...params.InputProps,
                        
                                startAdornment: (
                                    <>
                                    <InputAdornment position="start">
                                        <SearchRoundedIcon sx={{color:"rgb(255,128,0)"}}/>
                                    </InputAdornment>
                                    {params.InputProps.startAdornment}
                                    </>
                                )
                            }}
                            />
                )}
                sx={{ width: '500px' }}
                />
            </Grid>



            <Grid item>
                <Grid
                container
                direction="row"
                justifyContent="flex-end"
                alignItems="center"
                
                >
                    {
                        location.state.catalog.map((video,idx)=>{
                           
                            return(
                                idx == 0?
                                <Grid item key={idx} sx={{width:"20"}}>
                                    <Grid
                                    container
                                    direction="row"
                                    justifyContent="center"
                                    alignItems="center"
                                    id="VIDEO"
                                    
                                    >
                                        <Grid item>
                                            <img src={"http://img.youtube.com/vi/"+video.video_id+"/mqdefault.jpg"} alt={video.title} width="50px" height="50px"/>
                                        </Grid>
                                        <Grid item >
                                            <Grid
                                            container
                                            direction="column"
                                            justifyContent="center"
                                            alignItems="flex-start"
                                            sx={{backgroundColor:"white"}}
                                            >
                                                <Grid item sx={{width:"200px"}}>
                                                    <Typography noWrap variant="subtitle2" gutterBottom sx={{margin:0}}>
                                                    <b>{video.title}</b>
                                                    </Typography>
       
                                                </Grid>
                                                <Grid item sx={{width:"200px"}}>
                                                    <Typography noWrap variant="subtitle2" gutterBottom sx={{marginTop:0}}>
                                                    {video.creator}
                                                    </Typography>
                                                </Grid>
                                            </Grid>
                                        </Grid>
                                    </Grid>
                                </Grid>
                                :
                                <>
                                <Grid item>
                                    <AddCircleIcon/>
                                </Grid>
                                <Grid item key={idx} >
                                    <Grid
                                    container
                                    direction="row"
                                    justifyContent="center"
                                    alignItems="center"
                                    id="VIDEO"
                                    sx={{backgroundColor:"white"}}
                                    >
                                        <Grid item>
                                            <img src={"http://img.youtube.com/vi/"+video.video_id+"/mqdefault.jpg"} alt={video.title} width="50px" height="50px"/>
                                        </Grid>
                                        <Grid item>
                                            <Grid
                                            container
                                            direction="column"
                                            justifyContent="center"
                                            alignItems="flex-start"
                                            >
                                                <Grid item sx={{width:"200px"}}>
                                                    <Typography noWrap variant="subtitle2" gutterBottom sx={{margin:0}}>
                                                    <b>{video.title}</b>
                                                    </Typography>
       
                                                </Grid>
                                                <Grid item sx={{width:"200px"}}>
                                                    <Typography noWrap variant="subtitle2" gutterBottom sx={{marginTop:0}}>
                                                    {video.creator}
                                                    </Typography>
                                                </Grid>
                                            </Grid>
                                        </Grid>
                                    </Grid>
                                </Grid>
                                
                                </>
                            );
                        })
                    }
                </Grid>
            </Grid>
        </Grid>
        
        {/*DATA ROWS*/}
        <Grid
        container
        direction="column"
        justifyContent="center"
        alignItems="stretch"
        id="TITLE+THREE DATA ROWS"
        >
            <Grid item>
             <Container maxWidth="xl" sx={{mt:20}}>  
                <Typography variant="h3" gutterBottom sx={{mb:0, pb:0}}>
                    Risultati del confronto
                </Typography>
                <Box
                sx={{
                    m:0,
                    p:0,
                    width: '100px',
                    height: '4px',
                    backgroundColor: "rgb(155,221,193)",
                }}
                />
             </Container>
            </Grid>
            <Grid item sx={{backgroundColor:"rgb(237,237,237)", mt:5, p:5}}>
                <Container maxWidth="xl" sx={{}}>
                    <Grid
                    container
                    direction="column"
                    justifyContent="center"
                    alignItems="stretch"
                    id="CONFRONTO DURATE"
                    >
                        <Grid item>
                            <Grid
                            container
                            direction="column"
                            justifyContent="center"
                            alignItems="center"
                            >
                                <Grid item>
                                <Typography variant="h4" gutterBottom sx={{mb:0,pb:0}}>
                                    Confronto durate
                                </Typography>
                                <Box
                                sx={{
                                    m:0,
                                    p:0,
                                    width: '100px',
                                    height: '4px',
                                    backgroundColor: "rgb(223,216,242)",
                                }}
                                />
                                </Grid>
                            </Grid>
                        </Grid>
                        <Grid item>
                            <Grid
                            container
                            direction="row"
                            justifyContent="space-between"
                            alignItems="center"
                            id="BOTTONI"
                            sx={{pt:5}}
                            >
                                <Grid item>
                                    <Typography variant="caption" display="block" gutterBottom>
                                        Legenda
                                    </Typography>
                                </Grid>
                                <Grid item>
                                    <Grid
                                    container
                                    direction="row"
                                    justifyContent="flex-end"
                                    alignItems="center"
                                    spacing={2}
                                    >
                                        <Grid item>
                                            <Typography variant="caption" display="block" gutterBottom>
                                                Riepilogo
                                            </Typography>
                                        </Grid>
                                        <Grid item>
                                            <Typography variant="caption" display="block" gutterBottom>
                                                Definizione
                                            </Typography>
                                        </Grid>
                                        <Grid item>
                                            <Typography variant="caption" display="block" gutterBottom>
                                                Approfondimento
                                            </Typography>
                                        </Grid>
                                        <Grid item>
                                            <Typography variant="caption" display="block" gutterBottom>
                                                Video Intero
                                            </Typography>
                                        </Grid>
                                    </Grid>
                                </Grid>
                            </Grid>
                            
                        </Grid>
                        <Grid item>
                            <Box
                            sx={{
                                width: '100%',
                                backgroundColor: 'white',
                                borderRadius: '20px',
                                height:"500px"
                            }}
                            >
                            {/*INSERT GRAPH HERE */}
                            
                                <Barro/>    
                            </Box>
                        </Grid>
                        <Grid item sx={{m:5}}>
                            <Grid
                            container
                            direction="row"
                            justifyContent="space-around"
                            alignItems="center"
                            >
                                {

                                    location.state.catalog.map((video,idx)=>{
                                        return(
                                            <Grid item key={idx}>
                                                <Links href={'/app/'+video.video_id+'/'+video.title} underline="hover">
                                                    {video.title}
                                                </Links>
                                            </Grid>
                                        );
                                    })
                                }
                            </Grid>
                        
                        </Grid>
                    </Grid>
                </Container>  
            </Grid>
            <Grid item sx={{backgroundColor:"white", mt:5, p:5}}>
                <Container maxWidth="xl" sx={{}}>
                    <Grid
                    container
                    direction="column"
                    justifyContent="center"
                    alignItems="stretch"
                    id="CONFRONTO MAPPE"
                    >
                        <Grid item>
                            <Grid
                            container
                            direction="column"
                            justifyContent="center"
                            alignItems="center"
                            >
                                <Grid item>
                                <Typography variant="h4" gutterBottom sx={{mb:0,pb:0}}>
                                    Confronto mappe del concetto, cose da sapere e approfondimenti
                                </Typography>
                                <Box
                                sx={{
                                    m:0,
                                    p:0,
                                    width: '100px',
                                    height: '4px',
                                    backgroundColor: "orange",
                                    
                                }}
                                />
                                </Grid>
                            </Grid>
                        </Grid>
                        <Grid item>
                            <Grid
                            container
                            direction="row"
                            justifyContent="space-between"
                            alignItems="center"
                            id="BOTTONI"
                            sx={{pt:5}}
                            >
                                <Grid item>
                                    <Typography variant="caption" display="block" gutterBottom>
                                        Legenda
                                    </Typography>
                                </Grid>
                                <Grid item>
                                    <Grid
                                    container
                                    direction="row"
                                    justifyContent="flex-end"
                                    alignItems="center"
                                    spacing={2}
                                    >
                                        <Grid item>
                                        <Tabs
                                        value={graphcontrol2}
                                        onChange={handleChange}
                                        textColor="secondary"
                                        indicatorColor="secondary"
                                        aria-label="secondary tabs example"
                                       
                                    >
                                        <Tab value="one" label={<Typography variant="caption" display="block" gutterBottom>
                                            Riepilogo
                                        </Typography>} />
                                        <Tab value="two" label={<Typography variant="caption" display="block" gutterBottom>
                                            Cosa devi gia sapere?
                                        </Typography>} />
                                        <Tab value="three" label={<Typography variant="caption" display="block" gutterBottom>
                                            Cosa imparerai?
                                        </Typography>}/>
                                    </Tabs>
                                        </Grid>
                                       
                                    </Grid>
                                </Grid>
                            </Grid>
                            
                        </Grid>
                        <Grid item>
                            <Box
                            sx={{
                                width: '100%',
                                backgroundColor: 'white',
                                borderRadius: '10px',
                                height:"500px",
                                border: '1px solid grey',
                            }}
                            >
                                <Grid
                                    container
                                    direction="row"
                                    justifyContent="space-between"
                                    alignItems="stretch"
                                    sx={{
                                        width:"100%",
                                        height:"100%"
                                    }}
                                >
                                    {/*INSERT GRAPH HERE */}
                                    {
                                        
                                        location.state.catalogExtra.map((catExtra,idx)=>{
                                            console.log("catalogExtraFULL: ",location.state.catalogExtra);
                                            console.log("catExtra: ",catExtra)
                                            return(<>
                                                <Grid item xs>
                                                    <NetworkGraph width="100%" height="100%" concept={location.state.concept} conceptExtra={catExtra} idx={idx} graphcontrol={graphcontrol2}/>
                                                </Grid>
                                                <Divider orientation="vertical" variant="middle" flexItem  />
                                            </>
                                            );
                                        })
                                    }
                            <NetworkGraph width="100%" height="100%"/>
                                </Grid>
                            </Box>
                        </Grid>
                        <Grid item sx={{m:5}}>
                            <Grid
                            container
                            direction="row"
                            justifyContent="space-around"
                            alignItems="center"
                            >
                                {

                                    location.state.catalog.map((video,idx)=>{
                                        return(
                                            <Grid item key={idx}>
                                                <Links href={'/app/'+video.video_id+'/'+video.title} underline="hover">
                                                    {video.title}
                                                </Links>
                                            </Grid>
                                        );
                                    })
                                }
                            </Grid>
                        
                        </Grid>
                    </Grid>
                </Container>  
            </Grid>
            <Grid item sx={{backgroundColor:"rgb(237,237,237)", mt:5, p:5}}>
                <Container maxWidth="xl" sx={{}}>
                    <Grid
                    container
                    direction="column"
                    justifyContent="center"
                    alignItems="stretch"
                    id="CONFRONTO SLIDE"
                    >
                        <Grid item>
                            <Grid
                            container
                            direction="column"
                            justifyContent="center"
                            alignItems="center"
                            >
                                <Grid item>
                                <Typography variant="h4" gutterBottom sx={{mb:0,pb:0}}>
                                    Confronto presenza slide all'interno del video
                                </Typography>
                                <Box
                                sx={{
                                    m:0,
                                    p:0,
                                    width: '100px',
                                    height: '4px',
                                    backgroundColor: "rgb(223,216,242)",
                                }}
                                />
                                </Grid>
                            </Grid>
                        </Grid>
                        <Grid item>
                            <Grid
                            container
                            direction="row"
                            justifyContent="space-between"
                            alignItems="center"
                            id="BOTTONI"
                            sx={{pt:5}}
                            >
                                <Grid item>
                                    <Typography variant="caption" display="block" gutterBottom>
                                        Legenda
                                    </Typography>
                                </Grid>
                                <Grid item>
                                    <Grid
                                    container
                                    direction="row"
                                    justifyContent="flex-end"
                                    alignItems="center"
                                    spacing={2}
                                    >
                                        <Grid item>
                                            <Typography variant="caption" display="block" gutterBottom>
                                                Riepilogo
                                            </Typography>
                                        </Grid>
                                        <Grid item>
                                            <Typography variant="caption" display="block" gutterBottom>
                                                Definizione
                                            </Typography>
                                        </Grid>
                                        <Grid item>
                                            <Typography variant="caption" display="block" gutterBottom>
                                                Approfondimento
                                            </Typography>
                                        </Grid>
                                        <Grid item>
                                            <Typography variant="caption" display="block" gutterBottom>
                                                Video Intero
                                            </Typography>
                                        </Grid>
                                    </Grid>
                                </Grid>
                            </Grid>
                            
                        </Grid>
                        <Grid item>
                            <Box
                            sx={{
                                width: '100%',
                                backgroundColor: 'white',
                                borderRadius: '20px',
                                height:"500px"
                            }}
                            >
                            {/*INSERT GRAPH HERE */}
                            </Box>
                        </Grid>
                        <Grid item sx={{m:5}}>
                            <Grid
                            container
                            direction="row"
                            justifyContent="space-around"
                            alignItems="center"
                            >
                                {

                                    location.state.catalog.map((video,idx)=>{
                                        return(
                                            <Grid item key={idx}>
                                                <Links href={'/app/'+video.video_id+'/'+video.title} underline="hover">
                                                    {video.title}
                                                </Links>
                                            </Grid>
                                        );
                                    })
                                }
                            </Grid>
                        
                        </Grid>
                    </Grid>
                </Container>  
            </Grid>

            

        </Grid>
        <Grid
        container
        direction="column"
        justifyContent="center"
        alignItems="center"
        sx={{backgroundColor:"#9BDDC1", m:0, p:5}}
        >
            <Grid item>
                <Typography variant="overline" display="block" gutterBottom sx={{color:"white"}}>
                   Congratulation, you've made it to the footer :&#41;
                </Typography>
            </Grid>
        </Grid>
    
    </>);
}

