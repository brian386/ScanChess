import logo from '../logo.svg';
import React, {useState,useEffect} from 'react'
import '../App.css';

function App() {
  const [data, setData] = useState([{}])
  useEffect(() => {
    fetch("/api").then(
        res => res.json()
    ).then(
        data => {
          setData(data)
        }
    )
  },[])

  return (
    <div>
      {console.log(JSON.stringify(data))}
    </div>
  );

}

export default App;
