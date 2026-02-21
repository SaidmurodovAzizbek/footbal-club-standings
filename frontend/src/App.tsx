import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import LeagueDetails from './pages/LeagueDetails';
import ClubDetails from './pages/ClubDetails';
import Matches from './pages/Matches';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="league/:id" element={<LeagueDetails />} />
        <Route path="club/:id" element={<ClubDetails />} />
        <Route path="matches" element={<Matches />} />
      </Route>
    </Routes>
  );
}

export default App;
