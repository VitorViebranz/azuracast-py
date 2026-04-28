import useAuthStore from '../store/authStore';

export default function HomePage() {
  const { user } = useAuthStore();

  return (
    <div style={{ padding: '2rem' }}>
      <h1 style={{ marginBottom: '1rem', color: '#333' }}>Welcome to AzuraCast-py</h1>
      {user && (
        <p style={{ color: '#666', fontSize: '1.1rem' }}>
          Hello, <strong>{user.display_name || user.username}</strong>! You are logged in as {user.email}.
        </p>
      )}
      <div style={{ marginTop: '2rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '1rem' }}>
        {['Stations', 'Users', 'Settings', 'Analytics'].map((item) => (
          <div key={item} style={{ background: 'white', padding: '1.5rem', borderRadius: '8px', boxShadow: '0 1px 4px rgba(0,0,0,0.1)', textAlign: 'center' }}>
            <h3 style={{ color: '#444' }}>{item}</h3>
            <p style={{ color: '#888', fontSize: '0.9rem' }}>Manage {item.toLowerCase()}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
