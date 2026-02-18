import React from 'react';

interface Standing {
    position: number;
    club_name: string;
    club_crest: string | null;
    played: number;
    won: number;
    draw: number;
    lost: number;
    goals_for: number;
    goals_against: number;
    goal_difference: number;
    points: number;
    form: string | null;
}

interface StandingsTableProps {
    standings: Standing[];
}

const StandingsTable: React.FC<StandingsTableProps> = ({ standings }) => {
    const getFormColor = (char: string) => {
        switch (char) {
            case 'W': return 'bg-emerald-500 text-white';
            case 'D': return 'bg-gray-400 text-white';
            case 'L': return 'bg-red-500 text-white';
            default: return 'bg-gray-200 text-gray-600';
        }
    };

    return (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                    <thead className="bg-gray-50 dark:bg-gray-700/50 text-gray-500 dark:text-gray-400 font-medium border-b border-gray-200 dark:border-gray-700">
                        <tr>
                            <th className="px-4 py-3 text-center w-12">#</th>
                            <th className="px-4 py-3">Klub</th>
                            <th className="px-4 py-3 text-center" title="O'yinlar">O'</th>
                            <th className="px-4 py-3 text-center hidden sm:table-cell" title="G'alaba">G'</th>
                            <th className="px-4 py-3 text-center hidden sm:table-cell" title="Durang">D</th>
                            <th className="px-4 py-3 text-center hidden sm:table-cell" title="Mag'lubiyat">M</th>
                            <th className="px-4 py-3 text-center hidden md:table-cell">T/F</th>
                            <th className="px-4 py-3 text-center font-bold">O</th>
                            <th className="px-4 py-3 text-center hidden lg:table-cell">Form</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                        {standings.map((team) => (
                            <tr key={team.position} className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                                <td className="px-4 py-3 text-center font-medium text-gray-900 dark:text-white">
                                    {team.position}
                                </td>
                                <td className="px-4 py-3">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-8 h-8 flex-shrink-0 bg-white dark:bg-gray-700 p-1 rounded-full border border-gray-100 dark:border-gray-600">
                                            {team.club_crest ? (
                                                <img src={team.club_crest} alt={team.club_name} className="w-full h-full object-contain" />
                                            ) : (
                                                <div className="w-full h-full bg-gray-200 rounded-full"></div>
                                            )}
                                        </div>
                                        <span className="font-semibold text-gray-900 dark:text-white truncate max-w-[150px] sm:max-w-xs">{team.club_name}</span>
                                    </div>
                                </td>
                                <td className="px-4 py-3 text-center">{team.played}</td>
                                <td className="px-4 py-3 text-center hidden sm:table-cell">{team.won}</td>
                                <td className="px-4 py-3 text-center hidden sm:table-cell">{team.draw}</td>
                                <td className="px-4 py-3 text-center hidden sm:table-cell">{team.lost}</td>
                                <td className="px-4 py-3 text-center hidden md:table-cell space-x-1">
                                    <span className="text-gray-900 dark:text-white font-medium">{team.goals_for}</span>
                                    <span className="text-gray-400">-</span>
                                    <span className="text-gray-500 dark:text-gray-400">{team.goals_against}</span>
                                    <span className={`text-xs ml-1 px-1.5 py-0.5 rounded ${team.goal_difference > 0 ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' : team.goal_difference < 0 ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'}`}>
                                        {team.goal_difference > 0 ? '+' : ''}{team.goal_difference}
                                    </span>
                                </td>
                                <td className="px-4 py-3 text-center font-bold text-gray-900 dark:text-white text-base">
                                    {team.points}
                                </td>
                                <td className="px-4 py-3 hidden lg:table-cell">
                                    <div className="flex items-center justify-center space-x-1">
                                        {team.form ? team.form.split(',').map((char, idx) => (
                                            <span
                                                key={idx}
                                                className={`w-6 h-6 flex items-center justify-center rounded text-xs font-bold ${getFormColor(char)}`}
                                                title={char === 'W' ? "G'alaba" : char === 'D' ? 'Durang' : "Mag'lubiyat"}
                                            >
                                                {char}
                                            </span>
                                        )) : <span className="text-gray-400">-</span>}
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default StandingsTable;
