import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import DynastyLeague from './pages/DynastyLeague';
import TeamDetail from './pages/TeamDetail';
import RedraftLeague from './pages/RedraftLeague';
import HomePage from './pages/HomePage';
import Draft from './pages/Draft';

function App() {
  return (
    <Router>
      <div style={{ display: 'flex' }}>
        <div style={{ width: '100%' }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/dynasty/*" element={<LeagueWithHomeLink component={DynastyLeague} />} />
            <Route path="dynasty/draft*" element={<LeagueWithHomeLink component={Draft} />} />
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
      <Link to="/" style={{width: '80px', textAlign: 'center', position: 'absolute', top: '10px', left: '10px', padding: '10px', background: '#333', color: '#fff', textDecoration: 'none', borderRadius: '5px' }}>
        Home
      </Link>
      <Link to="/dynasty/draft" style={{width: '80px', textAlign: 'center', position: 'absolute', top: '60px', left: '10px', padding: '10px', background: '#333', color: '#fff', textDecoration: 'none', borderRadius: '5px' }}>
        Draft
      </Link>
      <Component />
    </div>
  );
}

export default App;
