import { Navigate, Outlet, Link } from 'react-router-dom';
import useAuthStore from '../store/authStore';

export default function Layout() {
  const { isAuthenticated, user, logout } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh', fontFamily: 'sans-serif' }}>
      <aside style={{ width: '240px', background: '#1a1a2e', color: 'white', padding: '1rem', display: 'flex', flexDirection: 'column' }}>
        <div style={{ fontSize: '1.2rem', fontWeight: 'bold', marginBottom: '2rem', padding: '0.5rem 0' }}>
          🎙 AzuraCast-py
        </div>
        <nav style={{ flex: 1 }}>
          {[
            { to: '/', label: '🏠 Dashboard' },
            { to: '/stations', label: '📻 Stations' },
            { to: '/users', label: '👥 Users' },
            { to: '/settings', label: '⚙️ Settings' },
          ].map(({ to, label }) => (
            <Link
              key={to}
              to={to}
              style={{ display: 'block', color: '#ccc', textDecoration: 'none', padding: '0.6rem 0.5rem', borderRadius: '4px', marginBottom: '0.25rem' }}
            >
              {label}
            </Link>
          ))}
        </nav>
        <div style={{ borderTop: '1px solid #333', paddingTop: '1rem' }}>
          <div style={{ fontSize: '0.85rem', color: '#aaa', marginBottom: '0.5rem' }}>
            {user?.email}
          </div>
          <button
            onClick={logout}
            style={{ background: 'transparent', border: '1px solid #555', color: '#ccc', padding: '0.4rem 1rem', borderRadius: '4px', cursor: 'pointer', width: '100%' }}
          >
            Sign Out
          </button>
        </div>
      </aside>
      <main style={{ flex: 1, background: '#f5f5f5', overflow: 'auto' }}>
        <Outlet />
      </main>
    </div>
  );
}
