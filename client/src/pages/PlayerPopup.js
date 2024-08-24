import React from 'react';
import Modal from 'react-modal';
import '../styles/PlayerDetail.css';

const PlayerPopup = ({ isOpen, onRequestClose, selectedPlayer, playerReview, playerGrade, loadingReview }) => {
    if (!selectedPlayer) return null;

    return (
        <Modal 
            isOpen={isOpen} 
            onRequestClose={onRequestClose} 
            className="player-popup"
            overlayClassName="player-popup-overlay"
            ariaHideApp={false}
        >
            <div className="modal-header">
                <h2>{selectedPlayer.first_name} {selectedPlayer.last_name}</h2>
                <button onClick={onRequestClose} className="close-button">&times;</button>
            </div>
            <div className="modal-content">
                <div className="player-info">
                    <p><span className="label">Position:</span> {selectedPlayer.position}</p>
                    <p><span className="label">Team:</span> {selectedPlayer.team || 'Unknown'}</p>
                    <p><span className="label">College:</span> {selectedPlayer.college || 'N/A'}</p>
                    <p><span className="label">Height:</span> {selectedPlayer.height || 'N/A'}</p>
                    <p><span className="label">Weight:</span> {selectedPlayer.weight || 'N/A'}</p>
                    <p><span className="label">Years of Experience:</span> {selectedPlayer.years_exp || 'N/A'}</p>
                    <p><span className="label">Age:</span> {selectedPlayer.age || 'N/A'}</p>
                    <div className="grade-box">
                        <span className="grade-label">Grade:</span> {playerGrade || 'N/A'}
                    </div>
                </div>
                <div className="review-section">
                    <h3>Review</h3>
                    {loadingReview ? <p>Loading review...</p> : <p className="review">{playerReview}</p>}
                </div>
            </div>
            <button className="close-modal" onClick={onRequestClose}>Close</button>
        </Modal>
    );
};

export default PlayerPopup;
