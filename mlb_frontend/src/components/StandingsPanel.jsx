function StandingsPanel({ division }) {
  return (
    <div className="standings-panel">
      <h3>{division}</h3>
      <table className="standings-table">
        <thead>
          <tr>
            <th>Team</th>
            <th>Wins</th>
            <th>Losses</th>
            <th>Win %</th>
          </tr>
        </thead>
        <tbody>
          {/* {division.teams.map((team) => (
                        <tr key={team.name}>
                            <td>{team.name}</td>
                            <td>{team.wins}</td>
                            <td>{team.losses}</td>
                            <td>{(team.wins / (team.wins + team.losses)).toFixed(3)}</td>
                        </tr>
                    ))} */}
        </tbody>
      </table>
    </div>
  );
}

export default StandingsPanel;
