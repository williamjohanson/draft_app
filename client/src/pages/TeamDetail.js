import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import PlayerPopup from './PlayerPopup';  // Ensure you have this component
import '../styles/TeamDetail.css';

const TeamDetail = () => {
    const { teamId } = useParams();
    const [teamData, setTeamData] = useState(null);
    const [groupedPlayers, setGroupedPlayers] = useState({});
    const [selectedPlayer, setSelectedPlayer] = useState(null);
    const [modalIsOpen, setModalIsOpen] = useState(false);
    const [playerReview, setPlayerReview] = useState('');
    const [playerGrade, setPlayerGrade] = useState('');
    const [teamGrade, setTeamGrade] = useState('');
    const [loadingReview, setLoadingReview] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        async function fetchTeamData() {
            try {
                const rostersResponse = await axios.get(`/api/league/1048178119665889280/rosters`);
                const team = rostersResponse.data.find(t => t.owner_id.toString() === teamId);
                if (!team) {
                    throw new Error('Team not found in roster data.');
                }
                setTeamData(team);
                groupPlayersByPosition(team.player_details);
                calculatePlayerGrades(team.player_details);
            } catch (error) {
                console.error('Error fetching team data:', error);
                setError('Failed to load team data. Please try again later.');
            }
        }

        fetchTeamData();
    }, [teamId]);

    const groupPlayersByPosition = (players) => {
        const positions = { QB: [], RB: [], WR: [], TE: [] };
        players.forEach(player => {
            if (positions[player.position]) {
                positions[player.position].push(player);
            }
        });
        setGroupedPlayers(positions);
    };

    const calculatePlayerGrades = async (players) => {
        try {
            const gradePromises = players.map(player =>
                axios.post('/api/player-grade', {
                    player_name: player.first_name + ' ' + player.last_name,
                    player_position: player.position,
                    team_roster: players
                })
            );

            const grades = await Promise.all(gradePromises);

            // Map grades to players
            players.forEach((player, index) => {
                player.grade = grades[index].data.grade;
            });

            // Calculate team grade (simple average for demonstration)
            const teamGrade = grades.reduce((sum, grade) => sum + parseFloat(grade.data.grade), 0) / grades.length;
            setTeamGrade(teamGrade.toFixed(2));
        } catch (error) {
            console.error('Error calculating player grades:', error);
        }
    };

    const openModal = async (player) => {
        setSelectedPlayer(player);
        setModalIsOpen(true);

        const cachedResponse = localStorage.getItem(player.player_id);
        if (cachedResponse) {
            const { review } = JSON.parse(cachedResponse);
            setPlayerReview(review);
        } else {
            setLoadingReview(true);
            try {
                const response = await axios.post('/api/player-review', {
                    player_name: `${player.first_name} ${player.last_name}`,
                    player_position: player.position,
                    player_grade: player.grade
                });
                const { review } = response.data;
                setPlayerReview(review);

                localStorage.setItem(player.player_id, JSON.stringify({ review }));
            } catch (error) {
                console.error('Error fetching player review:', error);
                setPlayerReview('Could not fetch review. Please try again later.');
            }
            setLoadingReview(false);
        }
    };

    const closeModal = () => {
        setModalIsOpen(false);
        setSelectedPlayer(null);
        setPlayerReview('');
        setPlayerGrade('');
    };

    if (error) return <div>{error}</div>;
    if (!teamData) return <div>Loading...</div>;

    return (
        <div className="team-container">
            <h2 className="team-header">{teamData.metadata.team_name || `Team ${teamData.owner_id}`}</h2>
            <div className="team-grade">Team Grade: {teamGrade}</div>
            <div className="roster-container">
                <h3>Roster</h3>
                {Object.keys(groupedPlayers).map(position => (
                    <div key={position} className="position-group">
                        <h4>{position}</h4>
                        <ul>
                            {groupedPlayers[position].map(player => (
                                <li key={player.player_id}>
                                    <button onClick={() => openModal(player)}>
                                        {player.first_name} {player.last_name} - {player.grade}
                                    </button>
                                </li>
                            ))}
                        </ul>
                    </div>
                ))}
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
