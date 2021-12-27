import Graph from "react-graph-vis";
import React from "react";


/**
 * Graph displayed by the Concept Component, it's a subgraph of the video graph (see GraphKnowledge component) focused on one concept
 */
export default class SubGraph extends React.Component {
  
    constructor(props){
      super(props);
      this.options={
        edges: {
              color: "#000000",
              smooth: true
            },
        nodes:{
          shape: "dot",
          size: 10,
          opacity: 0.9,
          mass:0.9
        },
        layout: { 
          randomSeed: 50, //fixed seed --> always the same nodes positions
          improvedLayout: true, 
          hierarchical: false, 
          clusterThreshold: 1000
      },
        physics: {
          stabilization: true,
          forceAtlas2Based: {
            avoidOverlap: 1,
            springLength: 200
          },
        },
        manipulation: {
          enabled: true
        },
        width: "650px",
        height: "400px",
      };
      
      this.state = {
        networkNodes: false,
        networkEdges: false,
        };

        try{}   catch{}
    }

    /**
     * function triggered when the concept change, and redraw the graph focused on the updated concept
     */
    componentDidUpdate = ()=> {
        try{this.state.networkEdges.clear();}   catch{}
        try{this.state.networkNodes.clear();}   catch{}
      var conceptObject = this.props.concept;

      if(conceptObject){
          let addedRels = []
          try{this.state.networkNodes.add({id: conceptObject.conceptName, label: conceptObject.conceptName, color: "#B85450", shadow:true ,font: {color : 'black' , face: 'monospace'} })
            }   catch{}

          for(const target of conceptObject.subgraph.targets){
            try{this.state.networkNodes.add({id: target.conceptName, label: target.conceptName, color: "#C0BAC0", shadow:true ,font: {color : 'black' , face: 'monospace'} })
            }   catch{}

            try{

              if (conceptObject.subgraph.relations.some(e => e.prerequisite === conceptObject.conceptName && e.target === target.conceptName)){
                
                let edge = {from: conceptObject.conceptName, to: target.conceptName}

                if(!addedRels.some(e => e.from === edge.from && e.to === edge.to)){
                  this.state.networkEdges.add({from: conceptObject.conceptName, to: target.conceptName})
                  addedRels.push({from: conceptObject.conceptName, to: target.conceptName})
                }

                
              }
                
            }   catch{}
          }
          
          this.addPrerequisiteTree(conceptObject, conceptObject.subgraph.relations, addedRels)
          try{this.state.networkNodes.update({id: conceptObject.conceptName, label: conceptObject.conceptName, color: "#B85450", shadow:true ,font: {color : 'black' , face: 'monospace'} })
            }   catch{}
      }
    }

    // recursive function used to draw the graph
    addPrerequisiteTree  = (conceptObject, relations, addedRels) => {

      for(const prerequisite of conceptObject.subgraph.prerequisites){
        try{this.state.networkNodes.add({id: prerequisite.conceptName, label: prerequisite.conceptName, color: "#E0B7DF", shadow:true, font: {color : 'black' , face: 'monospace'} })
        }   catch{}
        try{
          if (relations.some(e => e.prerequisite === prerequisite.conceptName && e.target === conceptObject.conceptName)){

              let edge = {from: prerequisite.conceptName, to: conceptObject.conceptName}

              console.log(addedRels)
              if(!addedRels.some(e => e.from === edge.from && e.to === edge.to)){
                this.state.networkEdges.add({from: prerequisite.conceptName, to: conceptObject.conceptName})
                addedRels.push({from: prerequisite.conceptName, to: conceptObject.conceptName})
              }

          }
            
        }   catch{}
        this.addPrerequisiteTree(prerequisite, relations, addedRels)
      }
      if(!conceptObject.subgraph.prerequisites.length){
        try{this.state.networkNodes.update({id: conceptObject.conceptName, label: conceptObject.conceptName, color: "#A9ACEA", shadow:true, font: {color : 'black' , face: 'monospace'} })
        }   catch{}
      }
    }
      
    //convert from format 'HH:MM:SS' to seconds
    convertTimeInSeconds = (time)=>{
      var a = time.split(':'); // split it at the colons
      // minutes are worth 60 seconds. Hours are worth 60 minutes.
      return (+a[0]) * 60 * 60 + (+a[1]) * 60 + (+a[2]);
    }
  
    render(){
      return (
          <Graph
            getNodes = {nodes => {this.setState({networkNodes: nodes})} }
            getEdges = {edges => {this.setState({networkEdges: edges})} }
            graph={{
                nodes: [],
                edges: []
              }}
            options={this.options}
            />
        )
    }
  }