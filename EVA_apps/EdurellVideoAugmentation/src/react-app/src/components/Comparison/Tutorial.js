import React from 'react';
import Modal from '@mui/material/Modal';
import {useState, useEffect,useRef} from 'react';
import EastIcon from '@mui/icons-material/East';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Menu from '@mui/material/Menu';
import WestIcon from '@mui/icons-material/West';
export default function Tutorial({anchor1,anchor2, open, closeTutorial}){

    const[page,setPage]=useState(0)
    const [anchorEl, setAnchorEl] = useState([null,null,null,null]);

    
    if(open){
        console.log("TUTORIAL: ",anchor1," ",anchor2)
    }
  

    
    useEffect(() => {
        setAnchorEl([anchorEl[0],anchor1.current,anchorEl[2],anchorEl[3]])
      }, [anchor1.current]);

    useEffect(()=>{
        setAnchorEl([anchorEl[0],anchorEl[1],anchor2,anchorEl[3]])
    },[anchor2])
    const handleClick = (event) => {
      setAnchorEl(event.currentTarget);
    };
    const handleClose = () => {
     // setAnchorEl(null);
    };

    function NextPage(){
        console.log("nextpage: ",page)


        if(page==0 && anchor1.current != null){
            anchor1.current.style.zIndex=10000;
        }else{
            anchor1.current.style.zIndex="auto";
        }

        if(page==1 && anchor1.current != null){
            anchor2.style.zIndex=10000;
        }else{
            anchor2.style.zIndex="auto";
        }
        if(page<3){
            setPage(page+1)
            
        }else{

        }
    }

    function PreviousPage(){
        if(page==2 && anchor1.current != null){
            anchor1.current.style.zIndex=10000;
        }else{
            anchor1.current.style.zIndex="auto";
        }
        if(page==2 && anchor1.current != null){
            anchor2.style.zIndex=10000;
        }else{
            anchor2.style.zIndex="auto";
        }
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
        sx={{mt:1}}
        anchorEl={anchorEl[page]}
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
              display: page==0?'none':page==3?'none':'block',
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
                            {page+1}/4
                        </Typography>
                    </Grid>
                    <Grid item>
                        <Typography variant="caption" display="block" gutterBottom onClick={closeTutorial}>
                            close | x
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
                >   {page==0?
                    <>
                    <Grid item>
                        <Typography variant="h6" gutterBottom>
                            Too many videos?
                        </Typography>
                    </Grid>
                    </>
                    :
                        page==1?
                            <>
                                <Grid item>
                                    <Typography variant="h6" gutterBottom>
                                        Set your filters for video
                                    </Typography>
                                </Grid>
                                <Grid item>
                                    <Typography variant="h6" gutterBottom>
                                        search
                                    </Typography>
                                </Grid>
                            </>
                            :
                            page==2?
                            <>
                                <Grid item>
                                    <Typography variant="h6" gutterBottom>
                                        Click
                                    </Typography>
                                    <Typography variant="h6" gutterBottom>
                                        to choose and
                                    </Typography>
                                </Grid>
                                <Grid item>
                                    <Typography variant="h6" gutterBottom>
                                        compare up to 4 videos
                                    </Typography>
                                </Grid>
                            </>
                            :
                            page==3?
                            <>
                                <Grid item>
                                    <Typography variant="h6" gutterBottom>
                                        Compare video stats and
                                    </Typography>
                                </Grid>
                                <Grid item>
                                    <Typography variant="h6" gutterBottom>
                                        choose the best video for
                                    </Typography>
                                </Grid>
                                <Grid item>
                                    <Typography variant="h6" gutterBottom>
                                        your needs!
                                    </Typography>
                                </Grid>
                            </>
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
                        page==0?
                        
                        <>
                            <Grid item>
                                <Typography variant="caption" display="block" gutterBottom>
                                    Don't worry,
                                </Typography>
                            </Grid>
                            <Grid item>
                                <Typography variant="caption" display="block" gutterBottom>
                                    we'll <b>help</b> you out!
                                </Typography>
                            </Grid>
                        </>
                        :
                        page==1?
                            <>
                                <Grid item>
                                    <Typography variant="caption" display="block" gutterBottom>
                                        Here you can select video
                                    </Typography>
                                </Grid>
                                <Grid item>
                                    <Typography variant="caption" display="block" gutterBottom>
                                        duration, expertise level and
                                    </Typography>
                                </Grid>
                                <Grid item>
                                    <Typography variant="caption" display="block" gutterBottom>
                                        other features to get the perfect
                                    </Typography>
                                </Grid>
                                <Grid item>
                                    <Typography variant="caption" display="block" gutterBottom>
                                        video you are looking for!
                                    </Typography>
                                </Grid>
                            </>
                            :
                            page==2?
                            <>
                                <Grid item>
                                    <Typography variant="caption" display="block" gutterBottom>
                                        Are there too many videos <b>and you don't know</b>
                                    </Typography>
                                </Grid>
                                <Grid item>
                                    <Typography variant="caption" display="block" gutterBottom>
                                        <b>which one to watch?</b>
                                    </Typography>
                                </Grid>
                                <Grid item>
                                    <Typography variant="caption" display="block" gutterBottom>
                                        <b>compare them</b> and find what suits you best!
                                    </Typography>
                                </Grid>
                            </>
                            :
                            page==3?
                            <>
                                <Grid item>
                                    <Typography variant="caption" display="block" gutterBottom>
                                        After choosing all the videos you want to compare
                                    </Typography>
                                </Grid>
                                <Grid item>
                                    <Typography variant="caption" display="block" gutterBottom>
                                        you will be able to access <b>all the stats</b> regarding:
                                    </Typography>
                                </Grid>
                                <Grid item>
                                    <ul>
                                        <li>
                                            <Typography variant="caption" display="block" gutterBottom>
                                                <b>Duration</b> of the whole video and also of the specific parts about the concept
                                            </Typography>
                                        </li>
                                        <li>
                                            <Typography variant="caption" display="block" gutterBottom>
                                                <b>What you should already know</b>
                                            </Typography>
                                        </li>
                                        <li>
                                            <Typography variant="caption" display="block" gutterBottom>
                                                <b>What you'll learn</b>
                                            </Typography>
                                        </li>
                                        <li>
                                            <Typography variant="caption" display="block" gutterBottom>
                                                Whether or not you'll find any <b>slides</b> in the video
                                            </Typography>
                                        </li>
                                    </ul>
                                </Grid>
                                <Grid item>
                                    <Typography variant="body2" display="block" gutterBottom>
                                        What are you waiting for?
                                    </Typography>
                                </Grid>
                                <Grid item>
                                    <Typography variant="body2" display="block" gutterBottom>
                                        <b>Try it yourself!</b>
                                    </Typography>
                                </Grid>
                            </>
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
                    {
                        page==0?
                        <>
                            <Grid item>

                            </Grid>
                        </>
                        :
                        <>
                            <Grid item xs="auto" sx={{p: 2 ,backgroundColor:'#B798f8', borderRadius:'0 50px 0 50px'}} onClick={PreviousPage}>
                                <Grid
                                container
                                direction="row"
                                justifyContent="center"
                                alignItems="center"
                                >
                                
                                    <Grid item>
                                        <WestIcon sx={{color:"#FFFFFF"}}/>
                                    </Grid>
                                    <Grid item>
                                        <p style={{color:'white'}}>Back</p>
                                    </Grid>
                                            
                                    
                                    
                                </Grid>
                            </Grid>
                        </>
                    }
                    
                    <Grid item xs="auto" sx={{p: 2 ,backgroundColor:'#B798f8', borderRadius:'50px 0 50px 0'}} onClick={NextPage}>
                        <Grid
                        container
                        direction="row"
                        justifyContent="center"
                        alignItems="center"
                        >
                            {
                                page==3?
                                <>
                                    <Grid item>
                                        <p style={{color:'white'}}>Got it, thanks.</p>
                                    </Grid>
                                </>
                                :
                                <>
                                    <Grid item>
                                        <p style={{color:'white'}}>Next</p>
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