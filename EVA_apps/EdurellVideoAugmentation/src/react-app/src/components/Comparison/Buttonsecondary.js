import * as React from 'react';
import { styled, withTheme } from "@material-ui/core/styles"
import Button from '@mui/material/Button';



const SecondaryColor = styled(withTheme(Button))({
      
  
      background: "#FA824C",
      '&:hover': {
      backgroundColor: "#FB9B6F",
    },
  });

export default function Buttonsecondary(){
    return <SecondaryColor variant="contained" size="large" ><b>Compare</b></SecondaryColor>
}