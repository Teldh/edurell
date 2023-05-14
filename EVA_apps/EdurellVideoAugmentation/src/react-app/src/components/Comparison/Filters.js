import * as React from 'react';
import Chip from '@mui/material/Chip';
import TuneRoundedIcon from '@mui/icons-material/TuneRounded';
import Typography from '@mui/material/Typography';
import {useState} from 'react';
import Grid from '@mui/material/Grid';
import Divider from '@mui/material/Divider';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Collapse from '@mui/material/Collapse';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Button from '@mui/material/Button';
import imag from './imgtest/brainicon.PNG'
import { useTheme } from '@material-ui/core/styles';
import CancelIcon from '@mui/icons-material/Cancel';
import Paper from '@mui/material/Paper';
import Fade from '@mui/material/Fade';
import Modal from '@mui/material/Modal';
import Backdrop from '@mui/material/Backdrop';
import Badge from '@mui/material/Badge';
import Stack from '@mui/material/Stack';
import Box from '@mui/material/Box';
import { styled } from '@mui/material/styles';
import IconButton from '@mui/material/IconButton';
import { useContext } from 'react';
import { ContextComparison } from './ContextComparison';
import {TokenContext} from '../account-management/TokenContext';
import HelpIcon from '@mui/icons-material/Help';
import Popover from '@mui/material/Popover';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';

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
  

const StyledToggleButtonGroup = styled(ToggleButtonGroup)(({ theme }) => ({
'& .MuiToggleButtonGroup-grouped': {
    margin: theme.spacing(0.5),
    border: 0,
    '&.Mui-disabled': {
    border: 0,
    },
    '&:not(:first-of-type)': {
    borderRadius: theme.shape.borderRadius,
    },
    '&:first-of-type': {
    borderRadius: theme.shape.borderRadius,
    },
},
}));
  
