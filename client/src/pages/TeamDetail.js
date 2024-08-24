import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import Modal from 'react-modal';
import '../styles/PlayerDetail.css';  // Use the correct path to your CSS file

const TeamDetail = () => {
    const { teamId } = useParams();
    const [teamData, setTeamData] = useState(null);
    const [transactions, setTransactions] = useState([]);
    const [selectedPlayer, setSelectedPlayer] = useState(null);
    const [modalIsOpen, setModalIsOpen] = useState(false);
    const [playerReview, setPlayerReview] = useState('');
    const [loadingReview, setLoadingReview] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        async function fetchTeamData() {
            try {
                const rostersResponse = await axios.get(`/api/league/1048178119665889280/rosters`);
                const usersResponse = await axios.get(`/api/league/1048178119665889280/users`);
                const team = rostersResponse.data.find(t => t.owner_id.toString() === teamId);

                if (!team) {
                    throw new Error('Team not found in roster data.');
                }

                const owner = usersResponse.data.find(u => u.user_id.toString() === team.owner_id.toString());
                const teamName = owner?.metadata?.team_name || 'Unknown Team';
                const ownerName = owner?.display_name || `Unknown Owner (ID: ${team.owner_id})`;

                setTeamData({
                    ...team,
                    team_name: teamName,
                    owner_name: ownerName,
                });

                const transactionsResponse = await axios.get(`/api/league/1048178119665889280/transactions`);
                const teamTransactions = transactionsResponse.data.filter(tx => tx.roster_ids.includes(parseInt(teamId)));
                setTransactions(teamTransactions);

            } catch (error) {
                setError('Failed to load team data. Please try again later.');
            }
        }

        fetchTeamData();
    }, [teamId]);

    const openModal = async (player) => {
        setSelectedPlayer(player);
        setModalIsOpen(true);

        // Fetch humorous review
        setLoadingReview(true);
        try {
            const response = await axios.post('/api/player-review', {
                player_name: `${player.first_name} ${player.last_name}`
            });
            setPlayerReview(response.data.review);
        } catch (error) {
            setPlayerReview('Could not fetch review. Please try again later.');
        }
        setLoadingReview(false);
    };

    const closeModal = () => {
        setModalIsOpen(false);
        setSelectedPlayer(null);
        setPlayerReview('');
    };

    if (error) return <div>{error}</div>;
    if (!teamData) return <div>Loading...</div>;

    return (
        <div className="team-detail-container">
            <h2>{teamData.team_name} (Owner: {teamData.owner_name})</h2>
            <div>
                <h3>Roster</h3>
                <ul>
                    {teamData.player_details && teamData.player_details.map(player => (
                        <li key={player.player_id}>
                            <button onClick={() => openModal(player)}>
                                {player.first_name} {player.last_name} - {player.position}
                            </button>
                        </li>
                    ))}
                </ul>
            </div>
            <div>
                <h3>Draft Picks</h3>
                <ul>
                    {teamData.draft_picks && teamData.draft_picks.map(pick => (
                        <li key={`${pick.season}-${pick.round}`}>
                            Round {pick.round}, Pick {pick.pick_number}
                        </li>
                    ))}
                </ul>
            </div>
            <div>
                <h3>Recent Transactions</h3>
                <ul>
                    {transactions.map(transaction => (
                        <li key={transaction.transaction_id}>
                            {transaction.type} - {new Date(transaction.status_updated).toLocaleDateString()}
                        </li>
                    ))}
                </ul>
            </div>
            {selectedPlayer && (
                <Modal isOpen={modalIsOpen} onRequestClose={closeModal} className="player-modal" overlayClassName="player-modal-overlay">
                    <div className="modal-content">
                        <h2>{selectedPlayer.first_name} {selectedPlayer.last_name}</h2>
                        <p><img src={`https://sleepercdn.com/avatars/${selectedPlayer.avatar}`} alt={`${selectedPlayer.first_name} ${selectedPlayer.last_name}`} /></p>
                        <p>Position: {selectedPlayer.position}</p>
                        <p>Team: {selectedPlayer.team}</p>
                        <p>College: {selectedPlayer.college}</p>
                        <p>Height: {selectedPlayer.height}</p>
                        <p>Weight: {selectedPlayer.weight}</p>
                        <p>Age: {selectedPlayer.age}</p>
                        <p>Years of Experience: {selectedPlayer.years_exp}</p>
                        <p>Status: {selectedPlayer.status}</p>
                        <p>Injury Status: {selectedPlayer.injury_status}</p>
                        <h3>Review</h3>
                        {loadingReview ? <p>Loading review...</p> : <p>{playerReview}</p>}
                        <button className="modal-close-button" onClick={closeModal}>Close</button>
                    </div>
                </Modal>
            )}
        </div>
    );
};

export default TeamDetail;
