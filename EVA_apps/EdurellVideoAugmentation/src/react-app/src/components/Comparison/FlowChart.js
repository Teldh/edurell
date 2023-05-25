import React, { useCallback,useState ,useEffect,useRef  } from 'react';
import './FlowChart.css';
import ReactFlow, {
  addEdge,
  ConnectionLineType,
  Panel,
  useNodesState,
  useEdgesState,
  Background, 
  MarkerType,
  MiniMap,
  Controls,
  ReactFlowProvider,
  useReactFlow ,
  ControlButton,

} from 'reactflow';
import dagre from 'dagre';
import ELK from "elkjs";



import 'reactflow/dist/style.css';

/*
const dagreGraph = new dagre.graphlib.Graph({directed:true,compound:true, multigraph:true});
dagreGraph.setDefaultEdgeLabel(() => ({}));

const nodeWidth = 172;
const nodeHeight = 36;

const getLayoutedElements = (nodes, edges, direction = 'TB') => {
  const isHorizontal = direction === 'LR';
  dagreGraph.setGraph({ rankdir: direction , align: "DL"});

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });

  edges.forEach((edge,idx) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);
  
  nodes.forEach((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    node.targetPosition = isHorizontal ? 'left' : 'top';
    node.sourcePosition = isHorizontal ? 'right' : 'bottom';

    // We are shifting the dagre node position (anchor=center center) to the top left
    // so it matches the React Flow node anchor point (top left).
    
    node.position = {
      x: nodeWithPosition.x - nodeWidth / 2,
      y: nodeWithPosition.y - nodeHeight / 2,
    };

    return node;
  });
  console.log("CREANDO NODO: ",dagre.graphlib.json.write(dagreGraph))
  return { nodes, edges };
};

*/

