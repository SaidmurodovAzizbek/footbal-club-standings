import { useEffect, useState } from 'react';
import { apiClient } from '../api/client';
import { Link } from 'react-router-dom';
import { Trophy, Search, Users } from 'lucide-react';

interface League {
    id: number;
    name: string;
    name_en: string;
    code: string;
}

interface Club {
    id: number;
    name_en: string;
    tla: string | null;
    crest_local: string | null;
    crest_url: string | null;
    founded: number | null;
}

const Clubs = () => {
    const [clubs, setClubs] = useState<Club[]>([]);
    const [leagues, setLeagues] = useState<League[]>([]);
    const [selectedLeague, setSelectedLeague] = useState<string>('ALL');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchLeagues = async () => {
            try {
                const res = await apiClient.get<League[]>('/leagues');
                setLeagues(res.data);
            } catch (err) {
                console.error("Failed to load leagues", err);
            }
        };
        fetchLeagues();
    }, []);

    useEffect(() => {
        const fetchClubs = async () => {
            setLoading(true);
            try {
                let url = '/clubs?limit=100';
                if (selectedLeague !== 'ALL') {
                    url += `&league_id=${selectedLeague}`;
                }
                const res = await apiClient.get<Club[]>(url);
                const sortedClubs = res.data.sort((a, b) => a.name_en.localeCompare(b.name_en));
                setClubs(sortedClubs);
            } catch (err) {
                console.error(err);
                setError('Jamoalarni yuklashda xatolik yuz berdi.');
            } finally {
                setLoading(false);
            }
        };

        fetchClubs();
    }, [selectedLeague]);

    return (
        <div className="max-w-7xl mx-auto animate-in fade-in duration-500">
            {/* Page Header */}
            <div className="mb-8 flex flex-col sm:flex-row sm:items-end justify-between gap-6">
                <div>
                    <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white mb-2 flex items-center space-x-3">
                        <Users className="w-8 h-8 text-emerald-500" />
                        <span>Barcha Jamoalar</span>
                    </h1>
                    <p className="text-gray-500 dark:text-gray-400">
                        Top ligalardagi barcha futbol jamoalari va klublar ro'yxati.
                    </p>
                </div>

                {/* Filters */}
                <div className="flex bg-white dark:bg-gray-800 p-2 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 w-full sm:w-auto">
                    <div className="flex items-center space-x-2 px-3 w-full">
                        <Trophy className="w-5 h-5 text-gray-400" />
                        <select
                            value={selectedLeague}
                            onChange={(e) => setSelectedLeague(e.target.value)}
                            className="bg-transparent border-none focus:ring-0 text-sm font-medium text-gray-700 dark:text-gray-200 w-full sm:w-48 appearance-none py-1 cursor-pointer"
                        >
                            <option value="ALL" className="dark:bg-gray-800">Barcha ligalar</option>
                            {leagues.map((league) => (
                                <option key={league.id} value={league.id.toString()} className="dark:bg-gray-800">
                                    {league.name_en}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>
            </div>

            {/* List */}
            {loading ? (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                    {[...Array(15)].map((_, i) => (
                        <div key={i} className="animate-pulse bg-white dark:bg-gray-800 h-40 rounded-2xl border border-gray-200 dark:border-gray-700"></div>
                    ))}
                </div>
            ) : error ? (
                <div className="text-center py-20 bg-red-50 dark:bg-red-900/10 rounded-xl border border-red-200">
                    <p className="text-red-500 font-medium">{error}</p>
                </div>
            ) : clubs.length === 0 ? (
                <div className="text-center py-24 bg-white dark:bg-gray-800 rounded-2xl border border-dashed border-gray-300 dark:border-gray-600 shadow-sm">
                    <div className="bg-gray-50 dark:bg-gray-700/50 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Search className="w-8 h-8 text-gray-400" />
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-1">
                        Jamoalar topilmadi
                    </h3>
                </div>
            ) : (
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4 md:gap-6">
                    {clubs.map((club) => (
                        <Link
                            key={club.id}
                            to={`/club/${club.id}`}
                            className="group bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 hover:border-emerald-500/50 dark:hover:border-emerald-500/50 rounded-2xl p-4 flex flex-col items-center text-center transition-all duration-300 hover:shadow-xl hover:-translate-y-1"
                        >
                            <div className="w-20 h-20 bg-gray-50 dark:bg-gray-900/50 rounded-full p-3 mb-4 shadow-inner flex items-center justify-center group-hover:bg-emerald-50 dark:group-hover:bg-emerald-900/20 transition-colors">
                                <img
                                    src={club.crest_local || club.crest_url || ''}
                                    alt={club.name_en}
                                    className="w-full h-full object-contain filter group-hover:scale-110 transition-transform duration-300"
                                    onError={(e) => {
                                        (e.target as HTMLImageElement).style.display = 'none';
                                        (e.target as HTMLImageElement).nextElementSibling?.classList.remove('hidden');
                                    }}
                                />
                                <span className="hidden text-xl font-bold text-gray-400">
                                    {club.tla || club.name_en.substring(0, 3).toUpperCase()}
                                </span>
                            </div>
                            <h3 className="font-bold text-gray-900 dark:text-white line-clamp-1 mb-1 group-hover:text-emerald-500 transition-colors">
                                {club.name_en}
                            </h3>
                            {club.founded && (
                                <p className="text-xs text-gray-500 dark:text-gray-400">
                                    Est. {club.founded}
                                </p>
                            )}
                        </Link>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Clubs;
