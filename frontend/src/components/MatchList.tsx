import React from 'react';
import { Calendar } from 'lucide-react';
import { Link } from 'react-router-dom';

interface Match {
    id: number;
    utc_date: string;
    status: string;
    matchday: number;
    home_team_id: number;
    home_team_name: string;
    away_team_id: number;
    away_team_name: string;
    home_team_crest: string | null;
    away_team_crest: string | null;
    home_score: number | null;
    away_score: number | null;
}

interface MatchListProps {
    matches: Match[];
}

const MatchList: React.FC<MatchListProps> = ({ matches }) => {
    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('uz-UZ', {
            weekday: 'short',
            day: 'numeric',
            month: 'short',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'FINISHED': return 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300';
            case 'IN_PLAY':
            case 'PAUSED': return 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400 animate-pulse';
            case 'SCHEDULED':
            case 'TIMED': return 'bg-emerald-100 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400';
            default: return 'bg-gray-100 text-gray-500';
        }
    };

    const getStatusText = (status: string) => {
        switch (status) {
            case 'FINISHED': return 'Tugatilgan';
            case 'IN_PLAY': return 'Jonli';
            case 'PAUSED': return 'Tanaffus';
            case 'SCHEDULED':
            case 'TIMED': return 'Rejalashtirilgan';
            case 'POSTPONED': return 'Qoldirilgan';
            default: return status;
        }
    };

    return (
        <div className="space-y-4">
            {matches.map((match) => (
                <div key={match.id} className="bg-white dark:bg-gray-800 rounded-xl shadow-sm hover:shadow-md transition-shadow border border-gray-200 dark:border-gray-700 p-4">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
                            <Calendar className="w-4 h-4" />
                            <span>{formatDate(match.utc_date)}</span>
                            <span className="mx-1">•</span>
                            <span>Tur {match.matchday}</span>
                        </div>
                        <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${getStatusColor(match.status)}`}>
                            {getStatusText(match.status)}
                        </span>
                    </div>

                    <div className="flex items-center justify-between">
                        {/* Home Team */}
                        <div className="flex-1 flex justify-end">
                            <Link to={`/club/${match.home_team_id}`} className="group flex items-center space-x-3 text-right">
                                <span className="font-semibold text-gray-900 dark:text-white hidden sm:block group-hover:text-emerald-500 transition-colors">{match.home_team_name}</span>
                                <div className="w-10 h-10 p-1 bg-gray-50 dark:bg-gray-700/50 rounded-full border border-gray-100 dark:border-gray-600 group-hover:border-emerald-500 transition-colors">
                                    {match.home_team_crest ? (
                                        <img src={match.home_team_crest} alt={match.home_team_name} className="w-full h-full object-contain" />
                                    ) : (
                                        <div className="w-full h-full bg-gray-200 rounded-full"></div>
                                    )}
                                </div>
                                <span className="font-semibold text-gray-900 dark:text-white sm:hidden group-hover:text-emerald-500 transition-colors">{match.home_team_name.slice(0, 3).toUpperCase()}</span>
                            </Link>
                        </div>

                        {/* Score / VS */}
                        <div className="px-6 flex flex-col items-center">
                            {match.status === 'FINISHED' || match.status === 'IN_PLAY' || match.status === 'PAUSED' ? (
                                <div className="text-2xl font-bold text-gray-900 dark:text-white tracking-widest bg-gray-50 dark:bg-gray-700/50 px-4 py-1 rounded-lg">
                                    {match.home_score} - {match.away_score}
                                </div>
                            ) : (
                                <div className="text-lg font-bold text-gray-400 bg-gray-50 dark:bg-gray-700/30 px-3 py-1 rounded-lg">
                                    VS
                                </div>
                            )}
                        </div>

                        {/* Away Team */}
                        <div className="flex-1 flex justify-start">
                            <Link to={`/club/${match.away_team_id}`} className="group flex items-center space-x-3 text-left">
                                <div className="w-10 h-10 p-1 bg-gray-50 dark:bg-gray-700/50 rounded-full border border-gray-100 dark:border-gray-600 group-hover:border-emerald-500 transition-colors">
                                    {match.away_team_crest ? (
                                        <img src={match.away_team_crest} alt={match.away_team_name} className="w-full h-full object-contain" />
                                    ) : (
                                        <div className="w-full h-full bg-gray-200 rounded-full"></div>
                                    )}
                                </div>
                                <span className="font-semibold text-gray-900 dark:text-white hidden sm:block group-hover:text-emerald-500 transition-colors">{match.away_team_name}</span>
                                <span className="font-semibold text-gray-900 dark:text-white sm:hidden group-hover:text-emerald-500 transition-colors">{match.away_team_name.slice(0, 3).toUpperCase()}</span>
                            </Link>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default MatchList;
