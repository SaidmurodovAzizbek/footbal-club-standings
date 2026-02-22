import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { apiClient } from '../api/client';
import StandingsTable from '../components/StandingsTable';
import MatchList from '../components/MatchList';
import { Calendar as CalendarIcon, Users, MapPin, Trophy } from 'lucide-react';
import { LEAGUE_META } from '../utils/constants';

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

    const meta = league ? LEAGUE_META[league.code] : null;
    const title = meta ? meta.title : league.name_en;
    const desc = meta ? meta.desc : 'Liga haqida batafsil ma\'lumotlar va statistikalar.';
    const logo = meta ? meta.logo : league.emblem_local;

    return (
        <div>
            {/* Premium League Header */}
            <div className="relative rounded-3xl shadow-2xl mb-8 overflow-hidden border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
                {/* Background Parallax Image */}
                {meta && (
                    <div className="absolute inset-0 w-full h-full opacity-10 dark:opacity-20 pointer-events-none">
                        <img src={meta.bgImage} alt="background" className="w-full h-full object-cover" />
                        <div className="absolute inset-0 bg-gradient-to-r from-white via-white/80 to-transparent dark:from-gray-800 dark:via-gray-800/80"></div>
                    </div>
                )}

                <div className="relative z-10 p-6 md:p-10 flex flex-col md:flex-row items-center md:items-start space-y-6 md:space-y-0 md:space-x-8">
                    {/* Glassmorphism Logo Container */}
                    <div className="w-32 h-32 flex-shrink-0 bg-white/50 dark:bg-gray-900/50 backdrop-blur-xl p-4 rounded-2xl border border-gray-200 dark:border-gray-600 shadow-xl flex items-center justify-center relative group">
                        <div className="absolute inset-0 border-2 border-emerald-400 rounded-2xl opacity-0 group-hover:opacity-100 scale-105 group-hover:scale-100 transition-all duration-300"></div>
                        {logo ? (
                            <img src={logo} alt={title} className="w-full h-full object-contain drop-shadow-lg" />
                        ) : (
                            <Trophy className="w-16 h-16 text-gray-400" />
                        )}
                    </div>

                    <div className="flex-1 text-center md:text-left">
                        <span className="inline-flex items-center space-x-1 px-3 py-1 rounded-full bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 text-xs font-bold uppercase tracking-wider mb-3">
                            <MapPin className="w-3 h-3" />
                            <span>{league.country}</span>
                        </span>
                        <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 dark:text-white mb-4 tracking-tight">
                            {title}
                        </h1>
                        <p className="text-gray-600 dark:text-gray-300 max-w-2xl text-lg leading-relaxed mb-6">
                            {desc}
                        </p>

                        <div className="flex flex-wrap items-center justify-center md:justify-start gap-4">
                            <div className="flex items-center space-x-2 bg-gray-100 dark:bg-gray-700/50 px-4 py-2 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-600">
                                <CalendarIcon className="w-4 h-4 text-emerald-500" />
                                <span>{league.season_start.split('-')[0]}/{league.season_end.split('-')[0]} Mavsum</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Glassy Tabs Container */}
                <div className="relative z-10 px-6 md:px-10 border-t border-gray-200 dark:border-gray-700 flex space-x-2 bg-gray-50/50 dark:bg-gray-900/20 backdrop-blur-sm pt-4">
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
