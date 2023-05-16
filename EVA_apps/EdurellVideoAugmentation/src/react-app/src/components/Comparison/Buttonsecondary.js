import * as React from 'react';
import { styled, withTheme } from "@material-ui/core/styles"
import Button from '@mui/material/Button';
import './buttonsecondary.css';


const SecondaryColor = styled(withTheme(Button))({
      
  
      background: "#FA824C",
      '&:hover': {
      backgroundColor: "#FB9B6F",
    },
  });

export default function Buttonsecondary({AddQueryElement, cs}){
    return <SecondaryColor variant="contained" className="buttonSize" onClick={() => {
      console.log("SearchButton: ",cs);
      AddQueryElement(cs);
      
    }}><b>Compare</b></SecondaryColor>
}