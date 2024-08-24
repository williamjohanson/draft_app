import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import DynastyLeague from './pages/DynastyLeague';
import TeamDetail from './pages/TeamDetail';
import RedraftLeague from './pages/RedraftLeague';
import HomePage from './pages/HomePage';

function App() {
  return (
    <Router>
      <div style={{ display: 'flex' }}>
        <div style={{ width: '100%' }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/dynasty/*" element={<LeagueWithHomeLink component={DynastyLeague} />} />
            <Route path="/redraft/*" element={<LeagueWithHomeLink component={RedraftLeague} />} />
            <Route path="/dynasty/team/:teamId" element={<TeamDetail />} />
            {/* Add more routes if needed */}
          </Routes>
        </div>
      </div>
    </Router>
  );
}

function LeagueWithHomeLink({ component: Component }) {
  return (
    <div style={{ position: 'relative' }}>
      <Link to="/" style={{ position: 'absolute', top: '10px', left: '10px', padding: '10px', background: '#333', color: '#fff', textDecoration: 'none', borderRadius: '5px' }}>
        Home
      </Link>
      <Component />
    </div>
  );
}

export default App;
