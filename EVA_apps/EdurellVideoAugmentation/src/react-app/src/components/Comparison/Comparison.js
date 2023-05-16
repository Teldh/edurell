import Header from '../Header/Header';
import React from 'react';
import { useContext,useState,useEffect } from 'react';
import {TokenContext} from '../account-management/TokenContext';
import Querybar from './Querybar.js';
import Listvideo from './Listvideo.js';
import { StyledEngineProvider } from '@mui/material/styles';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { ContextComparison } from './ContextComparison';
import handleFetchHttpErrors from '../../helpers/handleFetchHttpErrors';
import Button from '@mui/material/Button';
import C_Start from './C_Start.js';
import {
    Link,
    Redirect,
    Switch, 
    Route,
    useLocation
  } from "react-router-dom";



export default function Comparison(){
    const [listvideo, setListVideo]= useState([]);
    const [loading,setLoading]=useState(true);
    const [catalog,setCatalog]=useState(null);
    const [listConcepts, setListConcepts]=useState([]);
    const [querylist, setQueryList]=useState([]);
    const context = useContext(TokenContext);
    const nameSurname  = context.nameSurname;
    const [nomatch,setNomatch]=useState(false);
    const [firsttime, setFirstTime] = useState(true);
    let location = useLocation();
    const [searchClicked, SetSearchClicked] = useState(false);
    const [comparisonfilter, SetComparisonFilter] = useState([null,null,null,null,null,null,"recent"])
    useEffect(() => {
      if(location.state != undefined)
      console.log("data from previous search comparison: ", location.state.data);
    }, [location]);


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
        SetSearchClicked(true);
        //bug resettare la querylist coi elementi aggiornati
        if(catalog.length > 0 ){
            if(concept.length==0){
                //setCatalog(originalList);
            }
            console.log("addquery ",concept)
            const newquerylist = [...concept];
            setQueryList(newquerylist);
            console.log("newquerylist: ",newquerylist)
            
            
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

    function Endcstart(){
      setFirstTime(false);
      console.log("ENDSTART")
    }
    
    
    async function testf() {
      console.log("TESTCLICK");
      const risposta = await fetch('/api/ConceptVideoData/JDmNvQj0I5A/thing', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Basic ' + btoa(context.token+':unused')
        },
      })

      var data = await risposta.json();
      console.log("risposta: ",risposta);
      console.log("data: ",data);
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
          },
          whito:{
            main:'#FFFFFF',
          }
        },
      });
      console.log("TESTTTTT: ",comparisonfilter);
    return(
        <>
        
        <ThemeProvider theme={theme}>
        <StyledEngineProvider injectFirst> {/* to override the default style with your custom css */}
        <Header page="dashboard" login={nameSurname}/>
        <ContextComparison.Provider value={[AddVideo,RemoveVideo]}>

            <>
            <Querybar setfilter = {SetComparisonFilter} searchClicked={searchClicked} listvideo={listvideo} listconcepts={listConcepts} AddQueryElement={AddQueryElement} nomatch={nomatch} location={location.state===undefined?null:location.state.data}/>
            <br/>
            <Listvideo catalog={catalog} loading={loading}/>
            </>
            
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