export default function Filters(){

    const [expanded, setExpanded] = useState(false);
    const handleExpandClick = () => {
        setExpanded(!expanded);
    };

    const [anchorEl1, setAnchorEl1] = useState(null);
    const handlePopoverOpen1 = (event) => {
        setAnchorEl1(event.currentTarget);
    };
    const handlePopoverClose1 = () => {
        setAnchorEl1(null);
    };
    const open1 = Boolean(anchorEl1);

    const [anchorEl2, setAnchorEl2] = useState(null);
    const handlePopoverOpen2 = (event) => {
        setAnchorEl2(event.currentTarget);
    };
    const handlePopoverClose2 = () => {
        setAnchorEl2(null);
    };
    const open2 = Boolean(anchorEl2);

    const [anchorEl3, setAnchorEl3] = useState(null);
    const handlePopoverOpen3 = (event) => {
        setAnchorEl3(event.currentTarget);
    };
    const handlePopoverClose3 = () => {
        setAnchorEl3(null);
    };
    const open3 = Boolean(anchorEl3);


    const [alignment1, setAlignment1] = useState('web');

    const handleChange1 = (event, newAlignment) => {
        setAlignment1(newAlignment);
    };
    const [alignment2, setAlignment2] = useState('web');

    const handleChange2 = (event, newAlignment) => {
        setAlignment2(newAlignment);
    };
    const [alignment3, setAlignment3] = useState('web');

    const handleChange3 = (event, newAlignment) => {
        setAlignment3(newAlignment);
    };
    return(<>
        
        <Chip 
            sx={{width:'auto', margin:'5px'}}
            avatar={<TuneRoundedIcon/>}
            label="Clickable" 
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

        <Collapse in={expanded} timeout="auto" unmountOnExit>
            <Grid 
            container
            direction="row"
            justifyContent="center"
            alignItems="center"
            spacing={2}
            id="TRE COLONNE PRINCIPALI"
            >
                <Grid item>
                    <Grid
                    container
                    direction="column"
                    justifyContent="center"
                    alignItems="center"
                    id="CARATTERISTICHE"
                    >
                        <Grid item>
                            <Grid
                            container
                            direction="column"
                            justifyContent="center"
                            alignItems="flex-start"
                            id="TITOLO"
                            >
                                <Grid item>
                                    <Typography variant="h6" gutterBottom>
                                        CARATTERISTICHE:
                                    </Typography>
                                </Grid>
                            </Grid>
                        </Grid>
                        <Grid item>
                            <Grid
                            container
                            direction="column"
                            justifyContent="center"
                            alignItems="flex-start"
                            id="ADATTO A"
                            >
                                <Grid item>
                                    <HelpIcon
                                    onMouseEnter={handlePopoverOpen1}
                                    onMouseLeave={handlePopoverClose1}
                                    sx={{color:"rgb(255,128,0)"}}/>
                                    <Typography variant="subtitle2" display="inline" gutterBottom>
                                        · Adatto a:
                                    </Typography>
                                    
                                                <Popover 
                                                sx={{
                                                    pointerEvents: 'none',
                                                }}
                                                open={open1}
                                                anchorEl={anchorEl1}
                                                anchorOrigin={{
                                                    vertical: 'bottom',
                                                    horizontal: 'left',
                                                }}
                                                transformOrigin={{
                                                    vertical: 'top',
                                                    horizontal: 'right',
                                                }}
                                                onClose={handlePopoverClose1}
                                                disableRestoreFocus
                                                >
                                                <Box sx={{ width: '100%', maxWidth: 200 }}>
                                                    <Typography variant="body2" gutterBottom>
                                                    Nei video per principianti troverai spiegato sia il concetto che cerchi che i suoi prerequisiti. Se sei gia piu esperto troverai piu video in cui la conoscenza dei prerequisiti e' data per scontata
                                                    </Typography>
                                                </Box>
                                                </Popover>
                                </Grid>
                                <Grid item>
                                    <StyledToggleButtonGroup
                                    
                                    value={alignment1}
                                    exclusive
                                    onChange={handleChange1}
                                    aria-label="Platform"
                                    >
                                    <ToggleButton value="esperti">Esperti</ToggleButton>
                                    <ToggleButton value="principianti">Principianti</ToggleButton>
                                    </StyledToggleButtonGroup>
                                </Grid>
                            </Grid>
                        </Grid>
                        <Grid item>
                            <Grid
                            container
                            direction="column"
                            justifyContent="center"
                            alignItems="flex-start"
                            id="SPIEGAZIONE"
                            >
                                <Grid item>
                                    <HelpIcon
                                    onMouseEnter={handlePopoverOpen2}
                                    onMouseLeave={handlePopoverClose2}
                                    sx={{color:"rgb(255,128,0)"}}/>
                                    <Typography variant="subtitle2" display="inline" gutterBottom>
                                        · Adatto a:
                                    </Typography>
                                    
                                                <Popover 
                                                sx={{
                                                    pointerEvents: 'none',
                                                }}
                                                open={open2}
                                                anchorEl={anchorEl2}
                                                anchorOrigin={{
                                                    vertical: 'bottom',
                                                    horizontal: 'left',
                                                }}
                                                transformOrigin={{
                                                    vertical: 'top',
                                                    horizontal: 'right',
                                                }}
                                                onClose={handlePopoverClose2}
                                                disableRestoreFocus
                                                >
                                                <Box sx={{ width: '100%', maxWidth: 200 }}>
                                                    <Typography variant="body2" gutterBottom>
                                                    Una spiegazione essenziale andra dritta al punto senza distrazioni. Una spiegazione approfondita e' lideale se vuoi esplorare ogni sfumatura di ogni concetto
                                                    </Typography>
                                                </Box>
                                                </Popover>
                                </Grid>
                                <Grid item>
                                    <StyledToggleButtonGroup
                                    
                                    value={alignment2}
                                    exclusive
                                    onChange={handleChange2}
                                    aria-label="Platform"
                                    >
                                    <ToggleButton value="esperti">Essenziale</ToggleButton>
                                    <ToggleButton value="principianti">Approfondita</ToggleButton>
                                    </StyledToggleButtonGroup>
                                </Grid>
                            
                            </Grid>
                        </Grid>
                        <Grid item>
                            <Grid
                            container
                            direction="column"
                            justifyContent="center"
                            alignItems="flex-start"
                            id="TIPO DI LEZIONE"
                            >
                                <Grid item>
                                    <HelpIcon
                                    onMouseEnter={handlePopoverOpen3}
                                    onMouseLeave={handlePopoverClose3}
                                    sx={{color:"rgb(255,128,0)"}}/>
                                    <Typography variant="subtitle2" display="inline" gutterBottom>
                                        · Adatto a:
                                    </Typography>
                                    
                                                <Popover 
                                                sx={{
                                                    pointerEvents: 'none',
                                                }}
                                                open={open3}
                                                anchorEl={anchorEl3}
                                                anchorOrigin={{
                                                    vertical: 'bottom',
                                                    horizontal: 'left',
                                                }}
                                                transformOrigin={{
                                                    vertical: 'top',
                                                    horizontal: 'right',
                                                }}
                                                onClose={handlePopoverClose3}
                                                disableRestoreFocus
                                                >
                                                <Box sx={{ width: '100%', maxWidth: 200 }}>
                                                    <Typography variant="body2" gutterBottom>
                                                        Scegli video con slide se preferisci seguire una presentazione. Scegli senza slide se preferisci altre modalita'
                                                    </Typography>
                                                </Box>
                                                </Popover>
                                </Grid>
                                <Grid item>
                                    <StyledToggleButtonGroup
                                    
                                    value={alignment3}
                                    exclusive
                                    onChange={handleChange3}
                                    aria-label="Platform"
                                    >
                                    <ToggleButton value="esperti">Con slide</ToggleButton>
                                    <ToggleButton value="principianti">Senza slide</ToggleButton>
                                    </StyledToggleButtonGroup>
                                </Grid>
                            </Grid>
                        </Grid>
                    
                    </Grid>
                </Grid>






                <Grid item>
                    <Grid
                    container
                    direction="column"
                    justifyContent="center"
                    alignItems="center"
                    >
                    
                    </Grid>
                </Grid>
                <Grid item>
                    <Grid
                    container
                    direction="column"
                    justifyContent="center"
                    alignItems="center"
                    >
                    
                    </Grid>
                </Grid>

            </Grid>
        </Collapse>
        
        
        
    
    
    
    
    </>);
}