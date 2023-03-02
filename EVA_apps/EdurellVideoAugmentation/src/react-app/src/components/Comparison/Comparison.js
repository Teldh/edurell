import Header from '../Header/Header';
import React from 'react';
import { useContext } from 'react';
import {TokenContext} from '../account-management/TokenContext';
import Querybar from './Querybar.js';
import Listvideo from './Listvideo.js';

export default function Comparison(){

    const contextType = useContext(TokenContext);
    const nameSurname  = contextType.nameSurname;
    
    return(
        <>
        <Header page="dashboard" login={nameSurname}/>
        <Querybar/>
        <br/>
        <Listvideo/>
        </>
    );
}

