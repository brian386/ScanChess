import React from 'react';
import ReactDOM from 'react-dom';
import reportWebVitals from './reportWebVitals';
import Chessboard from "chessboardjsx";
import Webcam from 'react-webcam';
import './App.css'
import banner from './images/banner.jpg'

import App from './Components/App';
import Board from './Components/Board';
import VideoCapture from './Components/VideoCapture';
import Game from './Components/Game'

const axios = require('axios');



// ========================================

ReactDOM.render(
  <Game/>,
  document.getElementById('root')
);


// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
