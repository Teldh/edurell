// install (please try to align the version of installed @nivo packages)
// yarn add @nivo/bar

import React from "react";
import pattern from 'patternomaly';
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
                borderColor: graphcontrol=="two"||graphcontrol=="three"?"grey":[
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
                label:'definizione',
                data:catalogExtra.map(video=>video.conceptLength),
                backgroundColor:graphcontrol=="three" || graphcontrol=="four"?"grey":[
                    "#FF4545",
                    "#3E7FFF",
                    "#CE3FFF",
                    "#71D89A"
                ],
                order:1,
                categoryPercentage:0.7,

            },
            {
                label:'approfondimento',
                data: catalogExtra.map(video=>video.derivatedLength),
                backgroundColor:
                    graphcontrol=="two"||graphcontrol =="four"?createDiagonalPattern('grey'):
                    [pattern.draw('diagonal-right-left', '#F2BABA'),
                    pattern.draw('diagonal-right-left', '#B8CBF2'),
                    pattern.draw('diagonal-right-left', '#E3B8F2'),
                    pattern.draw('diagonal-right-left', '#C7E6D3')],
                borderColor: graphcontrol=="two" || graphcontrol=="four"?"grey":[
                    "#FF4545",
                    "#3E7FFF",
                    "#CE3FFF",
                    "#71D89A"
                ],
                borderWidth: 5,
                order:1,
                categoryPercentage:0.7
                
            },
        ]
    }

    const options ={
       
        plugins: {  // 'legend' now within object 'plugins {}'
            legend: {
                display: false,
            }
          },
        
          layout: {
            padding:{
                top:50,
                left:20,
                right:20
            } 
        },
        responsive: true, // Abilita la risposta al ridimensionamento
        maintainAspectRatio: false, // Disabilita il mantenimento dell'aspect ratio
        // Imposta le dimensioni desiderate
        width: 400,
        height: 300
    }
    return(<>
    
        <Bar
  
        data={data}
        options={options}
        >


        </Bar>
    
    
    
    </>);
}