import React, { useCallback,useState ,useEffect } from 'react';
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
  useReactFlow 
} from 'reactflow';
import dagre from 'dagre';



import 'reactflow/dist/style.css';

const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

const nodeWidth = 172;
const nodeHeight = 36;

const getLayoutedElements = (nodes, edges, direction = 'TB') => {
  const isHorizontal = direction === 'LR';
  dagreGraph.setGraph({ rankdir: direction });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });

  edges.forEach((edge) => {
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

  return { nodes, edges };
};

const LayoutFlow = ({concept, conceptExtra, idx, graphcontrol}) => {
    console.log("GRAPH CONTROL: ",graphcontrol)
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
                id:flowidx++,
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
                id:flowidx++,
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
            id:flowidx++,
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
            id:flowidx++,
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

    initialNodes=[...initialNodes,...prenodes,...postnodes]


    const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
    initialNodes,
    initialEdges
    );

  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState(initialEdges);

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
  


  return (

    <ReactFlow
      nodes={nodes}
      edges={edges}
      id={idx}
      fitView
    >
        <MiniMap nodeColor={nodeColor} nodeStrokeWidth={3} zoomable pannable />
        <Background color="black"  variant="cross"/>
        <Controls />
      <Panel position="top-right">
        <button onClick={() => onLayout('TB')}>vertical layout</button>
        <button onClick={() => onLayout('LR')}>horizontal layout</button>
      </Panel>
    </ReactFlow>

  );
};

export default LayoutFlow;
