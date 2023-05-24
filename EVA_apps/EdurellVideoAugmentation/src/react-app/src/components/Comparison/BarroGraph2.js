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
    function createDiagonalPattern(color = 'black') {
        // create a 10x10 px canvas for the pattern's base shape
        let shape = document.createElement('canvas')
        shape.width = 10
        shape.height = 10
        // get the context for drawing
        let c = shape.getContext('2d')
        c.lineWidth = 3;
        // draw 1st line of the shape 
        c.strokeStyle = color
        c.beginPath()
        c.moveTo(2, 0)
        c.lineTo(10, 8)
        c.stroke()
        // draw 2nd line of the shape 
        c.beginPath()
        c.moveTo(0, 8)
        c.lineTo(2, 10)
        c.stroke()
        // create the pattern from the shape
        return c.createPattern(shape, 'repeat')
      }
    const data = {
        labels: catalog.map(video=>video.title),
        datasets:[
            {
                label:'video intero',
                data:catalog.map(video=>video.duration),
                backgroundColor:"white",
                borderColor: graphcontrol=="two"?"grey":["red","blue","purple","green"],
                borderWidth: 5,
                grouped:false,
                order:10,
            },
            {
                label:'slide',
                data:catalogExtra.map(video=>video.video_slidishness*catalog.filter(cat=>cat.video_id == video.video_id)[0].duration),
                backgroundColor:graphcontrol=="three"?"grey":["red","blue","purple","green"],
                categoryPercentage:0.7,
            },
       
        ]
    }

    const options ={
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
            }
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