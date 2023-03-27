import {
    Link,
} from "react-router-dom";
export default function ButtonComp(){
    return (
        <div>
            <button>
                <Link to={`/comparison`}>Comparison</Link>
            </button>
        </div>
    );
}