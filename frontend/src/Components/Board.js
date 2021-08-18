import React from "react";
import Chessboard from "chessboardjsx";

class Board extends React.Component{
    render(){
        return(
            <div className = 'chessboard'>
                <Chessboard
                    width ={700}
                    position={this.props.curPosition}
                />
            </div>

        )
    }
}

export default Board;