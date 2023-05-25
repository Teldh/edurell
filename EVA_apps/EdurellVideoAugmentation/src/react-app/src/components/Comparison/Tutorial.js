import React from 'react';
import Modal from '@mui/material/Modal';
import {useState} from 'react';
import EastIcon from '@mui/icons-material/East';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Menu from '@mui/material/Menu';
import WestIcon from '@mui/icons-material/West';
export default function Tutorial({anchors, open, closeTutorial}){

    const[page,setPage]=useState(1)
    const [anchorEl, setAnchorEl] = useState(anchors[0]);

    const handleClick = (event) => {
      setAnchorEl(event.currentTarget);
    };
    const handleClose = () => {
      setAnchorEl(null);
    };

    function NextPage(){
        if(page==1){
            setAnchorEl(anchors[1])
        }
        if(page<4){
            setPage(page+1)
        }else{

        }
    }

    function PreviousPage(){
        if(page >0){
            setPage(page-1)
        }else{

        }
    }

    return(<>
    <Modal
    open={open}
    aria-labelledby="modal-modal-title"
    aria-describedby="modal-modal-description"
    >
    <Menu
        anchorEl={anchorEl}
        id="account-menu"
        open="true"
        onClose={handleClose}
        onClick={handleClose}
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
        <Grid
        container
        direction="column"
        justifyContent="center"
        alignItems="stretch"
        >
            <Grid item>
                <Grid
                container
                direction="row"
                justifyContent="space-between"
                alignItems="center"
                >
                    <Grid item>
                        <Typography variant="caption" display="block" gutterBottom>
                            {page}/4
                        </Typography>
                    </Grid>
                    <Grid item>
                        <Typography variant="caption" display="block" gutterBottom onClick={closeTutorial}>
                            chiudi | x
                        </Typography>
                    </Grid>
                </Grid>
            </Grid>
            <Grid item>
                <Grid
                container
                direction="column"
                justifyContent="flex-start"
                alignItems="center"
                >   {page==1?
                    <>
                    <Grid item>
                        <Typography variant="h6" gutterBottom>
                            Troppi video tra 
                        </Typography>
                    </Grid>
                    <Grid item>
                        <Typography variant="h6" gutterBottom>
                            cui cercare?
                        </Typography>
                    </Grid>
                    </>
                    :
                        page==2?
                            <>
                            </>
                            :
                            page==3?
                            <>
                            </>
                            :
                            page==4?
                            <></>
                            :
                            <></>
                    }
                </Grid>
            </Grid>
            <Grid item>
                <Grid
                container
                direction="column"
                justifyContent="flex-start"
                alignItems="center"
                >
                    {
                        page==1?
                        
                        <>
                            <Grid item>
                                <Typography variant="caption" display="block" gutterBottom>
                                    Nessun problema,
                                </Typography>
                            </Grid>
                            <Grid item>
                                <Typography variant="caption" display="block" gutterBottom>
                                    ti <b>aiutiamo</b> noi
                                </Typography>
                            </Grid>
                        </>
                        :
                        page==2?
                            <>
                            </>
                            :
                            page==3?
                            <>
                            </>
                            :
                            page==4?
                            <></>
                            :
                            <></>
                    }
                    
                </Grid>
            </Grid>
            <Grid item>
                <Grid
                container
                direction="row"
                justifyContent="space-between"
                alignItems="center"
                >
                    <Grid item xs="auto" sx={{p: 2 ,backgroundColor:'#B798f8', borderRadius:'0 50px 0 50px'}} onClick={PreviousPage}>
                        <Grid
                        container
                        direction="row"
                        justifyContent="center"
                        alignItems="center"
                        >
                            {
                                page==1?
                                <>
                                    
                                </>
                                :
                                <>  
                                    <Grid item>
                                        <WestIcon sx={{color:"#FFFFFF"}}/>
                                    </Grid>
                                    <Grid item>
                                        <p style={{color:'white'}}>Avanti</p>
                                    </Grid>
                                    
                                </>
                            }
                            
                        </Grid>
                    </Grid>
                    <Grid item xs="auto" sx={{p: 2 ,backgroundColor:'#B798f8', borderRadius:'50px 0 50px 0'}} onClick={NextPage}>
                        <Grid
                        container
                        direction="row"
                        justifyContent="center"
                        alignItems="center"
                        >
                            {
                                page==4?
                                <>
                                    <Grid item>
                                        <p style={{color:'white'}}>Fine</p>
                                    </Grid>
                                </>
                                :
                                <>
                                    <Grid item>
                                        <p style={{color:'white'}}>Avanti</p>
                                    </Grid>
                                    <Grid item>
                                        <EastIcon sx={{color:"#FFFFFF"}}/>
                                    </Grid>
                                </>
                            }
                            
                        </Grid>
                    </Grid>
                </Grid>
            </Grid>
        </Grid>
    </Menu>
    </Modal>
    </>);
}