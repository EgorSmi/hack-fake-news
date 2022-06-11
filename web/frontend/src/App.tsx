import React from 'react';
import {Card} from '@mui/material';

import './App.css';
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
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
