import { useEffect, useState } from 'react';
import { apiClient } from '../api/client';
import MatchList from '../components/MatchList';
import { Activity, Clock, LayoutList, CalendarDays } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';

const Matches = () => {
    const [searchParams] = useSearchParams();
    const [matches, setMatches] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [filter, setFilter] = useState<'SCHEDULED' | 'LIVE' | 'FINISHED' | 'ALL'>(
        (searchParams.get('tab') as any) || 'SCHEDULED'
    );

    useEffect(() => {
        const fetchMatches = async () => {
            setLoading(true);
            try {
                let url = '/matches?limit=100';
                if (filter === 'LIVE') {
                    url = '/matches/live';
                } else if (filter === 'FINISHED') {
                    url = '/matches?status=FINISHED&limit=100';
                } else if (filter === 'SCHEDULED') {
                    url = '/matches?status=SCHEDULED,TIMED&limit=100';
                }
                const response = await apiClient.get(url);
                setMatches(response.data);
            } catch (err) {
                console.error(err);
                setError('O\'yinlarni yuklashda xatolik yuz berdi.');
            } finally {
                setLoading(false);
            }
        };

        fetchMatches();

        // Polling for live matches
        let interval: ReturnType<typeof setInterval>;
        if (filter === 'LIVE') {
            interval = setInterval(fetchMatches, 60000); // Poll every minute
        }

        return () => {
            if (interval) clearInterval(interval);
        };
    }, [filter]);

    return (
        <div className="max-w-6xl mx-auto animate-in fade-in duration-500">
            {/* Page Header */}
            <div className="mb-8 flex flex-col sm:flex-row sm:items-end justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white mb-2 flex items-center space-x-3">
                        <span>
                            {filter === 'SCHEDULED' ? "Kelasi tur o'yinlari" : filter === 'LIVE' ? "Jonli o'yinlar" : filter === 'FINISHED' ? "Yakunlangan o'yinlar" : "Barcha o'yinlar"}
                        </span>
                        {filter === 'LIVE' && (
                            <span className="relative flex h-4 w-4">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-4 w-4 bg-red-500"></span>
                            </span>
                        )}
                    </h1>
                    <p className="text-gray-500 dark:text-gray-400">
                        {filter === 'SCHEDULED'
                            ? "Tez orada bo'lib o'tadigan eng qiziqarli uchrashuvlar tartibi."
                            : "Jahon miqyosidagi top o'yinlar va natijalar haqida to'liq ma'lumot"}
                    </p>
                </div>

                {/* Filters */}
                <div className="flex bg-gray-100 dark:bg-gray-800 p-1 rounded-xl w-full sm:w-auto overflow-x-auto shadow-inner border border-gray-200 dark:border-gray-700">
                    <button
                        onClick={() => setFilter('SCHEDULED')}
                        className={`flex items-center justify-center space-x-2 flex-1 sm:flex-none px-4 py-2 text-sm font-medium rounded-lg transition-all ${filter === 'SCHEDULED'
                            ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm ring-1 ring-gray-200 dark:ring-gray-600'
                            : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
                            }`}
                    >
                        <CalendarDays className="w-4 h-4" />
                        <span>Kelasi tur</span>
                    </button>
                    <button
                        onClick={() => setFilter('ALL')}
                        className={`flex items-center justify-center space-x-2 flex-1 sm:flex-none px-4 py-2 text-sm font-medium rounded-lg transition-all ${filter === 'ALL'
                            ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm ring-1 ring-gray-200 dark:ring-gray-600'
                            : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
                            }`}
                    >
                        <LayoutList className="w-4 h-4" />
                        <span>Barchasi</span>
                    </button>
                    <button
                        onClick={() => setFilter('LIVE')}
                        className={`flex items-center justify-center space-x-2 flex-1 sm:flex-none px-4 py-2 text-sm font-medium rounded-lg transition-all ${filter === 'LIVE'
                            ? 'bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 shadow-sm ring-1 ring-red-200 dark:ring-red-800/50'
                            : 'text-gray-500 hover:text-red-500 dark:hover:text-red-400'
                            }`}
                    >
                        <Activity className="w-4 h-4" />
                        <span>Jonli</span>
                    </button>
                    <button
                        onClick={() => setFilter('FINISHED')}
                        className={`flex items-center justify-center space-x-2 flex-1 sm:flex-none px-4 py-2 text-sm font-medium rounded-lg transition-all ${filter === 'FINISHED'
                            ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm ring-1 ring-gray-200 dark:ring-gray-600'
                            : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
                            }`}
                    >
                        <Clock className="w-4 h-4" />
                        <span>Yakunlangan</span>
                    </button>
                </div>
            </div>

            {/* List */}
            {loading ? (
                <div className="space-y-4">
                    {[1, 2, 3, 4].map((i) => (
                        <div key={i} className="animate-pulse bg-white dark:bg-gray-800 h-24 rounded-xl border border-gray-200 dark:border-gray-700"></div>
                    ))}
                </div>
            ) : error ? (
                <div className="text-center py-20 bg-red-50 dark:bg-red-900/10 rounded-xl border border-red-200">
                    <p className="text-red-500 font-medium">{error}</p>
                </div>
            ) : matches.length === 0 ? (
                <div className="text-center py-24 bg-white dark:bg-gray-800 rounded-2xl border border-dashed border-gray-300 dark:border-gray-600 shadow-sm">
                    <div className="bg-gray-50 dark:bg-gray-700/50 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Activity className="w-8 h-8 text-gray-400" />
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-1">
                        {filter === 'LIVE' ? "Ayni vaqtda jonli o'yinlar yo'q" : "O'yinlar topilmadi"}
                    </h3>
                    <p className="text-gray-500">Keyinroq yana tekshirib ko'ring yoki boshqa filterni tanlang.</p>
                    {filter === 'LIVE' && (
                        <button onClick={() => setFilter('ALL')} className="mt-6 px-5 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg transition-colors shadow-sm font-medium">
                            Barcha o'yinlarni ko'rish
                        </button>
                    )}
                </div>
            ) : (
                <div className="bg-transparent border-none">
                    <MatchList matches={matches} />
                </div>
            )}
        </div>
    );
};

export default Matches;
