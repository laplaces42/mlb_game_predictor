function Header() {
    return (
        <div className="header">
            <h2>MLB Game Tracker</h2>
            <nav>
                <ul>
                    <li><a href="/">Home</a></li>
                    <li><a href="/standings">Standings</a></li>
                    <li><a href="/teams">Teams</a></li>
                    <li><a href="/model-info">Model Info</a></li>
                </ul>
            </nav>

        </div>
    )
}

export default Header;