import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import LeagueDetails from './pages/LeagueDetails';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="league/:id" element={<LeagueDetails />} />
      </Route>
    </Routes>
  );
}

export default App;
