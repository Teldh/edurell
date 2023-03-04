import Header from '../Header/Header';
import React from 'react';
import { useContext,useState } from 'react';
import {TokenContext} from '../account-management/TokenContext';
import Querybar from './Querybar.js';
import Listvideo from './Listvideo.js';
import { StyledEngineProvider } from '@mui/material/styles';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { ContextComparison } from './ContextComparison';


export default function Comparison(){
    const [listvideo, setListVideo]= useState([]);
    const contextType = useContext(TokenContext);
    const nameSurname  = contextType.nameSurname;

    function AddVideo(img, title){
        const newListVideo = [...listvideo,{img:img,title:title,idx:listvideo.length}];
        setListVideo(newListVideo);
        console.log("add video");
    }

    function RemoveVideo(idx){
        const newListVideo = listvideo.filter(video => video.idx != idx);
        setListVideo(newListVideo);
        console.log("remove video "+idx);
        console.log(newListVideo[0]);
        console.log(listvideo[0])
    }

    const theme = createTheme({
        palette: {
          primary: {
            main: '#C6EBDC',
          },
          secondary: {
            main: '#FA824C',
    
          },
          closexenter:{
            main: "#e64a19",
        
          },
          closexexit:{
            main:"#e57373",
          }
        },
      });
    return(
        <>
        <ThemeProvider theme={theme}>
        <StyledEngineProvider injectFirst> {/* to override the default style with your custom css */}
        <Header page="dashboard" login={nameSurname}/>
        <ContextComparison.Provider value={RemoveVideo}>
        <Querybar listvideo={listvideo} />
        </ContextComparison.Provider>
        <br/>
        <ContextComparison.Provider value={AddVideo}>
        <Listvideo/>
        </ContextComparison.Provider>
        </StyledEngineProvider>
        </ThemeProvider>
        </>
    );
}

/*
1) Per ogni lista in una state, va a generare un oggetto <Videoselected/> in <Querybar/>
2) Quando aggiungo un video, <Videoavailable> usa una funzione di this per aggiungere alla lista
3) Quando clicco x, tolgo l'elemento dalla lista
4) quando clicco sul video, mi apre il modal corrispondente?

*/