import { Outlet, Link, useLocation } from 'react-router-dom';
import { Home, Trophy, Calendar, Users } from 'lucide-react';

const Layout = () => {
    const location = useLocation();

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 font-sans transition-colors duration-200 flex flex-col">
            <header className="sticky top-0 z-50 bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-700 shadow-sm">
                <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                    <Link to="/" className="flex items-center space-x-2 group">
                        <div className="bg-gradient-to-tr from-emerald-500 to-teal-400 p-2 rounded-lg shadow-lg group-hover:shadow-emerald-500/30 transition-all duration-300">
                            <Trophy className="w-6 h-6 text-white" />
                        </div>
                        <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-600 to-teal-500 dark:from-emerald-400 dark:to-teal-300">
                            FCS
                        </span>
                    </Link>

                    <nav className="hidden md:flex items-center space-x-1">
                        <Link to="/" className={`px-4 py-2 rounded-md transition-colors flex items-center space-x-2 text-sm font-medium ${location.pathname === '/' ? 'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}`}>
                            <Home className="w-4 h-4" />
                            <span>Bosh sahifa</span>
                        </Link>
                        <Link to="/clubs" className={`px-4 py-2 rounded-md transition-colors flex items-center space-x-2 text-sm font-medium ${location.pathname.startsWith('/clubs') ? 'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}`}>
                            <Users className="w-4 h-4" />
                            <span>Jamoalar</span>
                        </Link>
                        <Link to="/matches" className={`px-4 py-2 rounded-md transition-colors flex items-center space-x-2 text-sm font-medium ${location.pathname.startsWith('/matches') ? 'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}`}>
                            <Calendar className="w-4 h-4" />
                            <span>O'yinlar</span>
                        </Link>
                    </nav>

                    <div className="flex items-center space-x-4">
                        {/* Actions can be added here */}
                    </div>
                </div>
            </header>

            <main className="container mx-auto px-4 py-8 flex-1">
                <Outlet />
            </main>

            <footer className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 py-8 mt-auto">
                <div className="container mx-auto px-4 text-center text-gray-500 dark:text-gray-400 text-sm">
                    <p>&copy; {new Date().getFullYear()} FCS - Football Club Standings. All rights reserved.</p>
                </div>
            </footer>
        </div>
    );
};

export default Layout;
