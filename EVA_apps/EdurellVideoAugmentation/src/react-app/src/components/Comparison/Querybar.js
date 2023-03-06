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

export default function Querybar({listvideo, listconcepts, AddQueryElement, nomatch}){
    listvideo = listvideo.map(video =>
    
        <>
        <Videoselected imageurl={video.img} title={video.title} idx={video.idx} setAdd={video.setAdd}/>
        <Divider orientation="vertical" flexItem>
                            vs
                        </Divider>
                        </>
    );
    return(
        <>
        <Container maxWidth="false" className="containerBig">
            <Container maxWidth = "xl" >
                <Stack
                    direction="row"
                    justifyContent="flex-start"
                    alignItems="center"
                    spacing={2}
                >
                <Queryinput listconcepts={listconcepts} AddQueryElement={AddQueryElement} nomatch={nomatch}/>
                <Secondarybutton/>
                </Stack>
            </Container>
            <br/>
            <br/>
            <Container maxWidth = "xl">
                <Stack
                    direction="row"
                    justifyContent="flex-start"
                    alignItems="center"
                    spacing={2}
                >
                    {listvideo}
                </Stack>
            </Container>
        </Container>


        

        </>
    );
}