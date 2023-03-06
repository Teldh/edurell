import Header from '../Header/Header';
import React from 'react';
import { useContext,useState,useEffect } from 'react';
import {TokenContext} from '../account-management/TokenContext';
import Querybar from './Querybar.js';
import Listvideo from './Listvideo.js';
import { StyledEngineProvider } from '@mui/material/styles';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { ContextComparison } from './ContextComparison';
import handleFetchHttpErrors from '../../helpers/handleFetchHttpErrors'
import {
    Link,
    Redirect,
  } from "react-router-dom";
let checker = (arr, target) => target.every(v => arr.includes(v));
export default function Comparison(){
    const [listvideo, setListVideo]= useState([]);
    const [loading,setLoading]=useState(true);
    const [catalog,setCatalog]=useState(null);
    const [listConcepts, setListConcepts]=useState([]);
    const [querylist, setQueryList]=useState([]);
    const context = useContext(TokenContext);
    const nameSurname  = context.nameSurname;
    const [nomatch,setNomatch]=useState(false);
    let checker = (big, small) => small.every(v => big.includes(v));
    useEffect(() => {
        console.log("effect")
        const fetchData = async () => {
            let response=null
            try{
              response = await fetch('/api/get_catalog', {
                  method: 'GET',
                  headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Basic ' + btoa(context.token+':unused')
                  },
                })
                .then(handleFetchHttpErrors)
                .then(res => res.json())
            }
            catch(err){
              console.log(err)
              if(err.message==="401"){
                  
                  context.setToken('')
                  return <Redirect to="/" />
              }
              else  {
                
                  alert('Unknown Error')
                  return
              }
            }
            console.log("response",response)
            if(response===undefined){
              alert('Unknown Server Error')
              return
            }
            else{
              setCatalog(response.catalog)
              setLoading(false)
                //originallist = response.catalog
            
          }
        };
    
        fetchData();
        

      }, []);

    
      useEffect(() => {
        if (loading) { // It's used here...
          // ...
        } else {
          // ...// create unique list of concepts to use for queryinputs 
           
          let x=0;
          let newlistconcepts=[]
          catalog.map(video=>{
              
              video.extracted_keywords.map(concept=>{
                  
                  if(!newlistconcepts.includes(concept)){
                      newlistconcepts = [...newlistconcepts, concept];
                      
                  }
              })
      
          })
          x=x+1;
                  console.log(newlistconcepts);
          setListConcepts(newlistconcepts);
        
        }
      }, [loading]);

    function AddQueryElement(concept){
        //bug resettare la querylist coi elementi aggiornati
        if(catalog.length > 0 ){
            if(concept.length==0){
                //setCatalog(originalList);
            }
            console.log("addquery")
            const newquerylist = [...concept];
            setQueryList(newquerylist);
            
            
            let newcatalog = catalog.filter(video=>checker(video.extracted_keywords,concept));
            if(concept.length>0 && newcatalog.length==0){
                setNomatch(true)
            }else if(concept.length!=querylist.length){
                setNomatch(false);
            }
            newcatalog = [...newcatalog, ...catalog.filter(video=>!checker(video.extracted_keywords,concept))]
            setCatalog(newcatalog)
            

        }
    }

    function AddVideo(img, title,setAdd,idxurl){
        const newListVideo = [...listvideo,{img:img,title:title,idx:idxurl, setAdd:setAdd}];
        setListVideo(newListVideo);
        setAdd(true);
     
    }

    function RemoveVideo(idx){
        const newListVideo = listvideo.filter(video => video.idx != idx);
        setListVideo(newListVideo);
        
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
        <ContextComparison.Provider value={[AddVideo,RemoveVideo]}>
            <Querybar listvideo={listvideo} listconcepts={listConcepts} AddQueryElement={AddQueryElement} nomatch={nomatch}/>
            <br/>
            <Listvideo catalog={catalog} loading={loading}/>
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