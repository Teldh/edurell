import React from 'react';
import Container from '@mui/material/Container'
import '../Header/Header.css';
import './Comparison.css';
import { TextField } from '@material-ui/core';
import Stack from '@mui/material/Stack';
import './Queryinput.css';
import Typography from '@mui/material/Typography';
import InputAdornment from '@mui/material/InputAdornment'
import SearchRoundedIcon from '@mui/icons-material/SearchRounded';
import Header from '../Header/Header';
import { useContext,useState,useEffect } from 'react';
import {TokenContext} from '../account-management/TokenContext';
import handleFetchHttpErrors from '../../helpers/handleFetchHttpErrors';
import {
  Link,
  Redirect,
  Switch, 
  Route
} from "react-router-dom";
import Autocomplete from '@mui/material/Autocomplete';
import Popper from '@mui/material/Popper';
import { useHistory } from "react-router-dom";
import Box from '@mui/material/Box';

export default function C_Start({Endcstart}){
    const context = useContext(TokenContext);
    const nameSurname  = context.nameSurname;
    const [loading,setLoading]=useState(true);
    const [catalog,setCatalog]=useState(null);
    const [listConcepts, setListConcepts]=useState([]);
    const history = useHistory();

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


    function SendData(value){
        console.log("historypush: ",value);
        history.push({
            pathname: '/comparisonSearch',
            state: { data: value },
        });
    }

    return (
        <>
        <Header page="dashboard" login={nameSurname}/>
        
        
        <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
      }}
      className="bgcolordiv"
    >
   
            <Stack spacing={1} sx={{justifyContent:'center', alignItems:'center'}}>
                <Typography variant="h1" 
                    gutterBottom  
                    className="logofirstpage"
                    style={{
                        align:'center',
                        fontWeight: 'bold',
                        margin: '0'
                    }}>
                        Edurell
                </Typography>
        
                <Autocomplete
                
                    id="free-solo-demo"
                    freeSolo
                    options={listConcepts}

                    renderInput={(params) => 
                        <TextField {...params}
                        style={{width: '700px'}}
                        
                        className="backColor" 
                        variant="outlined" 
                        PopperComponent={(props) => (
                            <Popper {...props} placement="bottom" />
                          )}
                        placeholder="Cerca i concetti che vuoi approfondire" 
                        InputProps={{
                            ...params.InputProps,
                             type: 'search',
                            startAdornment: (
                                <InputAdornment position="start">
                                    <SearchRoundedIcon sx={{color:"rgb(255,128,0)"}}/>
                                </InputAdornment>
                            )
                        }}
                       
                        />
                    }
                    onChange={(event, value) => {
                        SendData(value);
                      }}
                />
                
            </Stack>
            
     
          
          
          
              
      </Box>



        </>
    );
}