import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import '../styles/DynastyLeague.css';

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
                    name: "Choo Choo Train",  // Assuming static league name and status for now
                    status: "pre_draft"
                });
            } catch (error) {
                setError('Error fetching league data');
            }
        }

        fetchLeagueData();
    }, []);

    if (error) return <div className="error-message">Error: {error}</div>;

    return (
        <div className="dynasty-league-container">
            <h1 className="league-title">League: {leagueInfo.name}</h1>
            <p className="league-status">Status: {leagueInfo.status}</p>
            <h2 className="teams-header">Teams</h2>
            <div className="teams-container">
                {teams.length > 0 ? (
                    teams.map(team => (
                        <Link
                            key={team.user_id}
                            to={`/dynasty/team/${team.user_id}`}
                            className="team-card"
                        >
                            <div className="team-info">
                                <h2 className="team-name">{team.metadata.team_name || team.display_name}</h2>
                            </div>
                        </Link>
                    ))
                ) : (
                    <p className="no-teams-message">No teams found</p>
                )}
            </div>
        </div>
    );
}

export default DynastyLeague;
