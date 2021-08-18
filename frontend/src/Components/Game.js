import React from "react";
import Board from "./Board";
import App from "./App";
import VideoCapture from "./VideoCapture";

class Game extends React.Component {

    constructor(){
        super();
        this.state = {
            'position' : 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
            'pgn' : '',
            'moveCount': 0,
        }
    }

    updatePosition = (newPosition) => {
        this.setState({'position': newPosition});
    }

    addMove = (move) => {
        if(this.state.moveCount % 2 == 0){
            this.setState({'pgn': this.state.pgn + '\n'});
        }
        if(this.state.moveCount % 2 == 0){
            this.setState({'pgn': this.state.pgn + `${this.state.moveCount/2 + 1}. `});
        }
        console.log(this.state.moveCount);

        this.setState({'pgn': this.state.pgn + move+' '});
        this.setState({'moveCount': this.state.moveCount+1});
    }

    render() {
      return (
        <div className = "container">
            <div className = 'header'></div>
            <div  className = 'chessboardContainer'>
                <h2> Current Position</h2>
                <Board curPosition={this.state.position}/>
                <h3> Moves</h3>
                <p> {this.state.pgn}</p>
                <h3> FEN </h3>
                <p className = "FEN">{this.state.position}</p>
            </div>
            <App/>

            <div className = "webcamContainer">
                <h2>Webcam View</h2>
                <VideoCapture updatePosition = {this.updatePosition} addMove = {this.addMove}/>
            </div>
        </div>
      );
    }
}

export default Game;