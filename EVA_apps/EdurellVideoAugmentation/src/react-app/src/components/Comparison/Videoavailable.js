import * as React from 'react';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import imag from './imgtest/brainicon.PNG'
import {useState} from 'react';
import { useTheme } from '@material-ui/core/styles';
import CancelIcon from '@mui/icons-material/Cancel';
import Paper from '@mui/material/Paper';
import Fade from '@mui/material/Fade';
import Modal from '@mui/material/Modal';
import Backdrop from '@mui/material/Backdrop';
import Grid from '@mui/material/Grid';
import Chip from '@mui/material/Chip';
import Badge from '@mui/material/Badge';
import Stack from '@mui/material/Stack';
import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';
import { styled } from '@mui/material/styles';
import IconButton from '@mui/material/IconButton';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Collapse from '@mui/material/Collapse';
import { useContext } from 'react';
import { ContextComparison } from './ContextComparison';



const ExpandMore = styled((props) => {
    const { expand, ...other } = props;
    return <IconButton {...other} />;
  })(({ theme, expand }) => ({
    transform: !expand ? 'rotate(0deg)' : 'rotate(180deg)',
    marginLeft: 'auto',
    transition: theme.transitions.create('transform', {
      duration: theme.transitions.duration.shortest,
    }),
  }));


export default function Videoavailable() {
    const addvideo = useContext(ContextComparison);
    const [shadow, setshadow] = useState(0);
    const [open, setOpen] = useState(0);
    const [expanded, setExpanded] = useState(false);
    const [add, setAdd] = useState(false);
    const title="Kurzesgast - The power of loveKurzesgast ";
    const handleExpandClick = () => {
      setExpanded(!expanded);
    };
 
    return (
        <>
      <Card elevation={shadow}
            color="primary" 
            sx={{ maxWidth: 250 , border: add?"2px solid #C6EBDC": '0px'}}
            onMouseEnter={()=>setshadow(5)}
            onMouseLeave={()=>setshadow(0)}
            onClick={()=>setOpen(!open)}
            align="left"
            >
     
        <CardMedia
        sx={{   height: 140,
                margin: 2,
                marginBottom:0,
                }}
        image={imag}
        title="green iguana"
      />
        <CardContent disableSpacing >

        <Typography noWrap variant="subtitle2" gutterBottom>
        Kurzesgast - The power of loveKurzesgast 
        </Typography>
        <Stack direction="row" spacing={1}>
        <Chip label="Concepts: 2" size="small" color="primary"/>
        <Chip label="Prerequisites: 2" size="small" color="secondary"/>
        
        </Stack>
        </CardContent>
      </Card>
        {/*start of modal*/}

        <Modal
        aria-labelledby="transition-modal-title"
        aria-describedby="transition-modal-description"
        open={open}
        onClose={()=>setOpen(!open)}
        closeAfterTransition
        slots={{ backdrop: Backdrop }}
        slotProps={{
          backdrop: {
            timeout: 500,
          },
        }}
        sx={{overflow:'scroll'}}
      >
            <Fade in={open}>
          
            <Grid
                container
                spacing={0}
                direction="column"
                alignItems="center"
                justifyContent="center"
               
                >

                <Grid sx={{zIndex: 2000}} item xs={12}>
                <Card 
                color="primary" 
                sx={{ maxWidth:1000,
                        width: 900,
                        margin:5}}
                
                >
        
                    <img src={imag} alt="Girl in a jacket" width="100%" height="auto"/>
                
                    <CardContent disableSpacing sx={{marginBottom:0, paddingBottom:0}}>

                    <Typography  variant="h5" gutterBottom sx={{margin:0, padding:0}}>
                    Kurzesgast - The power of loveKurzesgast 
                    </Typography>
                    
                    </CardContent>
                    <CardContent >
                      
                        <Stack direction="row" spacing={1} >
                        <Chip label="Concepts: 2" size="small" color="primary"/>
                        <Chip label="Prerequisites: 2" size="small" color="secondary"/>
                        
                        </Stack>

                        
                    </CardContent>
                    <Divider/>
                    <CardActions disableSpacing>
                        {
                            add?
                            <Button variant="contained" color="error" onClick={()=>{setAdd(!add);addvideo(imag,title);}}>
                            <b>REMOVE</b>
                            </Button>
                            :
                            <Button variant="contained" color="success" onClick={()=>{setAdd(!add); addvideo(imag,title);}}>
                            <b>ADD</b>
                            </Button>
                        }
                    

                        <ExpandMore
                        expand={expanded}
                        onClick={handleExpandClick}
                        aria-expanded={expanded}
                        aria-label="show more"
                        >
                        <ExpandMoreIcon />
                        </ExpandMore>
                    </CardActions>
                    <Collapse in={expanded} timeout="auto" unmountOnExit>
                        <CardContent>
                        <Divider/>
                        <br/>
                        <Typography>
                            Concepts
                        </Typography>
                        <Stack direction="row" spacing={1} >
                        <Chip label="Rock" size="small" color="primary"/>
                        <Chip label="wifi" size="small" color="primary"/>
                        </Stack>
                        <br/>
                        <br/>
                        <Divider/>
                        <br/>
                        <Typography>
                            Prerequisites
                        </Typography>
                        <Stack direction="row" spacing={1} >
                        <Chip label="il tuo cervello" size="small" color="secondary"/>
                        <Chip label="usa la materia grigia" size="small" color="secondary"/>
                        </Stack>
                        </CardContent>
                    </Collapse>
                </Card>
                </Grid>   
                
                </Grid> 

                
            </Fade>
      </Modal>
    </>
    );
  }


 