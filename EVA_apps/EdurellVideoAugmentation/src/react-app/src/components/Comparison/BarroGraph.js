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

export default function Barro(){
    const data = {
        labels: ['lun','mar','mer'],
        datasets:[
            {
                label:'369',
                data:[3,6,1],
                backgroundColor:'aqua',
                borderColor: 'black',
                borderWidth: 1,
            },
            {
                label:'"asd"',
                data:[1,2,3],
                backgroundColor:'green',
                borderColor: 'black',
                borderWidth: 1,
            },
        ]
    }

    const options ={

    }
    return(<>
    
        <Bar
        style={{width:"auto",height:"500px"}}
        data={data}
        options={options}
        >


        </Bar>
    
    
    
    </>);
}