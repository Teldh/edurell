import React from "react"
import './Popup.css'

/**
 * React Component used in the GraphKnowledge component.
 * It shows a small pop-up that appear next to the user's pointer when he clicks on a node of the graph
 */
export default class Popup extends React.Component{

    channel = new BroadcastChannel('react-connect'); //create a boradcast channel

    render(){
        return(this.props.visible &&
            <div className="popup" style={{left: `${this.props.x}px`, top: `${this.props.y}px`, display: 'inline-block'}}>
                <text>
                    Concept : {this.props.conceptName} 
                </text>
                <br/><button onClick={()=>this.props.goToTimestamp(this.props.conceptTimeBegin)} > GoToConcept : {this.props.conceptTimeBegin}</button>
                <br/><button onClick={()=>this.channel.postMessage({to: 'App', msg: this.props.conceptName})} > Open detailed description </button>
            </div>)
    }
}
