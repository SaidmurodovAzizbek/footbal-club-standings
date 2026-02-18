import { useEffect, useState } from 'react';
import { apiClient } from '../api/client';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

interface League {
    id: number;
    name: string;
    name_en: string;
    country: string;
    code: string;
    emblem_local: string | null;
    is_active: boolean;
}

const Home = () => {
    const [leagues, setLeagues] = useState<League[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchLeagues = async () => {
            try {
                const response = await apiClient.get<League[]>('/leagues');
                setLeagues(response.data);
            } catch (err) {
                setError('Ligalar yuklanmadi. Iltimos keyinroq urinib ko\'ring.');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        fetchLeagues();
    }, []);

    if (loading) {
        return (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[1, 2, 3, 4, 5, 6].map((i) => (
                    <div key={i} className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 animate-pulse border border-gray-200 dark:border-gray-700 h-48">
                        <div className="flex items-center space-x-4 mb-4">
                            <div className="w-12 h-12 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
                            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
                        </div>
                    </div>
                ))}
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center py-20 bg-red-50 dark:bg-red-900/10 rounded-xl border border-red-200 dark:border-red-800">
                <p className="text-red-500 dark:text-red-400 font-medium">{error}</p>
                <button onClick={() => window.location.reload()} className="mt-4 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-md transition-colors">
                    Qayta urinish
                </button>
            </div>
        );
    }

    return (
        <div>
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Ligalar</h1>
                <p className="text-gray-500 dark:text-gray-400">Dunyoning eng mashhur futbol ligalari statistikasi</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {leagues.map((league) => (
                    <Link
                        key={league.id}
                        to={`/league/${league.id}`}
                        className="group relative bg-white dark:bg-gray-800 rounded-xl shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-200 dark:border-gray-700"
                    >
                        <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-emerald-500 to-teal-400 opacity-0 group-hover:opacity-100 transition-opacity"></div>

                        <div className="p-6">
                            <div className="flex items-start justify-between mb-4">
                                <div className="w-16 h-16 bg-gray-50 dark:bg-gray-700/50 rounded-full flex items-center justify-center p-2 border border-gray-100 dark:border-gray-600 group-hover:scale-110 transition-transform duration-300">
                                    {league.emblem_local ? (
                                        <img src={league.emblem_local} alt={league.name_en} className="w-full h-full object-contain" />
                                    ) : (
                                        <span className="text-2xl font-bold text-gray-400">{league.code}</span>
                                    )}
                                </div>
                                <div className="px-2 py-1 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 text-xs font-semibold rounded-full uppercase tracking-wide">
                                    {league.country}
                                </div>
                            </div>

                            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-1 group-hover:text-emerald-500 dark:group-hover:text-emerald-400 transition-colors">
                                {league.name_en}
                            </h2>
                            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4 font-mono text-xs">
                                {league.code}
                            </p>

                            <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
                                <span className="text-sm font-medium text-gray-500 dark:text-gray-400 group-hover:text-gray-800 dark:group-hover:text-gray-200 transition-colors">
                                    Batafsil
                                </span>
                                <div className="w-8 h-8 rounded-full bg-gray-50 dark:bg-gray-700 text-gray-400 group-hover:bg-emerald-500 group-hover:text-white flex items-center justify-center transition-all duration-300 transform group-hover:translate-x-1">
                                    <ArrowRight className="w-4 h-4" />
                                </div>
                            </div>
                        </div>
                    </Link>
                ))}
            </div>
        </div>
    );
};

export default Home;
