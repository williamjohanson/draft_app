import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import '../styles/DynastyLeague.css';  // Assuming the correct path to the CSS file

function DynastyLeague() {
    const [teams, setTeams] = useState([]);
    const [leagueInfo, setLeagueInfo] = useState({});
    const [error, setError] = useState(null);

    useEffect(() => {
        async function fetchLeagueData() {
            try {
                const response = await axios.get('/api/league/1048178119665889280/users');
                setTeams(response.data);
                setLeagueInfo({
                    name: "Choo Choo Train",  // You can dynamically fetch and set this too
                    status: "pre_draft"      // You can dynamically fetch and set this too
                });
            } catch (error) {
                setError('Error fetching league data');
            }
        }

        fetchLeagueData();
    }, []);

    if (error) return <div>Error: {error}</div>;

    return (
        <div className="dynasty-league-container">
            <h1>League: {leagueInfo.name}</h1>
            <p>Status: {leagueInfo.status}</p>
            <h2>Teams</h2>
            <div className="teams-container">
                {teams.length > 0 ? (
                    teams.map(team => (
                        <Link
                            key={team.user_id}
                            to={`/dynasty/team/${team.user_id}`}
                            className="team-button"
                        >
                            {team.metadata.team_name || team.display_name}
                        </Link>
                    ))
                ) : (
                    <p>No teams found</p>
                )}
            </div>
        </div>
    );
}

export default DynastyLeague;
