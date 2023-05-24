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

export default function Barro({catalog, catalogExtra, graphcontrol}){
    
    const data = {
        labels: catalogExtra.map(video=>(video.video_slidishness*100).toString()+"%"),
        datasets:[
            {
                label:'video intero',
                data:catalog.map(video=>video.duration),
                backgroundColor:"white",
                borderColor: graphcontrol=="two"?"grey":[
                    "#FF4545",
                    "#3E7FFF",
                    "#CE3FFF",
                    "#71D89A"
                ],
                borderWidth: 5,
                grouped:false,
                order:10,
            },
            {
                label:'slide',
                data:catalogExtra.map(video=>video.video_slidishness*catalog.filter(cat=>cat.video_id == video.video_id)[0].duration),
                backgroundColor:graphcontrol=="three"?"grey":[
                    "#FF4545",
                    "#3E7FFF",
                    "#CE3FFF",
                    "#71D89A"
                ],
                categoryPercentage:0.7,
            },
       
        ]
    }

    const options ={
       scales:{
        x:{
            display:true
        }
       },
        responsive: true, // Abilita la risposta al ridimensionamento
        maintainAspectRatio: false, // Disabilita il mantenimento dell'aspect ratio
        // Imposta le dimensioni desiderate
        width: 400,
        height: 300,
        layout: {
            padding:{
                top:50,
                left:20,
                right:20
            } 
        },
        plugins: {  // 'legend' now within object 'plugins {}'
            legend: {
                display: false,
            },
           
          },
          
    }
    return(<>
    
        <Bar
  
        data={data}
        options={options}
        >


        </Bar>
    
    
    
    </>);
}