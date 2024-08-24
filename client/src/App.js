import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import DynastyLeague from './pages/DynastyLeague';
import TeamDetail from './pages/TeamDetail';  // Create this component for team details
import RedraftLeague from './pages/RedraftLeague';  // Assuming you have a RedraftLeague component
import HomePage from './pages/HomePage';  // Your existing HomePage component

function App() {
  return (
    <Router>
      <div style={{ display: 'flex' }}>
        <nav style={{ width: '200px', padding: '10px', borderRight: '1px solid #ddd' }}>
          <h2>Navigation</h2>
          <ul style={{ listStyleType: 'none', padding: 0 }}>
            <li><Link to="/">Home</Link></li>
            <li><Link to="/dynasty">Dynasty League</Link></li>
            <li><Link to="/redraft">Redraft League</Link></li>
            {/* Add more links here if you have additional pages */}
          </ul>
        </nav>
        <div style={{ flex: 1, padding: '10px' }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/dynasty" element={<DynastyLeague />} />
            <Route path="/dynasty/team/:teamId" element={<TeamDetail />} />
            <Route path="/redraft" element={<RedraftLeague />} />
            {/* Add more routes here if you have additional pages */}
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
