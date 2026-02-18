import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { apiClient } from '../api/client';
import StandingsTable from '../components/StandingsTable';
import MatchList from '../components/MatchList';
import { Calendar as CalendarIcon, Users } from 'lucide-react';

interface LeagueInfo {
    id: number;
    name: string;
    name_en: string;
    country: string;
    code: string;
    emblem_local: string | null;
    season_start: string;
    season_end: string;
}

const LeagueDetails = () => {
    const { id } = useParams<{ id: string }>();
    const [league, setLeague] = useState<LeagueInfo | null>(null);
    const [standings, setStandings] = useState<any[]>([]);
    const [matches, setMatches] = useState<any[]>([]);
    const [activeTab, setActiveTab] = useState<'standings' | 'matches'>('standings');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                // Fetch League info
                // Note: The API might just return the list or I need a specific endpoint.
                // Based on explore: /leagues/{id} wasn't explicitly seen but likely exists or I can filter from list.
                // Actually I should check if /leagues/{id} exists.
                // The implementation plan assumed services but I'm doing direct calls for MVP speed.

                // Let's assume /api/v1/leagues/{id} exists (standard REST). 
                // If not, I'll fetch list and find (fallback).

                // But the previous list_dir of schemas showed LeagueResponse has id.
                // I'll try to fetch specific league. If not available, I might need to implement it in backend or use what I have.
                // Wait, the backend conversation summary mentioned "API endpoints".
                // Let's check `backend/app/api/endpoints/leagues.py` if I could.
                // For now, I'll try /leagues/{id}.

                const leagueRes = await apiClient.get<LeagueInfo>(`/leagues/${id}`);
                setLeague(leagueRes.data);

                // Fetch Standings
                const standingsRes = await apiClient.get(`/standings/league/${id}`);
                setStandings(standingsRes.data);

                // Fetch Matches
                // I need to filter matches by league.
                const matchesRes = await apiClient.get(`/matches?league_id=${id}`);
                setMatches(matchesRes.data);

            } catch (err) {
                console.error(err);
                setError('Ma\'lumotlarni yuklashda xatolik yuz berdi.');
            } finally {
                setLoading(false);
            }
        };

        if (id) {
            fetchData();
        }
    }, [id]);

    if (loading) {
        return <div className="flex justify-center items-center h-64"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div></div>;
    }

    if (error || !league) {
        return <div className="text-center text-red-500 py-10">{error || 'Liga topilmadi'}</div>;
    }

    return (
        <div>
            {/* League Header */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8 border border-gray-200 dark:border-gray-700 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl -mr-16 -mt-16"></div>
                <div className="flex flex-col md:flex-row items-center md:items-start space-y-4 md:space-y-0 md:space-x-6 relative z-10">
                    <div className="w-24 h-24 bg-gray-50 dark:bg-gray-700 p-2 rounded-full border-2 border-emerald-100 dark:border-emerald-900 shadow-md">
                        {league.emblem_local ? (
                            <img src={league.emblem_local} alt={league.name_en} className="w-full h-full object-contain" />
                        ) : (
                            <div className="w-full h-full flex items-center justify-center text-2xl font-bold text-gray-400">{league.code}</div>
                        )}
                    </div>
                    <div className="text-center md:text-left">
                        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">{league.name_en}</h1>
                        <div className="flex items-center justify-center md:justify-start space-x-4 text-sm text-gray-500 dark:text-gray-400">
                            <span className="flex items-center space-x-1">
                                <span className="font-semibold px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">{league.country}</span>
                            </span>
                            <span>•</span>
                            <span>{league.season_start} - {league.season_end}</span>
                        </div>
                    </div>
                </div>

                {/* Tabs */}
                <div className="flex items-center justify-center md:justify-start mt-8 space-x-1 border-b border-gray-200 dark:border-gray-700">
                    <button
                        onClick={() => setActiveTab('standings')}
                        className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors flex items-center space-x-2 ${activeTab === 'standings' ? 'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400 border-b-2 border-emerald-500' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'}`}
                    >
                        <Users className="w-4 h-4" />
                        <span>Turnir jadvali</span>
                    </button>
                    <button
                        onClick={() => setActiveTab('matches')}
                        className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors flex items-center space-x-2 ${activeTab === 'matches' ? 'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400 border-b-2 border-emerald-500' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'}`}
                    >
                        <CalendarIcon className="w-4 h-4" />
                        <span>O'yinlar</span>
                    </button>
                </div>
            </div>

            {/* Content */}
            <div className="transition-all duration-300">
                {activeTab === 'standings' ? (
                    <StandingsTable standings={standings} />
                ) : (
                    <MatchList matches={matches} />
                )}
            </div>
        </div>
    );
};

export default LeagueDetails;
