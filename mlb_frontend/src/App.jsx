import './App.css';
import React from 'react';
import Header from './components/Header';
import GameView from './components/GameView';
import Standings from './components/Standings';
import TeamView from './components/TeamView';
import ModelInfo from './components/ModelInfo';
import Footer from './components/Footer';

function App() {
  return (
    <div className="App">
      <Header />
      <GameView />
      <Standings />
      <TeamView />
      <ModelInfo />
      <Footer />
    </div>
  );
}

export default App;
