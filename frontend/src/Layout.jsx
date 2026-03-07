import { Link, Outlet } from 'react-router-dom';

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-blue-900 text-white px-6 py-4 shadow-md">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link to="/" className="text-xl font-bold tracking-tight hover:opacity-90">
            🏛️ SD Council Voting Dashboard
          </Link>
          <nav className="flex gap-6 text-sm font-medium">
            <Link to="/" className="hover:text-blue-200">Dashboard</Link>
            <Link to="/members" className="hover:text-blue-200">Members</Link>
          </nav>
        </div>
      </header>
      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-8">
        <Outlet />
      </main>
      <footer className="bg-gray-100 text-center text-xs text-gray-500 py-4">
        Built with public City of San Diego data · Impact Hub Hackathon 2026
      </footer>
    </div>
  );
}
