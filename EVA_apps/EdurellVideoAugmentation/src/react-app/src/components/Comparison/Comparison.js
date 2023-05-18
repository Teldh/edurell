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
    let checker = (big, small) => {
      console.log("checker: ",big," ",small)
      return small.every(v => big.includes(v));
    };

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

    function ComputeDuration(start,end){
      let duration=0
      for(let i=0; i<start.length;i++){
        const time1 = end[i] .split("^^")[0];
        const time2 = start[i] .split("^^")[0];

        let [hours1, minutes1, seconds1] = time1.split(":");
        seconds1=Math.floor(seconds1)
        seconds1=seconds1+hours1*3600
        seconds1=seconds1+minutes1*60

        let [hours2, minutes2, seconds2] = time2.split(":");
        seconds2=Math.floor(seconds2)
        seconds2=seconds2+hours2*3600
        seconds2=seconds2+minutes2*60

        let resultseconds = Math.abs(seconds2-seconds1);
        duration = duration+resultseconds;
      }

        return duration
    }

    function ApplyFilters(listfilters){
      //SetComparisonFilter(listfilters)

      //Look at filter UI.
      //lista nuovi video
      //  const [catalogoriginal, SetCatalogOriginal] = useState(null);

      //concettiextraperfiltri
      // const [catalogFilter, SetCatalogFilter]=useState([])
      
       //applicare filtri
       console.log("querylist filter: ",querylist)
       let catalogfiltered=[...catalogoriginal];
        catalogfiltered = catalogfiltered.filter(video=>checker(video.extracted_keywords,querylist));
        console.log("inizio filtri: ",listfilters)
        console.log("catalogextra: ",catalogExtra)
        console.log("catalogfiltered: ",catalogfiltered)

       if(listfilters[0] == "novice"){
         //filtro, tutti i preconcetti concenuti nei concetti
         catalogfiltered = catalogfiltered.filter(video=>{
           console.log("NOVICE ",video.extracted_keywords," ",catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id)[0]["list_preconcept"]);
           if(catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id)[0]["list_preconcept"].length == 0){
            return true;
           }
           return checker(video.extracted_keywords, catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id)[0]["list_preconcept"])});
       }else if(listfilters[0] == "expert"){
         catalogfiltered = catalogfiltered.filter(video=>{
           console.log("EXPERT ",video.extracted_keywords," ",catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id));
           if(catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id)[0]["list_preconcept"].length == 0){
            return false;
           }
           return !checker(video.extracted_keywords, catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id)[0]["list_preconcept"]);
         })
       }

       

       //spiegazione
       if(listfilters[1] == "essential"){
         catalogfiltered = catalogfiltered.filter(video=>{
           console.log("essential ",catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id)[0]["explain"]);
           //if conceptexpansion array is empty, return always true
           if(catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id)[0]["explain"].length == 0){
            return true;
           }
           return !checker(catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id)[0]["explain"],["conceptExpansion"]);
         })
  

       }else if(listfilters[1]=="detailed"){
         catalogfiltered = catalogfiltered.filter(video=>{
           console.log("detailed ",catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id)[0]["explain"]);
           if(catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id)[0]["explain"].length == 0){
            return true;
           }
           return checker(catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id)[0]["explain"],["conceptExpansion"]);
         })
  
       }
     

       //tipo di lezione
       if(listfilters[2] == "withslide"){
         catalogfiltered = catalogfiltered.filter(video=>{
           console.log("wihslide ",catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id)[0]["video_slidishness"]);
           return catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id)[0]["video_slidishness"] > 0.1? true:false;
         })
 
       }else if(listfilters[2] == "withoutslide"){
         catalogfiltered = catalogfiltered.filter(video=>{
           console.log("withoutslide ",catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id)[0]["video_slidishness"]);
           return catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id)[0]["video_slidishness"] <= 0.1? true:false;
         })
    
       }
       

        console.log("definizione")
       //definizione
       if(listfilters[3]=="less4"){
          catalogfiltered = catalogfiltered.filter(video=>{
            let starttime = catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id)[0]["concept_starttime"]
            let endtime = catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id)[0]["concept_endtime"]
            console.log("starttime: ",starttime, " endtime: ",endtime," duration: ",ComputeDuration(endtime, starttime))
            return ComputeDuration(endtime, starttime) < 240
          });
    
       }else if(listfilters[3]=="4to20"){
          catalogfiltered = catalogfiltered.filter(video=>{
            let starttime = catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id)[0]["concept_starttime"]
            let endtime = catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id)[0]["concept_endtime"]
            console.log("starttime: ",starttime, " endtime: ",endtime," duration: ",ComputeDuration(endtime, starttime))
            return ComputeDuration(endtime, starttime) >= 240 && ComputeDuration(endtime, starttime) <= 1200
          });
      
       }else if(listfilters[3]=="greater20"){
          catalogfiltered = catalogfiltered.filter(video=>{
            let starttime = catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id)[0]["concept_starttime"]
            let endtime = catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id)[0]["concept_endtime"]
            console.log("starttime: ",starttime, " endtime: ",endtime," duration: ",ComputeDuration(endtime, starttime))
            return ComputeDuration(endtime, starttime) > 1200
          });
    
       }
   

        console.log("approfondimento")
       //approfondimento
       if(listfilters[4]=="less4"){
          catalogfiltered = catalogfiltered.filter(video=>{
            let starttime = catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id)[0]["derivatedconcept_starttime"]
            let endtime = catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id)[0]["derivatedconcept_endtime"]
            console.log("starttime: ",starttime, " endtime: ",endtime," duration: ",ComputeDuration(endtime, starttime))
            return ComputeDuration(endtime, starttime) < 240
          });

       }else if(listfilters[4]=="4to20"){
          catalogfiltered = catalogfiltered.filter(video=>{
            let starttime = catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id)[0]["derivatedconcept_starttime"]
            let endtime = catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id)[0]["derivatedconcept_endtime"]
            console.log("starttime: ",starttime, " endtime: ",endtime," duration: ",ComputeDuration(endtime, starttime))
            return ComputeDuration(endtime, starttime) >= 240 && ComputeDuration(endtime, starttime) <= 1200
          });

       }else if(listfilters[4]=="greater20"){
          catalogfiltered = catalogfiltered.filter(video=>{
            let starttime = catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id)[0]["derivatedconcept_starttime"]
            let endtime = catalogExtra.filter(videoExtra=>videoExtra.video_id == video.video_id)[0]["derivatedconcept_endtime"]
            console.log("starttime: ",starttime, " endtime: ",endtime," duration: ",ComputeDuration(endtime, starttime))
            return ComputeDuration(endtime, starttime) > 1200
          });

       }


        console.log("video intero")
       //video intero
       if(listfilters[5]=="less4"){
          catalogfiltered = catalogfiltered.filter(video=>video.duration < 240)

          console.log("after filter: ",catalogfiltered)
       }else if(listfilters[5]=="4to20"){
          console.log("videointero 4to20: ",catalogfiltered.filter(video=>video.duration >= 240 && video.duration < 1200))
          catalogfiltered = catalogfiltered.filter(video=>video.duration >= 240 && video.duration < 1200)

          console.log("after filter: ",catalogfiltered)
       }else if(listfilters[5]=="greater20"){

          catalogfiltered = catalogfiltered.filter(video=>{

            console.log("video intero: ",video.video_id," ",video.duration," ",video.duration > 1200)
            return video.duration > 1200;})
          console.log("after filter: ",catalogfiltered)
 
       }


       console.log("sort")
       if(listfilters[6]=="recent"){
          console.log("sort: ",catalogfiltered)
          catalogfiltered = catalogfiltered.sort(
            function(a,b){
              console.log("a: ",a," b: ",b)
              console.log("recent ",catalogExtra.filter(videoExtra=>{
                console.log("dentro: ",videoExtra.video_id," ",a.video_id," ",b.video_id)
                return videoExtra.video_id == a.video_id
              }))
              let date1=catalogExtra.filter(videoExtra=>videoExtra.video_id == a.video_id)[0]["created"];
              let date2=catalogExtra.filter(videoExtra=>videoExtra.video_id == b.video_id)[0]["created"];
              
              if(date1 >date2){
                return 1;
              }else if(date2 > date1){
                return -1;
              }else{
                return 0;
              }
            }
          )
   
       }else if(listfilters[6]=="videolength"){
          catalogfiltered = catalogfiltered.sort(
              function(a,b){
                if(a.duration > b.duration){
                  return 1;
                }else if(a.duration < b.duration){
                  return -1;
                }else{
                  return 0;
                }
              }



          )

       }else if(listfilters[6]=="deflength"){
        catalogfiltered = catalogfiltered.sort(
          function(a,b){
            let start1=catalogExtra.filter(videoExtra=>videoExtra.video_id == a.video_id)[0]["concept_starttime"];
            let end1=catalogExtra.filter(videoExtra=>videoExtra.video_id == a.video_id)[0]["concept_endtime"];
            console.log("deflengtha: ",catalogExtra," ",a, " ",catalogExtra.filter(videoExtra=>videoExtra.video_id == a.video_id)," ",end1)
           
            let duration1 = ComputeDuration(end1,start1)
            console.log("deflengthb: ",catalogExtra," ",b)
            console.log(catalogExtra.filter(videoExtra=>videoExtra.video_id == b.video_id))
            let start2=catalogExtra.filter(videoExtra=>videoExtra.video_id == b.video_id)[0]["concept_starttime"];
            let end2=catalogExtra.filter(videoExtra=>videoExtra.video_id == b.video_id)[0]["concept_endtime"];
            
            let duration2 = ComputeDuration(end2,start2)
            if(duration1 >duration2){
              return 1;
            }else if(duration2 > duration1){
              return -1;
            }else{
              return 0;
            }
          }
        )
   
       }else if(listfilters[6]=="detailedlength"){
        catalogfiltered = catalogfiltered.sort(
          function(a,b){
            let start1=catalogExtra.filter(videoExtra=>videoExtra.video_id == a.video_id)[0]["derivatedconcept_starttime"];
            let end1=catalogExtra.filter(videoExtra=>videoExtra.video_id == a.video_id)[0]["derivatedconcept_endtime"];
            let duration1 = ComputeDuration(end1,start1)

            let start2=catalogExtra.filter(videoExtra=>videoExtra.video_id == b.video_id)[0]["derivatedconcept_starttime"];
            let end2=catalogExtra.filter(videoExtra=>videoExtra.video_id == b.video_id)[0]["derivatedconcept_endtime"];
            let duration2 = ComputeDuration(end2,start2)
            if(duration1 >duration2){
              return 1;
            }else if(duration2 > duration1){
              return -1;
            }else{
              return 0;
            }
          }
        )
     
       }

       setCatalog(catalogfiltered)


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
        console.log("risposta: ",risposta)
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