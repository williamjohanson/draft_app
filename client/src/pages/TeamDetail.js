import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import PlayerPopup from './PlayerPopup';
import '../styles/TeamDetail.css';

const TeamDetail = () => {
    const { teamId } = useParams();
    const [teamData, setTeamData] = useState(null);
    const [groupedPlayers, setGroupedPlayers] = useState({});
    const [selectedPlayer, setSelectedPlayer] = useState(null);
    const [modalIsOpen, setModalIsOpen] = useState(false);
    const [suggestedPicks, setSuggestedPicks] = useState([]);
    const [loadingSuggestions, setLoadingSuggestions] = useState(false);
    const [error, setError] = useState(null);
    const [userData, setUserData] = useState(null);
    const [playerReview, setPlayerReview] = useState(null);
    const [playerGrade, setPlayerGrade] = useState(null);
    const [loadingReview, setLoadingReview] = useState(false);

    useEffect(() => {
        async function fetchData() {
            try {
                // Fetch team data
                const rostersResponse = await axios.get(`/api/league/1048178119665889280/rosters`);
                const team = rostersResponse.data.find(t => t.owner_id.toString() === teamId);
                if (!team) {
                    throw new Error('Team not found in roster data.');
                }
                setTeamData(team);
                groupPlayersByPosition(team.player_details);

                // Fetch user data
                const usersResponse = await axios.get(`/api/league/1048178119665889280/users`);
                const user = usersResponse.data.find(u => u.user_id.toString() === team.owner_id.toString());
                setUserData(user);
            } catch (error) {
                console.error('Error fetching data:', error);
                setError('Failed to load team data. Please try again later.');
            }
        }

        fetchData();
    }, [teamId]);

    const groupPlayersByPosition = (players) => {
        const positions = { QB: [], RB: [], WR: [], TE: [], K: [] };
        players.forEach(player => {
            if (positions[player.position]) {
                positions[player.position].push(player);
            }
        });
        setGroupedPlayers(positions);
    };

    const determineNextPick = async () => {
        setLoadingSuggestions(true);
        try {
            const response = await axios.post('/api/next-pick', {
                team_roster: teamData.player_details
            });
            setSuggestedPicks(response.data.suggestions);
        } catch (error) {
            console.error('Error determining next pick:', error);
            setError('Failed to determine next pick. Please try again later.');
        }
        setLoadingSuggestions(false);
    };

    const openModal = (player) => {
        setSelectedPlayer(player);
        setModalIsOpen(true);
    };

    const closeModal = () => {
        setModalIsOpen(false);
        setSelectedPlayer(null);
    };

    if (error) return <div>{error}</div>;
    if (!teamData || !userData) return <div>Loading...</div>;

    // Display the correct team name or user display name
    const teamName = teamData.metadata?.team_name || userData.display_name || `Team ${teamData.owner_id}`;

    return (
        <div className="team-container">
            <h2 className="team-header">{teamName}</h2>
            <div className="roster-container">
                <h3>Roster</h3>
                {Object.keys(groupedPlayers).map((position) => (
                    <div key={position} className="position-group">
                        <h4>{position}</h4>
                        <ul>
                            {groupedPlayers[position].map((player) => (
                                <li key={player.player_id}>
                                    <button onClick={() => openModal(player)}>
                                        {player.first_name} {player.last_name}
                                    </button>
                                </li>
                            ))}
                        </ul>
                    </div>
                ))}
            </div>
            <button onClick={determineNextPick}>Determine Next Pick</button>
            <div className="suggested-picks">
                <h3>Suggested Picks</h3>
                <ul>
                    {suggestedPicks.map((suggestion, index) => (
                        <li key={index}>
                            <strong>{suggestion.name}</strong> - Grade: {suggestion.grade}
                        </li>
                    ))}
                </ul>
            </div>
            <PlayerPopup
                isOpen={modalIsOpen}
                onRequestClose={closeModal}
                selectedPlayer={selectedPlayer}
                playerReview={playerReview}
                playerGrade={playerGrade}
                loadingReview={loadingReview}
            />
        </div>
    );
};

export default TeamDetail;