const LayoutFlow = ({concept, conceptExtra, idx, graphcontrol}) => {
  const reactFlowInstance = useReactFlow();
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [direction, setDirection] = useState("DOWN");
 
    const colorPick=[
      "#FF4545",
      "#3E7FFF",
      "#CE3FFF",
      "#71D89A",

      "#ff7878",
      "#9dbdfc",
      "#e08dfc",
      "#a4f5c4"
  ]
  const nodeColor = (node) => {
    if(idx == 0){
      switch (node.type) {
        case 'input':
          return '#FFFFFF';
        case 'output':
          return '#FFFFFF';
        default:
          return '#FF4545';
      }
    }else if(idx == 1){
      switch (node.type) {
        case 'input':
          return '#FFFFFF';
        case 'output':
          return '#FFFFFF';
        default:
          return '#3E7FFF';
      }
    }else if(idx == 2){
      switch (node.type) {
        case 'input':
          return '#FFFFFF';
        case 'output':
          return '#FFFFFF';
        default:
          return '#CE3FFF';
      }
    }else if(idx == 3){
      switch (node.type) {
        case 'input':
          return '#FFFFFF';
        case 'output':
          return '#FFFFFF';
        default:
          return '#71D89A';
      }
    }else{
      switch (node.type) {
        case 'input':
          return '#6ede87';
        case 'output':
          return '#6865A5';
        default:
          return '#ff0072';
      }
    }
    
  };

  

  const nodeStrokeColor = (node) => {
    if(idx == 0){

      if(node.type=="output"){
        return "#ff7878";
      }else{
        return '#FF4545';
      }
          
    
    }else if(idx == 1){
      if(node.type=="output"){
        return "#9dbdfc";
      }else{
        return '#3E7FFF';
      }
          
      
    }else if(idx == 2){
      if(node.type=="output"){
        return "#e08dfc";
      }else{
        return '#CE3FFF';
      }
          
      
    }else if(idx == 3){
      if(node.type=="output"){
        return "#a4f5c4";
      }else{
        return '#71D89A';
      }
          
      
    }else{
      switch (node.type) {
        case 'input':
          return '#6ede87';
        case 'output':
          return '#6865A5';
        default:
          return '#ff0072';
      }
    }
  
  };

  const elk = new ELK();
    const elkLayout = (nodes,edges,dir) => {
 
     const nodesForElk = nodes.map((node) => {
   
      switch(dir){
       
        case "LEFT":
          node.targetPosition="right";
          node.sourcePosition="left";
          break;
        case "RIGHT":
          node.targetPosition="left";
          node.sourcePosition="right";
          break;
        case "UP":
          node.targetPosition="bottom";
          node.sourcePosition="top";
          break;
        case "DOWN":
          node.targetPosition="top";
          node.sourcePosition="bottom";
          break;
      }
        
       return {
         id: node.id,
         width: 172,
         height: 36
       };
     });
     const graph = {
       id: "root",
       layoutOptions: {
         "elk.algorithm": "layered",
         "elk.direction": dir,
         "nodePlacement.strategy": "SIMPLE",
         "spacing.nodeNodeBetweenLayers":100,
       },
    
       children: nodesForElk,
       edges: edges
     };
     return elk.layout(graph);
    };

  useEffect(()=>{

    const position = { x: 0, y: 0 };

    let prenodes = []
    let prenodesnote=[]

    let initialNodes=[]

    let postnodes=[]
    let postnodesnote=[]

    let initialEdges=[]
    let flowidx=0

    if(conceptExtra["list_preconcept"].length > 0){
        for(let i=0; i<conceptExtra["list_preconcept"].length; i++){
            prenodes=[...prenodes,{
                id:(flowidx++).toString(),
                //id:conceptExtra["list_preconcept"][i],
                type:'input',
                data:{label:conceptExtra["list_preconcept"][i]},
                position,
                style:{backgroundColor:"white", borderColor:graphcontrol=="three"?"grey":colorPick[idx], borderWidth:"5px",fontWeight:"bold"}
            }];
            prenodesnote=[...prenodesnote,conceptExtra["list_prenotes"][i]]
        }
    }

    if(conceptExtra["list_derivatedconcept"].length>0){
        for(let i=0; i<conceptExtra["list_derivatedconcept"].length; i++){
            postnodes=[...postnodes,{
                id:(flowidx++).toString(),
                //id:conceptExtra["list_derivatedconcept"][i],
                type:'output',
                data:{label:conceptExtra["list_derivatedconcept"][i]},
                position,
                style:{backgroundColor:"white", borderColor:graphcontrol=="two"?"grey":colorPick[idx+4], borderWidth:"5px",fontWeight:"bold"}
            }];
            postnodesnote=[...postnodesnote,conceptExtra["list_postnotes"][i]]
        }    
    }

    initialNodes=[...initialNodes, {
        id:"conceptSelected",
        data:{label:concept},
        position,
        style:{backgroundColor:graphcontrol=="two"||graphcontrol=="three"?"grey":colorPick[idx], color:"white", borderColor:graphcontrol=="two"||graphcontrol=="three"?"grey":colorPick[idx], fontWeight:"bold"}
    }]

    for(let i=0; i<prenodes.length; i++){
        initialEdges=[...initialEdges,{
            id:(flowidx++).toString(),
            //id:prenodes[i].id+"_to_conceptSelected",
            source:prenodes[i].id,
            target:"conceptSelected",
            type: 'smoothstep',
            markerEnd:{
                type: MarkerType.Arrow,
                
            },
            style: {
              strokeWidth: prenodesnote[i]=="strongPrerequisite"?3:1
            }
        }]
    }

    for(let i=0; i<postnodes.length; i++){
        initialEdges=[...initialEdges,{
            id:(flowidx++).toString(),
            //id:"conceptSelected_to_"+postnodes[i].id,
            source:"conceptSelected",
            target:postnodes[i].id,
            type: 'smoothstep',
            markerEnd:{
                type: MarkerType.Arrow,

            },
            style:{
              strokeWidth: postnodesnote[i]=="strongPrerequisite"?3:1
            }
        }]
    }

    initialNodes=[...prenodes,...initialNodes,...postnodes]

    /*

    const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
    initialNodes,
    initialEdges,
    );
    */

 
    
    


    elkLayout(initialNodes,initialEdges,direction).then((graph) => {
   
      setNodes(nodesForFlow(graph,initialNodes));
      setEdges(edgesForFlow(graph));
    });

  },[]);


    const nodesForFlow = (graph, initialNodes) => {
      return [
        ...graph.children.map((node) => {
          
          return {
            ...initialNodes.find((n) => n.id === node.id),
            position: { x: node.x, y: node.y }
          };
        })
      ];
    };
    const edgesForFlow = (graph) => {
      return graph.edges;
    };

   

    useEffect(()=>{
      reactFlowInstance.fitView();
    })
    
    useEffect(()=>{
  
      if(nodes!=undefined){
      
        let newnode = nodes.map(node=>{
          
          if(node.type == "input"){
            node.style={backgroundColor:"white", borderColor:graphcontrol=="three"?"grey":colorPick[idx], borderWidth:"5px",fontWeight:"bold"}
          }else if(node.type == "output"){
            node.style={backgroundColor:"white", borderColor:graphcontrol=="two"?"grey":colorPick[idx+4], borderWidth:"5px",fontWeight:"bold"}
          }else{
            node.style={backgroundColor:graphcontrol=="two"||graphcontrol=="three"?"grey":colorPick[idx], color:"white", borderColor:graphcontrol=="two"||graphcontrol=="three"?"grey":colorPick[idx], fontWeight:"bold"}
          }
          return node
        })
        
        setNodes([...newnode])
      }
     
    },[graphcontrol])

    const onLayout = 
      (nodes,edges,direction) => {
        elkLayout(nodes,edges,direction).then((graph) => {
  
          setNodes([...nodesForFlow(graph,nodes)]);
          setEdges([...edgesForFlow(graph)]);
        });
      }
    
  /*
  const onLayout = useCallback(
    (direction) => {
      const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
        nodes,
        edges,
        direction
      );

      setNodes([...layoutedNodes]);
      setEdges([...layoutedEdges]);
    },
    [nodes, edges]
  );
  <button onClick={() => onLayout('TB')}>vertical layout</button>
        <button onClick={() => onLayout('LR')}>horizontal layout</button>
*/

  return (
<>    <ReactFlow
      nodes={nodes}
      edges={edges}
      id={idx}
      fitView
    >
      <Controls />
      <MiniMap nodeColor={nodeColor} nodeStrokeColor={nodeStrokeColor} nodeStrokeWidth={10} zoomable pannable />
      <Panel position="top-right">
      
        <button onClick={() => {onLayout(nodes,edges,'DOWN')}}>vertical layout</button>
        <button onClick={() => {onLayout(nodes,edges,'RIGHT')}}>horizontal layout</button>
      </Panel>
    </ReactFlow>
    </>
  );
};


export default LayoutFlow;
