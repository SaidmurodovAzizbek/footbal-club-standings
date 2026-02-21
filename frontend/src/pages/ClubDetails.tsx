import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { apiClient } from '../api/client';
import MatchList from '../components/MatchList';
import { MapPin, CalendarDays, ExternalLink, ArrowLeft, UserCircle2 } from 'lucide-react';

interface ClubInfo {
    id: number;
    external_id: number;
    name_en: string;
    short_name: string | null;
    tla: string | null;
    crest_local: string | null;
    crest_url: string | null;
    founded: number | null;
    venue: string | null;
    website: string | null;
    address: string | null;
    wiki_summary_en: string | null;
    wiki_summary_uz: string | null;
    coach_name: string | null;
    club_colors: string | null;
}

const ClubDetails = () => {
    const { id } = useParams<{ id: string }>();
    const [club, setClub] = useState<ClubInfo | null>(null);
    const [matches, setMatches] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchClubData = async () => {
            setLoading(true);
            try {
                // Fetch Club
                const clubRes = await apiClient.get<ClubInfo>(`/clubs/${id}`);
                setClub(clubRes.data);

                // Fetch Recent/Upcoming Matches for this club
                const matchesRes = await apiClient.get(`/matches?club_id=${id}&limit=10`);
                setMatches(matchesRes.data);
            } catch (err) {
                console.error(err);
                setError('Klub ma\'lumotlari yuklanmadi.');
            } finally {
                setLoading(false);
            }
        };

        if (id) {
            fetchClubData();
        }
    }, [id]);

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
            </div>
        );
    }

    if (error || !club) {
        return (
            <div className="text-center py-20 bg-red-50 dark:bg-red-900/10 rounded-xl border border-red-200">
                <p className="text-red-500 font-medium">{error || 'Klub topilmadi'}</p>
                <Link to="/" className="text-emerald-500 mt-4 inline-block hover:underline">
                    Bosh sahifaga qaytish
                </Link>
            </div>
        );
    }

    const crestImg = club.crest_local || club.crest_url;
    const summary = club.wiki_summary_uz || club.wiki_summary_en;

    return (
        <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Back button */}
            <Link to={-1 as any} className="inline-flex items-center space-x-2 text-sm text-gray-500 hover:text-emerald-600 transition-colors">
                <ArrowLeft className="w-4 h-4" />
                <span>Orqaga</span>
            </Link>

            {/* Club Hero Section */}
            <div className="relative bg-white dark:bg-gray-800 rounded-3xl shadow-xl overflow-hidden border border-gray-100 dark:border-gray-700">
                {/* Background Banner */}
                <div className="absolute top-0 left-0 w-full h-32 bg-gradient-to-r from-emerald-600 to-teal-800 opacity-90"></div>

                <div className="relative px-6 sm:px-10 pt-16 pb-8 flex flex-col md:flex-row gap-6 md:gap-10 items-end md:items-center">
                    {/* Club Crest */}
                    <div className="w-32 h-32 rounded-2xl bg-white dark:bg-gray-900 p-4 shadow-2xl flex-shrink-0 border-4 border-white dark:border-gray-800 z-10 transform -translate-y-4 md:translate-y-0 relative group">
                        {crestImg ? (
                            <img src={crestImg} alt={club.name_en} className="w-full h-full object-contain group-hover:scale-110 transition-transform duration-300" />
                        ) : (
                            <div className="w-full h-full bg-gray-100 dark:bg-gray-800 rounded-xl flex items-center justify-center font-bold text-gray-400 text-3xl">
                                {club.tla || club.name_en.substring(0, 3).toUpperCase()}
                            </div>
                        )}
                    </div>

                    {/* Club Info Headers */}
                    <div className="flex-1 text-center md:text-left">
                        <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 mb-2">
                            <h1 className="text-3xl sm:text-4xl font-extrabold text-gray-900 dark:text-white tracking-tight">
                                {club.name_en}
                            </h1>
                            {club.tla && (
                                <span className="bg-gradient-to-tr from-emerald-100 to-teal-100 dark:from-emerald-900/40 dark:to-teal-900/40 text-emerald-700 dark:text-emerald-300 px-3 py-1 rounded-lg font-mono text-sm border border-emerald-200 dark:border-emerald-800/50 hidden sm:inline-block shadow-sm">
                                    {club.tla}
                                </span>
                            )}
                        </div>
                        <p className="text-gray-500 dark:text-gray-400 font-medium">
                            {club.short_name || club.name_en} {club.club_colors && `• ${club.club_colors}`}
                        </p>
                    </div>

                    {/* Quick Stats side */}
                    <div className="flex md:flex-col gap-4 w-full md:w-auto overflow-x-auto pb-2 md:pb-0 hide-scrollbar">
                        {club.coach_name && (
                            <div className="flex items-center space-x-3 bg-gray-50 dark:bg-gray-700/50 p-3 rounded-xl border border-gray-100 dark:border-gray-600 min-w-max">
                                <UserCircle2 className="w-5 h-5 text-emerald-500" />
                                <div className="text-sm">
                                    <p className="text-gray-500 dark:text-gray-400 text-xs">Murabbiy</p>
                                    <p className="font-semibold text-gray-900 dark:text-white">{club.coach_name}</p>
                                </div>
                            </div>
                        )}
                        {club.founded && (
                            <div className="flex items-center space-x-3 bg-gray-50 dark:bg-gray-700/50 p-3 rounded-xl border border-gray-100 dark:border-gray-600 min-w-max">
                                <CalendarDays className="w-5 h-5 text-emerald-500" />
                                <div className="text-sm">
                                    <p className="text-gray-500 dark:text-gray-400 text-xs">Tashkil etilgan</p>
                                    <p className="font-semibold text-gray-900 dark:text-white">{club.founded}</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Col - Details & About */}
                <div className="space-y-8 lg:col-span-1">
                    {/* Club Details Card */}
                    <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
                        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-6 border-b border-gray-100 dark:border-gray-700 pb-3">Tafsilotlar</h3>
                        <div className="space-y-5">
                            {club.venue && (
                                <div className="flex items-start space-x-4">
                                    <div className="bg-emerald-50 dark:bg-emerald-900/20 p-2 rounded-lg">
                                        <MapPin className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                                    </div>
                                    <div>
                                        <p className="text-sm font-medium text-gray-900 dark:text-white">Stadion</p>
                                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{club.venue}</p>
                                        {club.address && <p className="text-xs text-gray-400 mt-0.5">{club.address}</p>}
                                    </div>
                                </div>
                            )}

                            {club.website && (
                                <div className="flex items-start space-x-4">
                                    <div className="bg-emerald-50 dark:bg-emerald-900/20 p-2 rounded-lg">
                                        <ExternalLink className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                                    </div>
                                    <div>
                                        <p className="text-sm font-medium text-gray-900 dark:text-white">Rasmiy sayt</p>
                                        <a href={club.website} target="_blank" rel="noopener noreferrer" className="text-sm text-emerald-500 hover:text-emerald-600 hover:underline mt-1 inline-block break-all">
                                            {club.website}
                                        </a>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Wikipedia Summary */}
                    {summary && (
                        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 leading-relaxed">
                            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4 border-b border-gray-100 dark:border-gray-700 pb-3">Tarix (Wikipedia)</h3>
                            <p className="text-sm text-gray-600 dark:text-gray-300 text-justify">
                                {summary}
                            </p>
                            <a href={`https://en.wikipedia.org/wiki/${club.name_en.replace(/ /g, '_')}`} target="_blank" rel="noreferrer" className="text-xs text-emerald-500 hover:underline mt-4 inline-block font-medium">
                                To'liq o'qish ↗
                            </a>
                        </div>
                    )}
                </div>

                {/* Right Col - Matches */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
                        <div className="flex items-center justify-between mb-6 border-b border-gray-100 dark:border-gray-700 pb-3">
                            <h3 className="text-lg font-bold text-gray-900 dark:text-white">So'nggi O'yinlar</h3>
                        </div>

                        {matches.length > 0 ? (
                            <MatchList matches={matches} />
                        ) : (
                            <div className="text-center py-10 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-dashed border-gray-300 dark:border-gray-600">
                                <p className="text-gray-500">O'yinlar topilmadi.</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ClubDetails;
