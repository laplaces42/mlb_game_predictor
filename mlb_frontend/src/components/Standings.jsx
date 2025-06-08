import React from 'react';
import StandingsPanel from './StandingsPanel';

function Standings() {
    return (
        <div className="standings">
            <div className="standings-container">
                <h2>Standings</h2>
                {/* Placeholder for standings data */}
                <p>Standings will be displayed here.</p>
                <div className='al-standings'>
                    <StandingsPanel division="AL East" />
                    <StandingsPanel division="AL Central" />
                    <StandingsPanel division="AL West" />
                </div>
                <div className='nl-standings'>
                    <StandingsPanel division="NL East" />
                    <StandingsPanel division="NL Central" />
                    <StandingsPanel division="NL West" />
                </div>
            </div>

        </div>
    )
}

export default Standings;