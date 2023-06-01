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
import pattern from 'patternomaly';
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
import FlowChart from './FlowChart.js'
import ReactFlow, { ReactFlowProvider, useReactFlow } from 'reactflow';
import { ContextComparison } from './ContextComparison';
import IconButton from '@mui/material/IconButton';
import TuneRoundedIcon from '@mui/icons-material/TuneRounded';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Avatar from '@mui/material/Avatar';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import Tooltip from '@mui/material/Tooltip';
import PersonAdd from '@mui/icons-material/PersonAdd';
import Settings from '@mui/icons-material/Settings';
import EastIcon from '@mui/icons-material/East';
import Logout from '@mui/icons-material/Logout';
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
import Barro2 from './BarroGraph2.js';
import { styled } from '@mui/material/styles';


function DP(color = 'black') {
    // create a 10x10 px canvas for the pattern's base shape
    let shape = document.createElement('canvas')
    shape.width = 10
    shape.height = 10
    // get the context for drawing
    let c = shape.getContext('2d')
    c.lineWidth = 1;
    // draw 1st line of the shape 
    c.strokeStyle = color
    c.beginPath()
    c.moveTo(2, 0)
    c.lineTo(10, 8)
    c.stroke()
    // draw 2nd line of the shape 
    c.beginPath()
    c.moveTo(0, 8)
    c.lineTo(2, 10)
    c.stroke()
    // create the pattern from the shape
    return c.createPattern(shape, 'repeat')
  }
  

  

