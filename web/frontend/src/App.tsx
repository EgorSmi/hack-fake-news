import React from 'react';
import './App.css';
import FooterComponent from "./components/FooterComponent";
import {MainComponent} from "./components/MainComponent";


function App() {
    return (
        <div className="App">
            <MainComponent/>
            <FooterComponent/>
        </div>
    ); 
}

export default App;
