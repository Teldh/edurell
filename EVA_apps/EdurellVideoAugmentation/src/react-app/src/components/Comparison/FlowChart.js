import React, { useCallback,useState ,useEffect,useRef  } from 'react';
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
  const [direction, setDirection] = useState("DOWN")
    console.log("FLOWCHART", idx)
    const colorPick=[
      "red",
      "blue",
      "purple",
      "green"
  ]
  const nodeColor = (node) => {
    switch (node.type) {
      case 'input':
        return '#6ede87';
      case 'output':
        return '#6865A5';
      default:
        return '#ff0072';
    }

    
  };

  const elk = new ELK();
    const elkLayout = (nodes,edges,dir) => {
      console.log("elklayout dir: ",dir)
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
          console.log("BEFORE DOWN: ",node)
          node.targetPosition="top";
          node.sourcePosition="bottom";
          console.log("AFTER DOWN: ",node)
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
         "nodePlacement.strategy": "SIMPLE"
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
                style:{backgroundColor:"white", borderColor:graphcontrol=="three"?"grey":colorPick[idx], borderWidth:"2px",fontWeight:"bold"}
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
                style:{backgroundColor:"white", borderColor:graphcontrol=="two"?"grey":colorPick[idx],borderStyle:"dashed", borderWidth:"2px",fontWeight:"bold"}
            }];
            postnodesnote=[...postnodesnote,conceptExtra["list_postnotes"][i]]
        }    
    }

    initialNodes=[...initialNodes, {
        id:"conceptSelected",
        data:{label:concept},
        position,
        style:{backgroundColor:graphcontrol=="two"||graphcontrol=="three"?"grey":colorPick[idx], color:"white", borderColor:colorPick[idx], fontWeight:"bold"}
    }]

    for(let i=0; i<prenodes.length; i++){
        initialEdges=[...initialEdges,{
            id:(flowidx++).toString(),
            //id:prenodes[i].id+"_to_conceptSelected",
            source:prenodes[i].id,
            target:"conceptSelected",
            markerEnd:{
                type: MarkerType.ArrowClosed,
                
            },
            style: {
              strokeWidth: prenodesnote[i]=="strongPrerequisite"?5:1
            }
        }]
    }

    for(let i=0; i<postnodes.length; i++){
        initialEdges=[...initialEdges,{
            id:(flowidx++).toString(),
            //id:"conceptSelected_to_"+postnodes[i].id,
            source:"conceptSelected",
            target:postnodes[i].id,
            markerEnd:{
                type: MarkerType.ArrowClosed,

            },
            style:{
              strokeWidth: postnodesnote[i]=="strongPrerequisite"?5:1
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
      console.log("elklayout first call ",idx)
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

    useEffect(() => {
      console.log("CALLING FITVIEW")
      reactFlowInstance.fitView();
    });
    

    const onLayout = 
      (nodes,edges,direction) => {
        elkLayout(nodes,edges,direction).then((graph) => {
          console.log("elklayout second call ",idx)
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
      <MiniMap nodeColor={nodeColor} nodeStrokeWidth={3} zoomable pannable />
      <Panel position="top-right">
      
        <button onClick={() => {onLayout(nodes,edges,'DOWN')}}>vertical layout</button>
        <button onClick={() => {onLayout(nodes,edges,'RIGHT')}}>horizontal layout</button>
      </Panel>
    </ReactFlow>
    </>
  );
};


export default LayoutFlow;
