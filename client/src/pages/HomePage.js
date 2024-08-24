import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/HomePage.css'; 

function HomePage() {
  return (
    <div className="home-container">
      <h1>Welcome to the Fantasy Football Draft App</h1>
      <p>Select your league type:</p>
      <div className="button-container">
        <Link to="/dynasty">
          <button className="league-button">
            <img src="/images/sleeper-logo.png" alt="Sleeper" className="league-logo" />
            Dynasty League
          </button>
        </Link>
        <Link to="/redraft">
          <button className="league-button">
            <img src="/images/espn-logo.png" alt="ESPN" className="league-logo" />
            Redraft League
          </button>
        </Link>
      </div>
    </div>
  );
}

export default HomePage;
