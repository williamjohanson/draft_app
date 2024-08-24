import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import PlayerPopup from './PlayerPopup';
import '../styles/Draft.css';

const Draft = () => {
    const { year } = useParams();
    const draftYear = year || new Date().getFullYear();
    const [draftData, setDraftData] = useState(null);
    const [picks, setPicks] = useState([]);
    const [rookies, setRookies] = useState([]);
    const [selectedPlayer, setSelectedPlayer] = useState(null);
    const [modalIsOpen, setModalIsOpen] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        async function fetchDraftData() {
            try {
                console.log("Fetching draft data for year:", draftYear);
                const response = await axios.get(`/api/league/1048178119665889280/drafts/${draftYear}`);
                setDraftData(response.data);

                const picksResponse = await axios.get(`/api/draft/${response.data.draft_id}/picks`);
                setPicks(picksResponse.data);

                if (draftYear === `${new Date().getFullYear()}`) {
                    const rookiesResponse = await axios.get('/api/rookies');
                    setRookies(rookiesResponse.data);
                }

                setLoading(false);
            } catch (error) {
                console.error('Error fetching draft data:', error);
                setError(`Draft for year ${draftYear} not found.`);
                setLoading(false);
            }
        }

        fetchDraftData();
    }, [draftYear]);

    const openModal = (player) => {
        setSelectedPlayer(player);
        setModalIsOpen(true);
    };

    const closeModal = () => {
        setModalIsOpen(false);
        setSelectedPlayer(null);
    };

    if (error) return <div>{error}</div>;
    if (loading) return <div>Loading...</div>;

    return (
        <div className="draft-container">
            <nav className="draft-nav">
                <Link to="/">Home</Link>
                {Array.from({ length: draftYear - 2017 }, (_, index) => {
                    const draftYearLink = draftYear - index;
                    return (
                        <Link key={draftYearLink} to={`/draft/${draftYearLink}`}>
                            {draftYearLink} Draft
                        </Link>
                    );
                })}
            </nav>

            <h2 className="draft-header">Draft - {draftYear}</h2>

            <div className="draft-picks">
                <h3>Picks</h3>
                {picks.length > 0 ? (
                    picks.map((pick, index) => (
                        <div key={index} className="draft-pick">
                            <span>
                                Round {pick.round}, Pick {pick.pick_no}: 
                                {pick.metadata ? (
                                    <button onClick={() => openModal(pick.metadata)}>
                                        {pick.metadata.first_name} {pick.metadata.last_name}
                                    </button>
                                ) : (
                                    'No Pick Yet'
                                )}
                            </span>
                        </div>
                    ))
                ) : (
                    <p>No picks found for this draft.</p>
                )}
            </div>

            {draftYear === `${new Date().getFullYear()}` && (
                <div className="rookies-list">
                    <h3>Available Rookies</h3>
                    {rookies.map((rookie, index) => (
                        <div key={index} className="rookie">
                            <button onClick={() => openModal(rookie)}>
                                {rookie.name} - {rookie.grade}
                            </button>
                        </div>
                    ))}
                </div>
            )}

            <PlayerPopup
                isOpen={modalIsOpen}
                onRequestClose={closeModal}
                selectedPlayer={selectedPlayer}
                playerGrade={selectedPlayer?.grade}
                loadingReview={false}  // Adjust based on actual loading state
            />
        </div>
    );
};

export default Draft;
