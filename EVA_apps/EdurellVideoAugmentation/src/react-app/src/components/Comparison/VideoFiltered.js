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
import CircleIcon from '@mui/icons-material/Circle';
import {TokenContext} from '../account-management/TokenContext';
import {
  Link,
  Redirect,
} from "react-router-dom";
//style={{position:'fixed'}}
export default function VideoFiltered({conceptextra, titleurl,imageurl,idxurl,concepts,creator}){
    const addvideo = useContext(ContextComparison)[0];
    const removevideo = useContext(ContextComparison)[1];
    const [shadow, setshadow] = useState(0);
    const [open, setOpen] = useState(0);
    const [expanded, setExpanded] = useState(false);
    const [add, setAdd] = useState(false);
    const [hoverm, setHoverm] = useState(false);

    //const title="Kurzesgast - The power of loveKurzesgast ";
    const handleExpandClick = () => {
      setExpanded(!expanded);
    };
    console.log("videofitlered ",conceptextra, " ", conceptextra[0])
    let duration=0

    if(conceptextra[0]!=undefined&& conceptextra[0].concept_starttime.length>0){
    
       
        
        
        for(let i=0; i<conceptextra[0].concept_starttime.length;i++){
            const time1 = conceptextra[0].concept_endtime[i] .split("^^")[0];
            const time2 = conceptextra[0].concept_starttime[i] .split("^^")[0];
    
            let [hours1, minutes1, seconds1] = time1.split(":");
            seconds1=Math.floor(seconds1)
            seconds1=seconds1+hours1*3600
            console.log("hours1: ",hours1*3600," ",seconds1)
            seconds1=seconds1+minutes1*60
            console.log("minutes: ",minutes1*60," ",seconds1)
    
            let [hours2, minutes2, seconds2] = time2.split(":");
            seconds2=Math.floor(seconds2)
            seconds2=seconds2+hours2*3600
            console.log("hours2: ",hours2*3600," ",seconds2)
            seconds2=seconds2+minutes2*60
            console.log("hours2: ",minutes2*60," ",seconds2)
    
            let resultseconds = Math.abs(seconds2-seconds1);
            console.log("difference: ",resultseconds);
          
       
    
           
            duration = duration+resultseconds;
        }

        
        let hours = Math.floor(duration /3600)
        console.log("hour: ",hours," remain: ",Math.abs(hours - (duration /3600)))
        let remainminutes = Math.abs(hours - (duration /3600))
        let minutes = Math.floor(remainminutes * 60);
        console.log("minutes: ",minutes," remain: ",Math.abs(minutes - (remainminutes * 60)))
        let seconds = Math.abs(minutes - (remainminutes * 60))
        seconds = seconds*60
        console.log("seconds: ",seconds);
        console.log("Differenza di tempo in minuti:", hours,":",minutes,":",seconds);
        duration = hours+":"+minutes+":"+seconds
    }
    return(
        <>
        <Card elevation={shadow}
            color="primary" 
            sx={{ maxWidth: 250 , border: add?"2px solid #C6EBDC": '0px'}}
            onMouseEnter={()=>setshadow(5)}
            onMouseLeave={()=>setshadow(0)}
            onClick={()=>handleExpandClick()/*THI FOR OPEN THE MODAL BUT NOW ITS CHANGED. OLD CODE. JUST FOR REFERENCE setOpen(!open)*/}
            align="left"
            >

        <CardMedia
        sx={{   height: 140,
                margin: 2,
                marginBottom:0,
                }}
        image={"http://img.youtube.com/vi/"+imageurl+"/mqdefault.jpg"}
        title={titleurl}
      />
        <CardContent disableSpacing >

        <Typography noWrap variant="subtitle2" gutterBottom sx={{margin:0}}>
        <b>{titleurl}</b>
        </Typography>
        <Typography noWrap variant="subtitle2" gutterBottom sx={{marginTop:0}}>
        {creator}
        </Typography>
        
        </CardContent>
        <CardActions disableSpacing >
            
            
            <Chip label={"1 match"} size="small" sx={{backgroundColor:"rgb(255,128,0)", color:"white"}}/>

           <Box
                sx={{marginLeft: 'auto',
                    backgroundColor:'#B798f8', 
                    color:"white",
                    borderRadius:'20px 0 0 0',
                    width:'auto',
                    maxWidth:'200px',
                    height:"auto"}}
                onMouseEnter={()=>setHoverm(true)}
                onMouseLeave={()=>setHoverm(false)}
                
           
           >
            {
                hoverm?
                <>
                <Typography variant="body2" display="block" sx={{m:0, pb:0, pt:1, pr:1, pl:1}} gutterBottom>Aggiungi</Typography>
                <Typography variant="body2" display="block" sx={{m:0, pt:0, pb:1, pr:1, pl:1}} gutterBottom>al confronto</Typography>
                </>
                :
                <>
                <Typography variant="body2" display="block" sx={{m:0, p:0.5, pl:3, pr:3}} gutterBottom>VS</Typography>
                </>
            }
            
            
            </Box>
            
            
        </CardActions>
     
      </Card>
        
        
        
        
        
        
        
        
        
        
        <Collapse in={expanded} timeout="auto" unmountOnExit style={{position:'fixed',bottom: 0, left:0, right:0, backgroundColor:"white"}}>
            <Grid
            container
            direction="row"
            justifyContent="center"
            alignItems="center"
            id="1 COLONNA CENTRALE DATI"
            >
                <Grid item xs={2}></Grid>
                <Grid item>
                    <Grid
                    container
                    direction="column"
                    justifyContent="center"
                    alignItems="center"
                    id="2 SOPRA DATI SOTTO BOTTONE"
                    >
                        <Grid item>
                            <Grid
                            container
                            direction="row"
                            justifyContent="center"
                            alignItems="center"
                            id="3 SX VIDEO, DX DATI"
                            >
                                <Grid item>
                                    <img src={"http://img.youtube.com/vi/"+imageurl+"/mqdefault.jpg"} alt={titleurl} width="100%" height="auto"/>
                                </Grid>
                                <Grid item>
                                    <Grid
                                    container
                                    direction="column"
                                    justifyContent="center"
                                    alignItems="center"
                                    id="4 ROW TITOLO DATI BOTTONE"
                                    >
                                        <Grid item>
                                            <Grid
                                            container
                                            direction="row"
                                            justifyContent="space-between"
                                            alignItems="center"
                                            id="4 TITOLO"
                                            >
                                                <Grid item>
                                                <Typography variant="subtitle2" gutterBottom>
                                                    {titleurl}    
                                                </Typography>
                                                <Divider orientation="vertical" flexItem/>
                                                <Typography variant="caption" gutterBottom>
                                                    {creator}
                                                </Typography>
                                                </Grid>
                                                <Grid item>
                                                    <Chip label={<><Typography variant="caption" gutterBottom>
                                                            X
                                                        </Typography> 
                                                        <Divider orientation="vertical" flexItem/>
                                                        <Typography variant="caption" gutterBottom>
                                                            chiudi anteprima
                                                        </Typography></>}
                                                        onClick={()=>handleExpandClick()} />
                                                </Grid>
                                            </Grid>
                                        </Grid>
                                        <Grid item>
                                            <Grid
                                            container
                                            direction="row"
                                            justifyContent="center"
                                            alignItems="center"
                                            id="4 DATI"
                                            >
                                                <Grid item>
                                                    <Grid
                                                    container
                                                    direction="column"
                                                    justifyContent="center"
                                                    alignItems="flex-start"
                                                    id="SX"
                                                    >
                                                        <Grid item>
                                                            <Typography variant="caption" display="block" gutterBottom>
                                                                Cosa devi sapere prima di vedere questo video
                                                            </Typography>
                                                        </Grid>
                                                        <Grid item>
                                                            <Grid
                                                            container
                                                            direction="row"
                                                            justifyContent="flex-start"
                                                            alignItems="flex-start"
                                                            id="lista di prerequisiti"
                                                            >
                                                            
                                                                {(conceptextra[0]!=undefined&& conceptextra[0].list_preconcept.length>0)?
                                                                conceptextra[0].list_preconcept.map(keyword=>
                                                                    <Grid item xs="auto" key={keyword}>
                                                                        <Chip label={keyword} size="small" color="primary"/>
                                                                    </Grid>
                                                                ):
                                                                <Grid item xs="auto" >
                                                                        <Chip label="empty" size="small" color="primary"/>
                                                                    </Grid>
                                                                
                                                                }
                                                            </Grid>
                                                        </Grid>
                                                        <Grid item>
                                                            <Typography variant="caption" display="block" gutterBottom>
                                                                Cosa imparerai in questo video
                                                            </Typography>
                                                        </Grid>
                                                        <Grid item>
                                                            <Grid
                                                            container
                                                            direction="row"
                                                            justifyContent="flex-start"
                                                            alignItems="flex-start"
                                                            id="lista di concetti"
                                                            >
                                                                {concepts.map(keyword=>
                                                                    <Grid item xs="auto" key={keyword}>
                                                                        <Chip label={keyword} size="small" color="primary"/>
                                                                    </Grid>
                                                                )}
                                                            </Grid>
                                                        </Grid>
                                                    </Grid>
                                                </Grid>
                                                <Grid item>
                                                    <Grid
                                                    container
                                                    direction="column"
                                                    justifyContent="center"
                                                    alignItems="flex-start"
                                                    id="DX"
                                                    > 
                                                        <Grid item>
                                                            <Typography variant="caption" display="block" gutterBottom>
                                                                Durate:
                                                            </Typography>
                                                        </Grid>
                                                        <Grid item>
                                                            <Grid
                                                            container
                                                            direction="row"
                                                            justifyContent="center"
                                                            alignItems="center"
                                                            id="definizione"
                                                            >
                                                                <Grid item>
                                                                    <CircleIcon sx={{color:"rgb(255,168,37)"}}/>
                                                                </Grid>
                                                                <Grid item>
                                                                    <Typography variant="caption" gutterBottom>
                                                                        Definizione:
                                                                    </Typography>
                                                                </Grid>
                                                                <Grid item>
                                                                    <Typography variant="subtitle2" gutterBottom>
                                                                        {(conceptextra[0]!=undefined&& conceptextra[0].concept_starttime.length>0)?
                                                                            
                                                                            <Typography variant="caption" gutterBottom>{duration}</Typography>
                                                                            :
                                                                            <Typography variant="caption" gutterBottom>null</Typography>

                                                                        }
                                                                    </Typography>
                                                                </Grid>
                                                            </Grid>
                                                            
                                                        </Grid>
                                                        <Grid item>
                                                        
                                                        </Grid>
                                                        <Grid item>
                                                        
                                                        </Grid>
                                                        <Grid item>
                                                        
                                                        </Grid>
                                                    </Grid>                           
                                                </Grid>
                                            </Grid>
                                        </Grid>
                                        <Grid item>

                                        </Grid>
                                    </Grid>
                                </Grid>
                            </Grid>
                        </Grid>







                        {/* DA QUI SOTTO CE BOTTONE */}
                        <Grid item>

                        </Grid>
                    </Grid>
                </Grid>
                <Grid item xs={2}></Grid>
            </Grid>

        </Collapse>
        
        
        
        
        
        
        
        
        
        
        
        </>
    );
}