export default function Result(){
  
    const history = useHistory();
    let location = useLocation();
    function SendData(value){
        console.log("historypush: ",value);
        history.push({
            pathname: '/comparisonSearch',
            state: { data: value },
        });
    }
    const colorPick=[
        "#FF4545",
        "#3E7FFF",
        "#CE3FFF",
        "#71D89A"
    ]
    //for first graph
    const [graphcontrol1, setGraphControl1] = useState("one");
    const handleChange1 = (event, newValue) => {
        setGraphControl1(newValue);
      };

    //for second graph
    const [graphcontrol2, setGraphControl2] = useState("one");
    const handleChange2 = (event, newValue) => {
        setGraphControl2(newValue);
      };

    //for third graph
    const [graphcontrol3, setGraphControl3] = useState("one");
    const handleChange3 = (event, newValue) => {
        setGraphControl3(newValue);
      };

    const context = useContext(TokenContext);
    const nameSurname  = context.nameSurname;
    //get from the previous page the data of the video selected for comparison
    
    
    useEffect(() => {
        if(location.state != undefined)
        console.log("data from previous search comparison: ", location.state.concept," ",location.state.catalog," ",location.state.catalogExtra);
      }, [location]);


    //for legenda1
    const ExpandMore1 = styled((props) => {
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
    const [expanded1, setExpanded1] = useState(false);
    const handleExpandClick1 = () => {
        setExpanded1(!expanded1);
    };
    const [anchorEl1, setAnchorEl1] = useState(null);
    const open1 = Boolean(anchorEl1);
    const handleClick1 = (event) => {
        setAnchorEl1(event.currentTarget);
        handleExpandClick1();
    };
    const handleClose1 = () => {
        setAnchorEl1(null);
    };


    //for legenda2
    const ExpandMore2 = styled((props) => {
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
    const [expanded2, setExpanded2] = useState(false);
    const handleExpandClick2 = () => {
        setExpanded2(!expanded2);
    };
    const [anchorEl2, setAnchorEl2] = useState(null);
    const open2 = Boolean(anchorEl2);
    const handleClick2 = (event) => {
        setAnchorEl2(event.currentTarget);
        handleExpandClick2();
    };
    const handleClose2 = () => {
        setAnchorEl2(null);
    };

    //for legenda3
    const ExpandMore3 = styled((props) => {
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
    const [expanded3, setExpanded3] = useState(false);
    const handleExpandClick3 = () => {
        setExpanded3(!expanded3);
    };
    const [anchorEl3, setAnchorEl3] = useState(null);
    const open3 = Boolean(anchorEl3);
    const handleClick3 = (event) => {
        setAnchorEl3(event.currentTarget);
        handleExpandClick3();
    };
    const handleClose3= () => {
        setAnchorEl3(null);
    };



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
                options={location.state.listConcepts}
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
                onChange={(event, value) => {
                    SendData(value);
                  }}
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
                                    <Box
                                        sx={{
                                            backgroundColor:"#8c91ff",
                                            width:"20px",
                                            height:"20px",
                                            borderRadius:"50%",
                                            justifyContent:"center",
                                            alignItems:"center",
                                            p:0.3,
                                            m:1
                                        }}>
                                        <Typography variant="caption" display="block" gutterBottom sx={{color:"white",pt:0.2,pl:0.2}}>
                                            <b>VS</b>
                                        </Typography>

                                    </Box>
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
                    Comparison results
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
                                <Typography variant="h4" gutterBottom sx={{mb:0,pb:0,pt:10}}>
                                    <b>Duration</b>
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
                                    <Chip 
                                        sx={{width:'auto',
                                            margin:'5px',
                                            backgroundColor:"rgb(0,0,0,0)"}}
                                        
                                        avatar={<ExpandMore1
                                            expand={expanded1}
                                    
                                            aria-expanded={expanded1}
                                            aria-label="show more"
                                            >
                                                <ExpandMoreIcon />
                                            </ExpandMore1>}
                                        label={<Typography variant="caption" display="block" gutterBottom sx={{mt:1}}>
                                        Key
                                    </Typography>} 
                                        onClick={handleClick1}
                                       
                                    />
                                    
                                </Grid>
                                                    <Menu
                                                    anchorEl={anchorEl1}
                                                    id="account-menu"
                                                    open={open1}
                                                    onClose={handleClose1}
                                                    onClick={handleClose1}
                                                    PaperProps={{
                                                    elevation: 0,
                                                    sx: {
                                                        overflow: 'visible',
                                                        filter: 'drop-shadow(0px 2px 8px rgba(0,0,0,0.32))',
                                                        mt: 1.5,
                                                        '& .MuiAvatar-root': {
                                                        width: 32,
                                                        height: 32,
                                                        ml: -0.5,
                                                        mr: 1,
                                                        },
                                                        '&:before': {
                                                        content: '""',
                                                        display: 'block',
                                                        position: 'absolute',
                                                        top: 0,
                                                        right: 14,
                                                        width: 10,
                                                        height: 10,
                                                        bgcolor: 'background.paper',
                                                        transform: 'translateY(-50%) rotate(45deg)',
                                                        zIndex: 0,
                                                        },
                                                    },
                                                    }}
                                                    transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                                                    anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
                                                    >
                                                        {
                                                            graphcontrol1=="one"?
                                                            <>
                                                                <MenuItem>
                                                                    <Typography variant="caption"  gutterBottom>
                                                                        <b>Overview:</b>
                                                                    </Typography>
                                                                </MenuItem>
                                                                <MenuItem sx={{mb:0, pb:0}}>
                                                                    <Box sx={{
                                                                        width:"15px",
                                                                        height:"15px",
                                                                        backgroundColor:"#FF4545",
                                                            
                                                                    }}/>
                                                                    <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                        Video 1
                                                                    </Typography>
                                                                </MenuItem>
                                                                <MenuItem sx={{mt:0, mb:0, pt:0, pb:0}}>
                                                                    <Box sx={{
                                                                        width:"15px",
                                                                        height:"15px",
                                                                        backgroundColor:"#3E7FFF"
                                                                    }}/>
                                                                    <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                        Video 2
                                                                    </Typography>
                                                                </MenuItem>
                                                                <MenuItem sx={{mt:0, mb:0, pt:0, pb:0}}>
                                                                    <Box sx={{
                                                                        width:"15px",
                                                                        height:"15px",
                                                                        backgroundColor:"#CE3FFF"
                                                                    }}/>
                                                                    <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                        Video 3
                                                                    </Typography>
                                                                </MenuItem>
                                                                <MenuItem sx={{pt:0, pb:0}}>
                                                                    <Box sx={{
                                                                        width:"15px",
                                                                        height:"15px",
                                                                        backgroundColor:"#71D89A"
                                                                    }}/>
                                                                    <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                        Video 4
                                                                    </Typography>
                                                                </MenuItem>
                                                                <MenuItem sx={{mb:0, pb:0, mt:1}}>
                                                                    <Box sx={{
                                                                        width:"15px",
                                                                        height:"15px",
                                                                        backgroundColor:"white",
                                                                        border: '1px solid gray',
                                                                    }}/>
                                                                    <Typography variant ="caption" gutterBottom sx={{mt:1, pl:1}}>
                                                                        Whole video
                                                                    </Typography>
                                                                </MenuItem>
                                                                <MenuItem sx={{mt:0, mb:0, pt:0, pb:0}}>
                                                                    <Box sx={{
                                                                        width:"15px",
                                                                        height:"15px",
                                                                        backgroundColor:"grey",
                                                                        opacity:"0.8",
                                                                        background:"repeating-linear-gradient( 135deg, grey, grey 3px, white 2px, white 5px )",
                                                                        border: '1px solid gray',
                                                                    }}/>
                                                                    <Typography variant ="caption" gutterBottom sx={{mt:1, pl:1}}>
                                                                        In depth
                                                                    </Typography>
                                                                </MenuItem>
                                                                <MenuItem sx={{pt:0, mt:0}}>
                                                                    <Box sx={{
                                                                        width:"15px",
                                                                        height:"15px",
                                                                        backgroundColor:"grey",
                                                                        border: '1px solid gray',
                                                                    }}/>
                                                                    <Typography variant ="caption" gutterBottom sx={{mt:1, pl:1}}>
                                                                        Definition
                                                                    </Typography>
                                                                </MenuItem>
                                                            </>
                                                            :
                                                            graphcontrol1=="two"?
                                                                    <>
                                                                        <MenuItem>
                                                                        <Typography variant="caption"  gutterBottom>
                                                                            <b>Definition:</b>
                                                                        </Typography>
                                                                        </MenuItem>
                                                                        <MenuItem sx={{mb:0, pb:0}}>
                                                                            <Box sx={{
                                                                                width:"15px",
                                                                                height:"15px",
                                                                                backgroundColor:"#FF4545",
                                                                    
                                                                            }}/>
                                                                            <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                                Video 1
                                                                            </Typography>
                                                                        </MenuItem>
                                                                        <MenuItem sx={{mt:0, mb:0, pt:0, pb:0}}>
                                                                            <Box sx={{
                                                                                width:"15px",
                                                                                height:"15px",
                                                                                backgroundColor:"#3E7FFF"
                                                                            }}/>
                                                                            <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                                Video 2
                                                                            </Typography>
                                                                        </MenuItem>
                                                                        <MenuItem sx={{mt:0, mb:0, pt:0, pb:0}}>
                                                                            <Box sx={{
                                                                                width:"15px",
                                                                                height:"15px",
                                                                                backgroundColor:"#CE3FFF"
                                                                            }}/>
                                                                            <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                                Video 3
                                                                            </Typography>
                                                                        </MenuItem>
                                                                        <MenuItem sx={{pt:0, pb:0}}>
                                                                            <Box sx={{
                                                                                width:"15px",
                                                                                height:"15px",
                                                                                backgroundColor:"#71D89A"
                                                                            }}/>
                                                                            <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                                Video 4
                                                                            </Typography>
                                                                        </MenuItem>
                                                                    </>
                                                                    :
                                                                    graphcontrol1=="three"?
                                                                            <>
                                                                                <MenuItem>
                                                                                    <Typography variant="caption"  gutterBottom>
                                                                                        <b>In depth:</b>
                                                                                    </Typography>
                                                                                </MenuItem>
                                                                                <MenuItem sx={{mb:0, pb:0}}>
                                                                                    <Box sx={{
                                                                                        width:"15px",
                                                                                        height:"15px",
                                                                                        width:"15px",
                                                                                        height:"15px",
                                                                                        backgroundColor:"#e5e5f7","opacity":"0.8",
                                                                                        background:"repeating-linear-gradient( 135deg, #FF4545, #FF4545 3px, #e5e5f7 2px, #e5e5f7 5px )",
                                                                                        border:1,
                                                                                        borderColor:"grey"
                                                                            
                                                                                    }}/>
                                                                                    <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                                        Video 1
                                                                                    </Typography>
                                                                                </MenuItem>
                                                                                <MenuItem sx={{mt:0, mb:0, pt:0, pb:0}}>
                                                                                    <Box sx={{
                                                                                        width:"15px",
                                                                                        height:"15px",
                                                                                        backgroundColor:"#e5e5f7","opacity":"0.8",
                                                                                        background:"repeating-linear-gradient( 135deg, #3E7FFF, #3E7FFF 3px, #e5e5f7 2px, #e5e5f7 5px )",
                                                                                        border:1,
                                                                                        borderColor:"grey"
                                                                                    }}/>
                                                                                    <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                                        Video 2
                                                                                    </Typography>
                                                                                </MenuItem>
                                                                                <MenuItem sx={{mt:0, mb:0, pt:0, pb:0}}>
                                                                                    <Box sx={{
                                                                                        width:"15px",
                                                                                        height:"15px",
                                                                                        backgroundColor:"#e5e5f7","opacity":"0.8",
                                                                                        background:"repeating-linear-gradient( 135deg, #E3B8F2, #E3B8F2 3px, #e5e5f7 2px, #e5e5f7 5px )",
                                                                                        border:1,
                                                                                        borderColor:"grey"
                                                                                    }}/>
                                                                                    <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                                        Video 3
                                                                                    </Typography>
                                                                                </MenuItem>
                                                                                <MenuItem sx={{pt:0, pb:0}}>
                                                                                    <Box sx={{
                                                                                        width:"15px",
                                                                                        height:"15px",
                                                                                        backgroundColor:"#e5e5f7","opacity":"0.8",
                                                                                        background:"repeating-linear-gradient( 135deg, #71D89A, #71D89A 3px, #e5e5f7 2px, #e5e5f7 5px )",
                                                                                        border:1,
                                                                                        borderColor:"grey"
                                                                                    }}/>
                                                                                    <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                                        Video 4
                                                                                    </Typography>
                                                                                </MenuItem>
                                                                            
                                                                            </>
                                                                            :
                                                                            graphcontrol1=="four"?
                                                                                <>
                                                                                    <MenuItem>
                                                                                        <Typography variant="caption"  gutterBottom>
                                                                                            <b>Whole video:</b>
                                                                                        </Typography>
                                                                                    </MenuItem>
                                                                                    <MenuItem sx={{mb:0, pb:0}}>
                                                                                        <Box sx={{
                                                                                            width:"15px",
                                                                                            height:"15px",
                                                                                            backgroundColor:"white",
                                                                                            border:2,
                                                                                            borderColor:"#FF4545"
                                                                                
                                                                                        }}/>
                                                                                        <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                                            Video 1
                                                                                        </Typography>
                                                                                    </MenuItem>
                                                                                    <MenuItem sx={{mt:0, mb:0, pt:0, pb:0}}>
                                                                                        <Box sx={{
                                                                                            width:"15px",
                                                                                            height:"15px",
                                                                                            backgroundColor:"white",
                                                                                            border:2,
                                                                                            borderColor:"#3E7FFF"
                                                                                        }}/>
                                                                                        <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                                            Video 2
                                                                                        </Typography>
                                                                                    </MenuItem>
                                                                                    <MenuItem sx={{mt:0, mb:0, pt:0, pb:0}}>
                                                                                        <Box sx={{
                                                                                            width:"15px",
                                                                                            height:"15px",
                                                                                            backgroundColor:"white",
                                                                                            border:2,
                                                                                            borderColor:"#CE3FFF"
                                                                                        }}/>
                                                                                        <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                                            Video 3
                                                                                        </Typography>
                                                                                    </MenuItem>
                                                                                    <MenuItem sx={{pt:0, pb:0}}>
                                                                                        <Box sx={{
                                                                                            width:"15px",
                                                                                            height:"15px",
                                                                                            backgroundColor:"white",
                                                                                            border:2,
                                                                                            borderColor:"#71D89A"
                                                                                        }}/>
                                                                                        <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                                            Video 4
                                                                                        </Typography>
                                                                                    </MenuItem>
                                                                                </>
                                                                                :
                                                                                <>something went wrong..</>
                                                        }
                                                    
                                                    
                                                </Menu>
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
                                        value={graphcontrol1}
                                        onChange={handleChange1}
                                        textColor="secondary"
                                        indicatorColor="secondary"
                                        aria-label="secondary tabs example"
                                       
                                    >
                                        
                                        <Tab value="two" label={<Typography variant="caption" display="block" gutterBottom>
                                            Definition
                                        </Typography>} />
                                        <Tab value="three" label={<Typography variant="caption" display="block" gutterBottom>
                                            in depth
                                        </Typography>}/>
                                        <Tab value="four" label={<Typography variant="caption" display="block" gutterBottom>
                                            Whole video
                                        </Typography>}/>
                                        <Tab value="one" label={<Typography variant="caption" display="block" gutterBottom>
                                            Overview
                                        </Typography>} />
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
                                borderRadius: '20px',
                                height:"500px"
                            }}
                            >
                            {/*INSERT GRAPH HERE */}
                            
                                <Barro catalog={location.state.catalog} catalogExtra={location.state.catalogExtra} graphcontrol ={graphcontrol1}/>    
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
                                                <Links href={'/app/'+video.video_id+'/'+video.title} underline="hover" style={{marginLeft:0,paddingLeft:5, color:"#3b3b3b"}}>
                                                <Box
                                                    sx={{
                                                        width:"auto",
                                                        height:"auto",
                                                        border:1,
                                                        borderColor:"grey.300",
                                                        borderRadius:"16px",
                                                        backgroundColor:"white"
                                                    }}>
                                                    <Stack direction="row" spacing={0.5} sx={{ml:1, mr:1, mt:0.5, mb:0.5}}>
                                        
                                                        <Box
                                                        sx={{
                                                            backgroundColor:colorPick[idx],
                                                            width:"8px",
                                                            height:"15px",
                                                            mr:0,
                                                            pr:0,
                                                            mt:0.4
                                                        }}/>
                                                
                                            
                                                        
                                                            <Typography variant="caption" gutterBottom sx={{pt:0.4}}>
                                                                {video.title}
                                                            </Typography>
                                                         
                                                        <EastIcon sx={{pt:0.4, width:"15px", height:'15px'}}/> 
                                                
                                                    </Stack>
                                                </Box>
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
                                <Typography variant="h4" gutterBottom sx={{mb:0,pb:0, pt:10}}>
                                    <b>What you must already know, what you are going to learn</b>
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
                                    <Chip 
                                        sx={{width:'auto',
                                            margin:'5px',
                                            backgroundColor:"rgb(0,0,0,0)"}}
                                        
                                        avatar={<ExpandMore2
                                            expand={expanded2}
                                    
                                            aria-expanded={expanded2}
                                            aria-label="show more"
                                            >
                                                <ExpandMoreIcon />
                                            </ExpandMore2>}
                                        label={<Typography variant="caption" display="block" gutterBottom sx={{mt:1}}>
                                        Key
                                    </Typography>} 
                                        onClick={handleClick2}
                                       
                                    />
                                    
                                </Grid>
                                                    <Menu
                                                    anchorEl={anchorEl2}
                                                    id="account-menu"
                                                    open={open2}
                                                    onClose={handleClose2}
                                                    onClick={handleClose2}
                                                    PaperProps={{
                                                    elevation: 0,
                                                    sx: {
                                                        overflow: 'visible',
                                                        filter: 'drop-shadow(0px 2px 8px rgba(0,0,0,0.32))',
                                                        mt: 1.5,
                                                        '& .MuiAvatar-root': {
                                                        width: 32,
                                                        height: 32,
                                                        ml: -0.5,
                                                        mr: 1,
                                                        },
                                                        '&:before': {
                                                        content: '""',
                                                        display: 'block',
                                                        position: 'absolute',
                                                        top: 0,
                                                        right: 14,
                                                        width: 10,
                                                        height: 10,
                                                        bgcolor: 'background.paper',
                                                        transform: 'translateY(-50%) rotate(45deg)',
                                                        zIndex: 0,
                                                        },
                                                    },
                                                    }}
                                                    transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                                                    anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
                                                >
                                                    {
                                                        graphcontrol2=="one"?
                                                        <>
                                                            <MenuItem>
                                                                <Typography variant="caption"  gutterBottom>
                                                                    <b>Overview:</b>
                                                                </Typography>
                                                            </MenuItem>
                                                            <MenuItem sx={{mb:0, pb:0}}>
                                                                <Box sx={{
                                                                    width:"15px",
                                                                    height:"15px",
                                                                    backgroundColor:"#FF4545",
                                                        
                                                                }}/>
                                                                <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                    Video 1
                                                                </Typography>
                                                            </MenuItem>
                                                            <MenuItem sx={{mt:0, mb:0, pt:0, pb:0}}>
                                                                <Box sx={{
                                                                    width:"15px",
                                                                    height:"15px",
                                                                    backgroundColor:"#3E7FFF"
                                                                }}/>
                                                                <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                    Video 2
                                                                </Typography>
                                                            </MenuItem>
                                                            <MenuItem sx={{mt:0, mb:0, pt:0, pb:0}}>
                                                                <Box sx={{
                                                                    width:"15px",
                                                                    height:"15px",
                                                                    backgroundColor:"#CE3FFF"
                                                                }}/>
                                                                <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                    Video 3
                                                                </Typography>
                                                            </MenuItem>
                                                            <MenuItem sx={{pt:0, pb:0}}>
                                                                <Box sx={{
                                                                    width:"15px",
                                                                    height:"15px",
                                                                    backgroundColor:"#71D89A"
                                                                }}/>
                                                                <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                    Video 4
                                                                </Typography>
                                                            </MenuItem>
                                                            <MenuItem sx={{mb:0, pb:0, mt:1}}>
                                                                <Box sx={{
                                                                    width:"15px",
                                                                    height:"15px",
                                                                    backgroundColor:"white",
                                                                    border: 2,
                                                                    borderColor:"black"
                                                                }}/>
                                                                <Typography variant ="caption" gutterBottom sx={{mt:1, pl:1}}>
                                                                    What should you already know?
                                                                </Typography>
                                                            </MenuItem>
                                                            <MenuItem sx={{mt:0, mb:0, pt:0, pb:0}}>
                                                                <Box sx={{
                                                                    width:"15px",
                                                                    height:"15px",
                                                                    backgroundColor:"grey",
                                                                    opacity:"0.5",
                                                                    background:"white",
                                                                    border: 2,
                                                                    borderColor:"grey"
                                                                }}/>
                                                                <Typography variant ="caption" gutterBottom sx={{mt:1, pl:1}}>
                                                                    What will you learn?
                                                                </Typography>
                                                            </MenuItem>
                                                            <MenuItem sx={{pt:0, mt:0}}>
                                                                <Box sx={{
                                                                    width:"15px",
                                                                    height:"15px",
                                                                    backgroundColor:"grey",
                                                                    border: '2px solid gray',
                                                                }}/>
                                                                <Typography variant ="caption" gutterBottom sx={{mt:1, pl:1}}>
                                                                    Concept
                                                                </Typography>
                                                            </MenuItem>
                                                            <MenuItem sx={{pb:0,mb:0}}>
                                                                <EastIcon sx={{stroke: "black", strokeWidth: 2}}/>
                                                                <Typography variant="caption" gutterBottom sx={{mt:1, pl:1}}>
                                                                    <b>Strong link</b>
                                                                </Typography>
                                                            </MenuItem>
                                                            <MenuItem sx={{pt:0,mt:0}}>
                                                                <EastIcon/>
                                                                <Typography variant="caption" gutterBottom sx={{mt:1, pl:1}}>
                                                                    Weak link
                                                                </Typography>
                                                            </MenuItem>
                                                        </>
                                                        :
                                                        graphcontrol2=="two"?
                                                                <>
                                                                    <MenuItem>
                                                                        <Typography variant="caption"  gutterBottom>
                                                                            <b>What should you already know?</b>
                                                                        </Typography>
                                                                    </MenuItem>
                                                                    <MenuItem sx={{mb:0, pb:0}}>
                                                                        <Box sx={{
                                                                            width:"15px",
                                                                            height:"15px",
                                                                            backgroundColor:"white",
                                                                            border:2,
                                                                            borderColor:"#FF4545",
                                                                
                                                                        }}/>
                                                                        <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                            Video 1
                                                                        </Typography>
                                                                    </MenuItem>
                                                                    <MenuItem sx={{mt:0, mb:0, pt:0, pb:0}}>
                                                                        <Box sx={{
                                                                            width:"15px",
                                                                            height:"15px",
                                                                            backgroundColor:"white",
                                                                            border:2,
                                                                            borderColor:"#3E7FFF"
                                                                        }}/>
                                                                        <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                            Video 2
                                                                        </Typography>
                                                                    </MenuItem>
                                                                    <MenuItem sx={{mt:0, mb:0, pt:0, pb:0}}>
                                                                        <Box sx={{
                                                                            width:"15px",
                                                                            height:"15px",
                                                                            backgroundColor:"white",
                                                                            border:2,
                                                                            borderColor:"#CE3FFF"
                                                                        }}/>
                                                                        <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                            Video 3
                                                                        </Typography>
                                                                    </MenuItem>
                                                                    <MenuItem sx={{pt:0, pb:0}}>
                                                                        <Box sx={{
                                                                            width:"15px",
                                                                            height:"15px",
                                                                            backgroundColor:"white",
                                                                            border:2,
                                                                            borderColor:"#71D89A"
                                                                        }}/>
                                                                        <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                            Video 4
                                                                        </Typography>
                                                                    </MenuItem>
                                                                    <MenuItem sx={{pb:0,mb:0}}>
                                                                        <EastIcon sx={{stroke: "black", strokeWidth: 2}}/>
                                                                        <Typography variant="caption" gutterBottom sx={{mt:1, pl:1}}>
                                                                            <b>Strong link</b>
                                                                        </Typography>
                                                                    </MenuItem>
                                                                    <MenuItem sx={{pt:0,mt:0}}>
                                                                        <EastIcon/>
                                                                        <Typography variant="caption" gutterBottom sx={{mt:1, pl:1}}>
                                                                            Weak link
                                                                        </Typography>
                                                                    </MenuItem>
                                                                </>
                                                                :
                                                                graphcontrol2=="three"?
                                                                        <>
                                                                            <MenuItem>
                                                                                <Typography variant="caption"  gutterBottom>
                                                                                    <b>What will you learn?</b>
                                                                                </Typography>
                                                                            </MenuItem>
                                                                            <MenuItem sx={{mb:0, pb:0}}>
                                                                                <Box sx={{
                                                                                    width:"15px",
                                                                                    height:"15px",
                                                                                    backgroundColor:"white",
                                                                                    border:2,
                                                                                    borderColor:"#ff7878",
                                                                                
                                                                        
                                                                                }}/>
                                                                                <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                                    Video 1
                                                                                </Typography>
                                                                            </MenuItem>
                                                                            <MenuItem sx={{mt:0, mb:0, pt:0, pb:0}}>
                                                                                <Box sx={{
                                                                                    width:"15px",
                                                                                    height:"15px",
                                                                                    backgroundColor:"white",
                                                                                    border:2,
                                                                                    borderColor:"#9dbdfc",
                                                                                
                                                                                }}/>
                                                                                <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                                    Video 2
                                                                                </Typography>
                                                                            </MenuItem>
                                                                            <MenuItem sx={{mt:0, mb:0, pt:0, pb:0}}>
                                                                                <Box sx={{
                                                                                    width:"15px",
                                                                                    height:"15px",
                                                                                    backgroundColor:"white",
                                                                                    border:2,
                                                                                    borderColor:"#e08dfc",
                                                                             
                                                                                }}/>
                                                                                <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                                    Video 3
                                                                                </Typography>
                                                                            </MenuItem>
                                                                            <MenuItem sx={{pt:0, pb:0}}>
                                                                                <Box sx={{
                                                                                    width:"15px",
                                                                                    height:"15px",
                                                                                    backgroundColor:"white",
                                                                                    border:2,
                                                                                    borderColor:"#a4f5c4",
                                                                                    
                                                                                }}/>
                                                                                <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                                    Video 4
                                                                                </Typography>
                                                                            </MenuItem>
                                                                            <MenuItem sx={{pb:0,mb:0}}>
                                                                                <EastIcon sx={{stroke: "black", strokeWidth: 2}}/>
                                                                                <Typography variant="caption" gutterBottom sx={{mt:1, pl:1}}>
                                                                                    <b>Strong link</b>
                                                                                </Typography>
                                                                            </MenuItem>
                                                                            <MenuItem sx={{pt:0,mt:0}}>
                                                                                <EastIcon/>
                                                                                <Typography variant="caption" gutterBottom sx={{mt:1, pl:1}}>
                                                                                    Weak link
                                                                                </Typography>
                                                                            </MenuItem>
                                                                        
                                                                        </>
                                                                        :
                                                                        <>something went wrong..</>
                                                    }
                                                    
                                                    
                                                </Menu>
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
                                        onChange={handleChange2}
                                        textColor="secondary"
                                        indicatorColor="secondary"
                                        aria-label="secondary tabs example"
                                       
                                    >
                                       
                                        <Tab value="two" label={<Typography variant="caption" display="block" gutterBottom>
                                            What should you already know?
                                        </Typography>} />
                                        <Tab value="three" label={<Typography variant="caption" display="block" gutterBottom>
                                            What will you learn?
                                        </Typography>}/>
                                        <Tab value="one" label={<Typography variant="caption" display="block" gutterBottom>
                                            Overview
                                        </Typography>} />
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
                                   
                                            
                                            return(<>
                                                <Grid item xs>
                                                <ReactFlowProvider>
                                                    <FlowChart concept={location.state.concept} conceptExtra={catExtra} idx={idx} graphcontrol={graphcontrol2}/>
                                                </ReactFlowProvider>
                                                </Grid>
                                                <Divider orientation="vertical" variant="middle" flexItem  />
                                            </>
                                            );
                                        })
                                       
                                    }
                         
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
                                                <Links href={'/app/'+video.video_id+'/'+video.title} underline="hover" style={{marginLeft:0,paddingLeft:5, color:"#3b3b3b"}}>
                                                <Box
                                                    sx={{
                                                        width:"auto",
                                                        height:"auto",
                                                        border:1,
                                                        borderColor:"grey.300",
                                                        borderRadius:"16px",
                                                        backgroundColor:"white"
                                                    }}>
                                                    <Stack direction="row" spacing={0.5} sx={{ml:1, mr:1, mt:0.5, mb:0.5}}>
                                        
                                                        <Box
                                                        sx={{
                                                            backgroundColor:colorPick[idx],
                                                            width:"8px",
                                                            height:"15px",
                                                            mr:0,
                                                            pr:0,
                                                            mt:0.4
                                                        }}/>
                                                
                                            
                                                        
                                                            <Typography variant="caption" gutterBottom sx={{pt:0.4}}>
                                                                {video.title}
                                                            </Typography>
                                                         
                                                        <EastIcon sx={{pt:0.4, width:"15px", height:'15px'}}/> 
                                                
                                                    </Stack>
                                                </Box>
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
                                <Typography variant="h4" gutterBottom sx={{mb:0,pb:0, pt:10}}>
                                    <b>Slide presence</b>
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
                                    <Chip 
                                        sx={{width:'auto',
                                            margin:'5px',
                                            backgroundColor:"rgb(0,0,0,0)"}}
                                        
                                        avatar={<ExpandMore3
                                            expand={expanded3}
                                    
                                            aria-expanded={expanded3}
                                            aria-label="show more"
                                            >
                                                <ExpandMoreIcon />
                                            </ExpandMore3>}
                                        label={<Typography variant="caption" display="block" gutterBottom sx={{mt:1}}>
                                        Key
                                    </Typography>} 
                                        onClick={handleClick3}
                                       
                                    />
                                    
                                </Grid>
                                                    <Menu
                                                    anchorEl={anchorEl3}
                                                    id="account-menu"
                                                    open={open3}
                                                    onClose={handleClose3}
                                                    onClick={handleClose3}
                                                    PaperProps={{
                                                    elevation: 0,
                                                    sx: {
                                                        overflow: 'visible',
                                                        filter: 'drop-shadow(0px 2px 8px rgba(0,0,0,0.32))',
                                                        mt: 1.5,
                                                        '& .MuiAvatar-root': {
                                                        width: 32,
                                                        height: 32,
                                                        ml: -0.5,
                                                        mr: 1,
                                                        },
                                                        '&:before': {
                                                        content: '""',
                                                        display: 'block',
                                                        position: 'absolute',
                                                        top: 0,
                                                        right: 14,
                                                        width: 10,
                                                        height: 10,
                                                        bgcolor: 'background.paper',
                                                        transform: 'translateY(-50%) rotate(45deg)',
                                                        zIndex: 0,
                                                        },
                                                    },
                                                    }}
                                                    transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                                                    anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
                                                >
                                                    {
                                                        graphcontrol3=="one"?
                                                        <>
                                                            <MenuItem>
                                                                <Typography variant="caption"  gutterBottom>
                                                                    <b>Overview:</b>
                                                                </Typography>
                                                            </MenuItem>
                                                            <MenuItem sx={{mb:0, pb:0}}>
                                                                <Box sx={{
                                                                    width:"15px",
                                                                    height:"15px",
                                                                    backgroundColor:"#FF4545",
                                                        
                                                                }}/>
                                                                <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                    Video 1
                                                                </Typography>
                                                            </MenuItem>
                                                            <MenuItem sx={{mt:0, mb:0, pt:0, pb:0}}>
                                                                <Box sx={{
                                                                    width:"15px",
                                                                    height:"15px",
                                                                    backgroundColor:"#3E7FFF"
                                                                }}/>
                                                                <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                    Video 2
                                                                </Typography>
                                                            </MenuItem>
                                                            <MenuItem sx={{mt:0, mb:0, pt:0, pb:0}}>
                                                                <Box sx={{
                                                                    width:"15px",
                                                                    height:"15px",
                                                                    backgroundColor:"#CE3FFF"
                                                                }}/>
                                                                <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                    Video 3
                                                                </Typography>
                                                            </MenuItem>
                                                            <MenuItem sx={{pt:0, pb:0}}>
                                                                <Box sx={{
                                                                    width:"15px",
                                                                    height:"15px",
                                                                    backgroundColor:"#71D89A"
                                                                }}/>
                                                                <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                    Video 4
                                                                </Typography>
                                                            </MenuItem>
                                                            <MenuItem sx={{mb:0, pb:0, mt:1}}>
                                                                <Box sx={{
                                                                    width:"15px",
                                                                    height:"15px",
                                                                    backgroundColor:"white",
                                                                    border: '1px solid gray',
                                                                }}/>
                                                                <Typography variant ="caption" gutterBottom sx={{mt:1, pl:1}}>
                                                                    Whole video
                                                                </Typography>
                                                            </MenuItem>
                                                        
                                                            <MenuItem sx={{pt:0, mt:0}}>
                                                                <Box sx={{
                                                                    width:"15px",
                                                                    height:"15px",
                                                                    backgroundColor:"grey",
                                                                    border: '1px solid gray',
                                                                }}/>
                                                                <Typography variant ="caption" gutterBottom sx={{mt:1, pl:1}}>
                                                                    Slide
                                                                </Typography>
                                                            </MenuItem>
                                                                
                                                        
                                                        </>
                                                        :
                                                        graphcontrol3=="two"?
                                                                <>
                                                                    <MenuItem>
                                                                        <Typography variant="caption"  gutterBottom>
                                                                            <b>Slide:</b>
                                                                        </Typography>
                                                                    </MenuItem>
                                                                    <MenuItem sx={{mb:0, pb:0}}>
                                                                        <Box sx={{
                                                                            width:"15px",
                                                                            height:"15px",
                                                                            backgroundColor:"#FF4545",
                                                                
                                                                        }}/>
                                                                        <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                            Video 1
                                                                        </Typography>
                                                                    </MenuItem>
                                                                    <MenuItem sx={{mt:0, mb:0, pt:0, pb:0}}>
                                                                        <Box sx={{
                                                                            width:"15px",
                                                                            height:"15px",
                                                                            backgroundColor:"#3E7FFF"
                                                                        }}/>
                                                                        <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                            Video 2
                                                                        </Typography>
                                                                    </MenuItem>
                                                                    <MenuItem sx={{mt:0, mb:0, pt:0, pb:0}}>
                                                                        <Box sx={{
                                                                            width:"15px",
                                                                            height:"15px",
                                                                            backgroundColor:"#CE3FFF"
                                                                        }}/>
                                                                        <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                            Video 3
                                                                        </Typography>
                                                                    </MenuItem>
                                                                    <MenuItem sx={{pt:0, pb:0}}>
                                                                        <Box sx={{
                                                                            width:"15px",
                                                                            height:"15px",
                                                                            backgroundColor:"#71D89A"
                                                                        }}/>
                                                                        <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                            Video 4
                                                                        </Typography>
                                                                    </MenuItem>
                                                                
                                                                
                                                                </>
                                                                :
                                                                graphcontrol3 == "three"?
                                                                        <>
                                                                            <MenuItem>
                                                                                <Typography variant="caption"  gutterBottom>
                                                                                    <b>Whole video:</b>
                                                                                </Typography>
                                                                            </MenuItem>
                                                                            <MenuItem sx={{mb:0, pb:0}}>
                                                                                <Box sx={{
                                                                                    width:"15px",
                                                                                    height:"15px",
                                                                                    backgroundColor:"white",
                                                                                    border:2,
                                                                                    borderColor:"#FF4545",
                                                                        
                                                                                }}/>
                                                                                <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                                    Video 1
                                                                                </Typography>
                                                                            </MenuItem>
                                                                            <MenuItem sx={{mt:0, mb:0, pt:0, pb:0}}>
                                                                                <Box sx={{
                                                                                    width:"15px",
                                                                                    height:"15px",
                                                                                    backgroundColor:"white",
                                                                                    border:2,
                                                                                    borderColor:"#3E7FFF"
                                                                                }}/>
                                                                                <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                                    Video 2
                                                                                </Typography>
                                                                            </MenuItem>
                                                                            <MenuItem sx={{mt:0, mb:0, pt:0, pb:0}}>
                                                                                <Box sx={{
                                                                                    width:"15px",
                                                                                    height:"15px",
                                                                                    backgroundColor:"white",
                                                                                    border:2,
                                                                                    borderColor:"#CE3FFF"
                                                                                }}/>
                                                                                <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                                    Video 3
                                                                                </Typography>
                                                                            </MenuItem>
                                                                            <MenuItem sx={{pt:0, pb:0}}>
                                                                                <Box sx={{
                                                                                    width:"15px",
                                                                                    height:"15px",
                                                                                    backgroundColor:"white",
                                                                                    border:2,
                                                                                    borderColor:"#71D89A"
                                                                                }}/>
                                                                                <Typography variant="caption" gutterBottom sx={{mt:1,pl:1}}>
                                                                                    Video 4
                                                                                </Typography>
                                                                            </MenuItem>
                                                                        </>
                                                                        :
                                                                        <>something went wrong..</>

                                                    }
                                                    
                                                    
                                                    
                                                </Menu>
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
                                        value={graphcontrol3}
                                        onChange={handleChange3}
                                        textColor="secondary"
                                        indicatorColor="secondary"
                                        aria-label="secondary tabs example"
                                       
                                    >
                                        
                                        <Tab value="two" label={<Typography variant="caption" display="block" gutterBottom>
                                            Slide
                                        </Typography>} />
                                        <Tab value="three" label={<Typography variant="caption" display="block" gutterBottom>
                                            Whole video
                                        </Typography>}/>
                                        <Tab value="one" label={<Typography variant="caption" display="block" gutterBottom>
                                            Overview
                                        </Typography>} />
                                
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
                                borderRadius: '20px',
                                height:"500px"
                            }}
                            >
                            {/*INSERT GRAPH HERE */}
                            <Barro2 catalog={location.state.catalog} catalogExtra={location.state.catalogExtra} graphcontrol = {graphcontrol3}/>
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
                                                <Links href={'/app/'+video.video_id+'/'+video.title} underline="hover" style={{marginLeft:0,paddingLeft:5, color:"#3b3b3b"}}>
                                                <Box
                                                    sx={{
                                                        width:"auto",
                                                        height:"auto",
                                                        border:1,
                                                        borderColor:"grey.300",
                                                        borderRadius:"16px",
                                                        backgroundColor:"white"
                                                    }}>
                                                    <Stack direction="row" spacing={0.5} sx={{ml:1, mr:1, mt:0.5, mb:0.5}}>
                                        
                                                        <Box
                                                        sx={{
                                                            backgroundColor:colorPick[idx],
                                                            width:"8px",
                                                            height:"15px",
                                                            mr:0,
                                                            pr:0,
                                                            mt:0.4
                                                        }}/>
                                                
                                            
                                                        
                                                            <Typography variant="caption" gutterBottom sx={{pt:0.4}}>
                                                                {video.title}
                                                            </Typography>
                                                         
                                                        <EastIcon sx={{pt:0.4, width:"15px", height:'15px'}}/> 
                                                
                                                    </Stack>
                                                </Box>
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
                <b>Edurell Platform for enhanced Video-based Learning</b>
                </Typography>
            </Grid>
        </Grid>
        {
            
        }
    
    </>);
}

