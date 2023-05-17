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

/*


DEVI CAMBIARE FLASK MAIN.PY PER FAR IN MODO CHE NON PRENDE
IL PIU RECENTE MA ANCHE LA SOMMA DI TUTTI I GRAFI E FARCI LA SOMMA

SEMPRE SU MAIN.PY GUARDARE SE SI SPOSTA IL LOGIN FUORI  DA FUNZIONE
POSSO CHIAMARE SOLO LE QUERY SENZA AVERE PROBLEMI CON LE 500 CONNESSIONI
*/

export default function Comparison(){
    //list of video selected for comparison
    const [listvideo, setListVideo]= useState([]);

    //a bool to check if download list of video from DB is successful
    //if its false, doesnt list the videos in the page
    //if true, catalog is populate with the videos and display all the videos available
    const [loading,setLoading]=useState(true);

    //list of video from the mongodb collection vidoes. if successful get the data, set loading to true
    const [catalog,setCatalog]=useState(null);

    //each video in catalog has multiple concepts and each concepts has extra data required for the website
    const [catalogExtra, SetCatalogExtra]=useState([]);

    //more data for catalog for filters before selecting any concept
    const [catalogFilter, SetCatalogFilter]=useState([])

    //its the catalog but with fewer elements due to filters
    const [catalogoriginal, SetCatalogOriginal] = useState(null);

    //extract from catalog a list of unique concepts, so no duplicates used for textfield list
    const [listConcepts, setListConcepts]=useState([]);

    //used for textfield list, where we read all the concept user has selected.
    const [querylist, setQueryList]=useState([]);

    const context = useContext(TokenContext);
    const nameSurname  = context.nameSurname;

    //if from querylist, there is no video with that combination of concepts, set this to false otherwise true
    //used to make the textfield red to show errors
    const [nomatch,setNomatch]=useState(false);

    //in the previous page, you select a concept. this is used to capture that concept sent from previous page to this one
    let location = useLocation();

    //its used to show the list of videos selected under the queryinput.
    //by default its hidden when this is false. when you select a concept to search it becomes true
    const [searchClicked, SetSearchClicked] = useState(false);

    //check if concept selected to filter video to match
    const [searchFilterClicked,setSearchFilterClicked] = useState(false);

    //list fo filters value. used to filter the videos
    const [comparisonfilter, SetComparisonFilter] = useState([null,null,null,null,null,null,"recent"])
    
    //capturing the concept sent from previous page
    useEffect(() => {
      if(location.state != undefined)
      console.log("data from previous search comparison: ", location.state.data);
    }, [location]);


    //a function used to check if small is included into big
    let checker = (big, small) => small.every(v => big.includes(v));

    //request from mongodb to the value inside collection videos
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
              SetCatalogOriginal(response.catalog)
              setLoading(false)
                //originallist = response.catalog
            
          }
        };
    
        fetchData();
        

      }, []);

      //if query to videos collection is successful or not, depending on variable loading
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
          //used to get all type and preconcept of all video. not used anymore. just for reference in the future.
          //QueryVideoTypeAndPre()
        }
      }, [loading]);

      useEffect(()=>{

        if(searchFilterClicked){
          SetCatalogExtra(catalogExtra=>[])
          console.log("queryextra use effect ",catalog)
          let asd = catalogExtra
          catalog.map(video=>{
          console.log("sto facendo query")
          
            
            QueryConceptExtra(video.video_id, querylist)
          })
        
          
        }
      },[searchFilterClicked])


    //OLD, sort the video based on concept on query
    function AddQueryElementOLD(concept){
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
            
            setSearchFilterClicked(true)
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
    function AddQueryElement(concept){
      //attiva la lista video selected
      SetSearchClicked(true);
      console.log("DOPOCLICKBUTTON: ",searchFilterClicked)
      //SetCatalogOriginal(catalog);
      //setCatalog(catalogoriginal);
      //bug resettare la querylist coi elementi aggiornati
      console.log(catalog," ",catalogoriginal)
      if(catalog.length > 0 ){
          setCatalog(catalogoriginal);
         
          if(concept[0]==null){
              //setSearchFilterClicked(false);
              console.log("addqueryelement return")
              return;
          }
          setSearchFilterClicked(true);
          
          console.log("addquery ",concept)
          const newquerylist = [...concept];
          setQueryList(newquerylist);
          console.log("newquerylist: ",newquerylist)
          
          
          let newcatalog = catalogoriginal.filter(video=>checker(video.extracted_keywords,concept));
          if(concept.length>0 && newcatalog.length==0){
              setNomatch(true)
          }else if(concept.length!=querylist.length){
              setNomatch(false);
          }
          
      
          setCatalog(newcatalog)
          

      }
    }

    function ApplyFilters(listfilters){
      SetComparisonFilter(listfilters)

      //Look at filter UI.
      //lista nuovi video
      //  const [catalogoriginal, SetCatalogOriginal] = useState(null);

      //concettiextraperfiltri
      // const [catalogFilter, SetCatalogFilter]=useState([])

      //adatto a
      let newcatalog=null;
      if(comparisonfilter[0] == "novice"){
        //filtro, tutti i preconcetti concenuti nei concetti
        newcatalog = catalog.filter(video=>{
          console.log("NOVICE ",video.extracted_keywords," ",catalogFilter[video.video_id]["prerequisite"]);
          return checker(video.extracted_keywords, catalogFilter[video.video_id]["prerequisite"])});
      //  SetCatalogAfterFilter(newcatalog);
      }else if(comparisonfilter[0] == "expert"){
        newcatalog = catalog.filter(video=>{
          console.log("EXPERT ",video.extracted_keywords," ",catalogFilter[video.video_id]["prerequisite"]);
          return !checker(video.extracted_keywords, catalogFilter[video.video_id]["prerequisite"]);
        })
       // SetCatalogAfterFilter(newcatalog);
      }

      //spiegazione
      if(comparisonfilter[1] == "essential"){
        newcatalog = catalog.filter(video=>{
          console.log("essential ",catalogFilter[video.video_id]["typedef"]);
          return !checker(catalogFilter[video.video_id]["typedef"],"conceptExpansion");
        })
      ///  SetCatalogAfterFilter(newcatalog);

      }else if(comparisonfilter[1]=="detailed"){
        newcatalog = catalog.filter(video=>{
          console.log("detailed ",catalogFilter[video.video_id]["typedef"]);
          return checker(catalogFilter[video.video_id]["typedef"],"conceptExpansion");
        })
       // SetCatalogAfterFilter(newcatalog);
      }

      //tipo di lezione
      if(comparisonfilter[2] == "withslide"){
        newcatalog = catalog.filter(video=>{
          console.log("wihslide ",catalogFilter[video.video_id]["video_slidishness"]);
          return catalogFilter[video.video_id]["video_slidishness"] > 0.1? true:false;
        })
       // SetCatalogAfterFilter(newcatalog);
      }else if(comparisonfilter[2] == "withoutslide"){
        newcatalog = catalog.filter(video=>{
          console.log("wihslide ",catalogFilter[video.video_id]["video_slidishness"]);
          return catalogFilter[video.video_id]["video_slidishness"] <= 0.1? true:false;
        })
       // SetCatalogAfterFilter(newcatalog);
      }

      //definizione
      if(comparisonfilter[3]=="less4"){

      }else if(comparisonfilter[3]="4to20"){

      }else if(comparisonfilter[3]="greater20"){

      }

      //approfondimento
      if(comparisonfilter[4]=="less4"){

      }else if(comparisonfilter[4]="4to20"){

      }else if(comparisonfilter[4]="greater20"){

      }

      //video intero
      if(comparisonfilter[5]=="less4"){

      }else if(comparisonfilter[5]="4to20"){

      }else if(comparisonfilter[5]="greater20"){

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

    async function QueryVideoTypeAndPre(){
      console.log("startquerytypeandpre");
      const risposta = await fetch('/api/GetVideoTypeAndPrerequisite',{
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Basic ' + btoa(context.token+':unused')
        },
      })

      var data = await risposta.json();
      console.log('queryvideotyperep: ',data);
      SetCatalogFilter(data);
    }
    
    //query to the extra data for a specific concept
    async function QueryConceptExtra(videoid, concept) {
      console.log("START queryconceptextra");
      let risposta=null
      try{

       risposta = await fetch('/api/ConceptVideoData/'+videoid+"/"+concept, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Basic ' + btoa(context.token+':unused')
        },
      })
      }
      catch(err){
        console.log(err)
      }
      if(risposta===undefined){
        alert("problem  qeury")
        return
      }else{
        var data = await risposta.json();
        console.log("data catalogextra: ",data);
        SetCatalogExtra(catalogExtra=>[...catalogExtra,data]);
        console.log("catalogextra: ",catalogExtra)
      }
      

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
      
    return(
        <>
        
        <ThemeProvider theme={theme}>
        <StyledEngineProvider injectFirst> {/* to override the default style with your custom css */}
        <Header page="dashboard" login={nameSurname}/>
        <ContextComparison.Provider value={[AddVideo,RemoveVideo,setSearchFilterClicked]}>

            <>
            <Querybar ApplyFilters = {ApplyFilters} searchClicked={searchClicked} listvideo={listvideo} listconcepts={listConcepts} AddQueryElement={AddQueryElement} nomatch={nomatch} location={location.state===undefined?null:location.state.data}/>
            <br/>
            <Listvideo catalogExtra={catalogExtra} catalog={catalog} loading={loading} searchFilterClicked={searchFilterClicked} catalogoriginal={catalogoriginal}/>
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