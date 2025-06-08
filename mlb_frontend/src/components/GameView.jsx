import React from 'react';
import TodaysGames from './TodaysGames';
import RecentGames from './RecentGames';

function GameView() {
    return (
        <div className="game-view">
            <RecentGames />
            <TodaysGames />
        </div>
    )
}

export default GameView;