import React from "react";
import Webcam from "react-webcam";

const VideoCapture = function(props){
    const webcamRef = React.useRef(null);
    const [result, setResult] = React.useState({'message': 'Press Calibrate on an empty board'});
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

export default VideoCapture;