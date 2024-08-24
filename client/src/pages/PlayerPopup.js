import React from 'react';
import Modal from 'react-modal';
import '../styles/PlayerDetail.css';

const PlayerPopup = ({ isOpen, onRequestClose, selectedPlayer, playerReview, playerGrade, loadingReview }) => {
    if (!selectedPlayer) return null;

    return (
        <Modal isOpen={isOpen} onRequestClose={onRequestClose} className="player-popup">
            <div className="modal-header">
                <h2>{selectedPlayer.first_name} {selectedPlayer.last_name}</h2>
                <button onClick={onRequestClose}>&times;</button>
            </div>
            <div className="modal-content">
                <p><span>Position:</span> {selectedPlayer.position}</p>
                <p><span>Team:</span> {selectedPlayer.team || 'Unknown'}</p>
                <p><span>College:</span> {selectedPlayer.college || 'N/A'}</p>
                <p><span>Height:</span> {selectedPlayer.height || 'N/A'}</p>
                <p><span>Weight:</span> {selectedPlayer.weight || 'N/A'}</p>
                <p><span>Years of Experience:</span> {selectedPlayer.years_exp || 'N/A'}</p>
                <p><span>Age:</span> {selectedPlayer.age || 'N/A'}</p>
                <div className="grade-box">{playerGrade || 'N/A'}</div>
                <h3>Review</h3>
                {loadingReview ? <p>Loading review...</p> : <p className="review">{playerReview}</p>}
            </div>
            <button className="close-modal" onClick={onRequestClose}>Close</button>
        </Modal>
    );
};

export default PlayerPopup;
