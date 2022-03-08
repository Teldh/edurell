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
                { this.props.conceptList && this.props.conceptList.map((value, id) => 
                <ul className="ul-popup">
                    <li className="popup-li">
                        Concept: <span className="text-concept-popup">{value}</span> 
                    </li>
                    <div className="row">
                        <button className="popup-button" onClick={()=>this.props.goToTimestamp(this.props.conceptTimeBeginList[id])} > GoToConcept : {this.props.conceptTimeBeginList[id]}</button>
                    </div>
                    <div className="row">
                        <button className="popup-button" onClick={()=>this.channel.postMessage({to: 'App', msg: this.props.conceptList[id]})} > Open detailed description </button>
                    </div>
                </ul>) 
                }
            </div>
        )
    }
}
