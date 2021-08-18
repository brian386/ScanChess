import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import reportWebVitals from './reportWebVitals';
import Chessboard from "chessboardjsx";
import Webcam from 'react-webcam';
import './App.css'
import banner from './images/banner.jpg'
const axios = require('axios');
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

const VideoCapture = function(props){
    const webcamRef = React.useRef(null);
    const [result, setResult] = React.useState({});
    const [mode, setMode] = React.useState('CALIBRATE');
    const [promotionPiece, setPromotionPiece] = React.useState('q');
    const [gameStatus, setGameStatus] = React.useState('');
    const calibration_capture = React.useCallback(
        async ()=>{
            const imageSrc = webcamRef.current.getScreenshot({width: 800, height: 600});
            setResult({'status': 'WAIT', 'message': 'Loading....'});
            //FETCH POSTING TO FLASK
            //console.log(imageSrc);
            const formData = new FormData()
            formData.append('image', imageSrc)
            const response = await fetch('/calibrate', {
                method: "POST",
                mode: 'no-cors',
                body: JSON.stringify({data: imageSrc}),
                datatype: 'json',
                headers:{
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
            });

            if(response.status === 200) {

                const text = await response.json();
                setResult(text);
                if(text['status'] == 'CALIBRATION_COMPLETE'){
                    setMode("MOVE");
                }
                console.log(text);
            }else {
                setResult("Error from api");
            }

        },
        [webcamRef]
    );
    const move_capture = React.useCallback(
        async ()=>{
            const imageSrc = webcamRef.current.getScreenshot({width: 800, height: 600});
            setResult({'status': 'WAIT', 'message': 'Loading....'});
            //FETCH POSTING TO FLASK
            //console.log(imageSrc);
            const response = await fetch('/make_move', {
                method: "POST",
                mode: 'no-cors',
                body: JSON.stringify({data: imageSrc, promotionPiece: promotionPiece}),
                datatype: 'json',
                headers:{
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
            });

            if(response.status === 200) {
                const text = await response.json();
                setResult(text);
                //check win
                if(text['game_result'] == 'WHITE_WIN'){
                    setGameStatus('White won');
                } else if(text['game_result'] == 'BLACK_WIN'){
                    setGameStatus('Black won')
                } else if (text['game_result'] == 'DRAW'){
                    setGameStatus('game was a draw')
                }
                if(text['status'] != 'ERR') {
                    props.updatePosition(text['position']);
                    props.addMove(text['move']);
                }
                console.log(text);
            }else {
                setResult("Error from api");
            }
        },
        [webcamRef]
    );

    let curButton;
    if(mode == 'CALIBRATE'){
        curButton = <button
            className = "button"
            id = "calibrateButton"
            onClick = {calibration_capture}
        >
            Calibrate
        </button>
    } else{
        curButton = <button
            className = "button"
            id = "moveButton"
            onClick = {move_capture}
        >
            Confirm Move
        </button>
    }
    return(
        <div>
            <div className = 'webcam'>
                <Webcam ref = {webcamRef} screenshotFormat = "image/jpeg" width = {500}/>
            </div>
            {curButton}
            <p>{result['message']}</p>
            <p>{gameStatus}</p>
            {console.log(JSON.stringify(result))}
        </div>
    )
}

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
                <h5> {this.state.pgn}</h5>
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


// ========================================

ReactDOM.render(
  <Game/>,
  document.getElementById('root')
);


// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
