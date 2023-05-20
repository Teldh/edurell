// install (please try to align the version of installed @nivo packages)
// yarn add @nivo/bar

import React from "react";
import{
    Chart as ChartJS,
    BarElement,
    CategoryScale,
    LinearScale,
    Tooltip,
    Legend
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
    BarElement,
    CategoryScale,
    LinearScale,
    Tooltip,
    Legend
)

export default function Barro({catalog, catalogExtra}){
    
    const data = {
        labels: ['lun','mar','mer'],
        datasets:[
            {
                label:'video intero',
                data:catalog.map(video=>video.duration),
                backgroundColor:'aqua',
                borderColor: 'black',
                borderWidth: 1,
            },
            {
                label:'definizione',
                data:catalogExtra.map(video=>video.conceptLength),
                backgroundColor:'green',
                borderColor: 'black',
                borderWidth: 1,
            },
            {
                label:'approfondimento',
                data: catalogExtra.map(video=>video.derivatedLength),
                backgroundColor:'red',
                borderColor: 'black',
                borderWidth: 1,
            },
        ]
    }

    const options ={

    }
    return(<>
    
        <Bar
        style={{width:"10px",height:"50px"}}
        data={data}
        options={options}
        >


        </Bar>
    
    
    
    </>);
}