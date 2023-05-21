import React, { useCallback,useState } from 'react';
import ReactFlow, {
  addEdge,
  ConnectionLineType,
  Panel,
  useNodesState,
  useEdgesState,
  Background, 
  MarkerType 
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

    
    const position = { x: 0, y: 0 };

    let prenodes = []
    let initialNodes=[]
    let postnodes=[]
    let initialEdges=[]
    let flowidx=0

    if(conceptExtra["list_preconcept"].length > 0){
        for(let i=0; i<conceptExtra["list_preconcept"].length; i++){
            prenodes=[...prenodes,{
                id:flowidx++,
                type:'input',
                data:{label:conceptExtra["list_preconcept"][i]},
                position,
            }]
        }
    }

    if(conceptExtra["list_derivatedconcept"].length>0){
        for(let i=0; i<conceptExtra["list_derivatedconcept"].length; i++){
            dernodes=[...dernodes,{
                id:flowidx++,
                type:'output',
                data:{label:conceptExtra["list_derivatedconcept"][i]},
                position,
            }]
        }    
    }

    initialNodes=[...initialNodes, {
        id:"conceptSelected",
        data:{label:concept},
        position,
    }]

    for(let i=0; i<prenodes.length; i++){
        initialEdges=[...initialEdges,{
            id:flowidx++,
            source:prenodes[i].id,
            target:"conceptSelected",
            markerEnd:{
                type: MarkerType.Arrow,
            }
        }]
    }

    for(let i=0; i<postnodes.length; i++){
        initialEdges=[...initialEdges,{
            id:flowidx++,
            source:"conceptSelected",
            target:postnodes[i].id,
            markerEnd:{
                type: MarkerType.Arrow,
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

      fitView
    >
      <Panel position="top-right">
        <button onClick={() => onLayout('TB')}>vertical layout</button>
        <button onClick={() => onLayout('LR')}>horizontal layout</button>
      </Panel>
    </ReactFlow>
  );
};

export default LayoutFlow;
