import { useEffect, useState } from 'react';
import { apiClient } from '../api/client';
import { Link } from 'react-router-dom';
import { ArrowRight, Trophy, Activity, Calendar, MapPin, PlayCircle, Info } from 'lucide-react';

interface League {
    id: number;
    name: string;
    name_en: string;
    country: string;
    code: string;
    emblem_local: string | null;
    is_active: boolean;
    current_matchday: number | null;
}

interface LiveMatchParams {
    id: number;
}

import { LEAGUE_META } from '../utils/constants';

const Home = () => {
    const [leagues, setLeagues] = useState<League[]>([]);
    const [liveMatches, setLiveMatches] = useState<LiveMatchParams[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchHomeData = async () => {
            try {
                const [leaguesRes, liveRes] = await Promise.all([
                    apiClient.get<League[]>('/leagues'),
                    apiClient.get<LiveMatchParams[]>('/matches/live'),
                ]);

                // Sort leagues according to user's requested order
                const order = ['PD', 'PL', 'BL1', 'SA', 'FL1'];
                const sortedLeagues = order.map(code =>
                    leaguesRes.data.find(l => l.code === code)
                ).filter(Boolean) as League[];

                setLeagues(sortedLeagues);
                setLiveMatches(liveRes.data);
            } catch (err) {
                setError('Ma\'lumotlar yuklanmadi. Iltimos keyinroq urinib ko\'ring.');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        fetchHomeData();
    }, []);

    if (loading) {
        return (
            <div className="flex flex-col space-y-8 animate-pulse">
                <div className="h-64 bg-gray-200 dark:bg-gray-800 rounded-3xl w-full"></div>
                <div className="h-48 bg-gray-200 dark:bg-gray-800 rounded-3xl w-full"></div>
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
        <div className="space-y-12">

            {/* HERO SECTION - README STYLE */}
            <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white shadow-2xl border border-gray-700">
                {/* Decorative background glow */}
                <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-emerald-500/20 rounded-full blur-[100px] -translate-y-1/2 translate-x-1/3"></div>
                <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-blue-500/20 rounded-full blur-[100px] translate-y-1/3 -translate-x-1/3"></div>

                <div className="relative z-10 p-8 md:p-12 lg:p-16 flex flex-col md:flex-row items-center justify-between gap-10">
                    <div className="flex-1 space-y-6">
                        <div className="inline-flex items-center space-x-2 px-3 py-1 bg-emerald-500/20 text-emerald-300 rounded-full border border-emerald-500/30 text-sm font-medium">
                            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                            <span>Premium Futbol Platformasi</span>
                        </div>
                        <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-tight leading-tight">
                            Futbol Olamiga <br /> <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-300">Xush Kelibsiz</span>
                        </h1>
                        <p className="text-gray-300 text-lg md:text-xl max-w-2xl leading-relaxed">
                            FCS — dunyoning eng yirik TOP 5 ligasini o'zida jamlagan professional loyiha.
                            Sevimli ligangizning barcha o'yinlarini shu yerda kuzatib boring.
                            Sevimli jamoangizning barcha o'yinlarini shu yerda kuzatib boring.
                        </p>
                        <div className="flex flex-wrap items-center gap-4 pt-4">
                            <Link to="/matches" className="px-6 py-3 bg-emerald-500 hover:bg-emerald-600 text-white font-medium rounded-xl transition-all shadow-lg hover:shadow-emerald-500/30 flex items-center space-x-2">
                                <Calendar className="w-5 h-5" />
                                <span>Barcha o'yinlarni ko'rish</span>
                            </Link>
                            <a href="#leagues" className="px-6 py-3 bg-gray-800 hover:bg-gray-700 text-white font-medium rounded-xl border border-gray-600 transition-all flex items-center space-x-2">
                                <Trophy className="w-5 h-5" />
                                <span>Ligalar ro'yxati</span>
                            </a>
                        </div>
                    </div>

                    <div className="w-full md:w-1/3 flex flex-col gap-4">
                        <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/10">
                            <div className="flex items-center space-x-3 mb-2">
                                <Activity className="w-6 h-6 text-emerald-400" />
                                <h3 className="font-semibold text-lg">Tezkor Sinxronizatsiya</h3>
                            </div>
                            <p className="text-sm text-gray-300">O'yin natijalari va jadvallar avtomatik yangilanib turadi(malumotlar 1-2 daqiqaga kechikishi mumkin)</p>
                        </div>
                        <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/10">
                            <div className="flex items-center space-x-3 mb-2">
                                <Info className="w-6 h-6 text-blue-400" />
                                <h3 className="font-semibold text-lg">Kengaytirilgan baza</h3>
                            </div>
                            <p className="text-sm text-gray-300">Klublarning malumotlari, liga jadvallari va tur o'yinlari aynan shu yerda(Wikipedia/Football-data.org)</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* LIVE MATCHES BANNER (If any) */}
            {liveMatches.length > 0 && (
                <section className="bg-red-500 text-white rounded-2xl p-6 shadow-xl shadow-red-500/20 flex flex-col sm:flex-row items-center justify-between gap-4 border border-red-400 relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-white/20 rounded-full blur-2xl -translate-y-1/2 translate-x-1/2"></div>
                    <div className="flex items-center space-x-4 relative z-10">
                        <div className="w-12 h-12 bg-white text-red-500 rounded-full flex items-center justify-center shadow-inner animate-pulse">
                            <PlayCircle className="w-6 h-6" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold flex items-center space-x-2">
                                <span>Jonli o'yinlar davom etmoqda!</span>
                            </h2>
                            <p className="text-red-100">Hozirda {liveMatches.length} ta o'yin bo'lib o'tmoqda.</p>
                        </div>
                    </div>
                    <Link to="/matches?tab=live" className="px-6 py-2 bg-white text-red-600 font-bold rounded-lg hover:bg-red-50 transition-colors shadow-md relative z-10">
                        Tomosha qilish
                    </Link>
                </section>
            )}

            {/* LEAGUES SECTION */}
            <section id="leagues" className="scroll-mt-24">
                <div className="mb-6 flex items-center space-x-3">
                    <Trophy className="w-8 h-8 text-emerald-500" />
                    <h2 className="text-3xl font-extrabold text-gray-900 dark:text-white">Top Ligalar</h2>
                </div>

                <div className="flex flex-col gap-6">
                    {leagues.map((league) => {
                        const meta = LEAGUE_META[league.code] || {
                            title: league.name_en,
                            desc: `${league.country} davlatining yetakchi ligasi.`,
                            bgImage: 'https://images.unsplash.com/photo-1518605368461-1ee12523f05f?auto=format&fit=crop&q=80&w=2000',
                            logo: league.emblem_local || ''
                        };

                        return (
                            <Link
                                key={league.id}
                                to={`/league/${league.id}`}
                                className="group relative w-full h-[300px] sm:h-[250px] rounded-3xl overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-500 flex flex-col justify-end"
                            >
                                {/* Background Image with Parallax subtle effect on hover */}
                                <div className="absolute inset-0 w-full h-full">
                                    <img
                                        src={meta.bgImage}
                                        alt={meta.title}
                                        className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-700 ease-in-out"
                                    />
                                    {/* Overlay Gradient for readability */}
                                    <div className="absolute inset-0 bg-gradient-to-t from-gray-900 via-gray-900/80 to-transparent"></div>
                                    <div className="absolute inset-0 bg-emerald-900/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                                </div>

                                {/* Content overlaid on image */}
                                <div className="relative z-10 p-6 sm:p-8 flex flex-col sm:flex-row items-start sm:items-end justify-between gap-4 h-full">
                                    <div className="flex-1">
                                        <div className="flex items-center space-x-4 mb-3">
                                            {/* League Logo isolated within a glassmorphism circle */}
                                            <div className="w-16 h-16 bg-white/10 backdrop-blur-md rounded-2xl border border-white/20 p-2 shadow-xl flex items-center justify-center group-hover:-translate-y-1 transition-transform">
                                                <img
                                                    src={meta.logo || league.emblem_local || ''}
                                                    alt={meta.title}
                                                    className="w-full h-full object-contain filter drop-shadow-md"
                                                />
                                            </div>
                                            <div className="flex flex-col">
                                                <span className="text-xs font-bold text-emerald-300 uppercase tracking-wider mb-1 flex items-center space-x-1">
                                                    <MapPin className="w-3 h-3" />
                                                    <span>{league.country}</span>
                                                </span>
                                                <h3 className="text-2xl sm:text-3xl font-extrabold text-white text-shadow-sm group-hover:text-emerald-300 transition-colors">
                                                    {meta.title}
                                                </h3>
                                            </div>
                                        </div>
                                        <p className="text-gray-300 text-sm sm:text-base max-w-2xl line-clamp-2 pr-4 pl-[80px]">
                                            {meta.desc}
                                        </p>
                                    </div>

                                    {/* Action & Stats Side */}
                                    <div className="flex flex-row sm:flex-col items-center sm:items-end justify-between w-full sm:w-auto mt-4 sm:mt-0 gap-4">
                                        {league.current_matchday && (
                                            <div className="px-4 py-2 bg-black/40 backdrop-blur-md rounded-xl border border-white/10 text-white font-medium flex items-center space-x-2">
                                                <Calendar className="w-4 h-4 text-emerald-400" />
                                                <span>{league.current_matchday}-tur ketyapti</span>
                                            </div>
                                        )}
                                        <div className="w-12 h-12 rounded-full bg-emerald-500 text-white flex items-center justify-center shadow-lg group-hover:scale-110 group-hover:bg-emerald-400 transition-all duration-300">
                                            <ArrowRight className="w-5 h-5" />
                                        </div>
                                    </div>
                                </div>
                            </Link>
                        );
                    })}
                </div>
            </section>
        </div>
    );
};

export default Home;
