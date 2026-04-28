import { useUsers } from '../api/users';
import useAuthStore from '../store/authStore';

export default function UsersPage() {
  const { user: currentUser } = useAuthStore();
  const { data: users, isLoading, error } = useUsers();

  return (
    <div style={{ padding: '2rem' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ color: '#333', margin: 0 }}>👥 Users</h1>
      </div>

      {isLoading && <p style={{ color: '#666' }}>Loading users...</p>}
      {error && <p style={{ color: 'red' }}>Failed to load users. You may not have permission to view this list.</p>}

      {users && users.length > 0 && (
        <div style={{ background: 'white', borderRadius: '8px', boxShadow: '0 1px 4px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#f8f9fa', borderBottom: '2px solid #dee2e6' }}>
                <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: '#555', fontWeight: 600 }}>User</th>
                <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: '#555', fontWeight: 600 }}>Email</th>
                <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: '#555', fontWeight: 600 }}>Roles</th>
                <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: '#555', fontWeight: 600 }}>Status</th>
                <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: '#555', fontWeight: 600 }}>Admin</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u, idx) => (
                <tr
                  key={u.id}
                  style={{
                    borderBottom: '1px solid #dee2e6',
                    background: u.id === currentUser?.id ? '#f0f7ff' : idx % 2 === 0 ? 'white' : '#fafafa',
                  }}
                >
                  <td style={{ padding: '0.75rem 1rem' }}>
                    <div style={{ fontWeight: 500, color: '#333' }}>
                      {u.display_name || u.username}
                      {u.id === currentUser?.id && (
                        <span style={{ marginLeft: '0.5rem', fontSize: '0.75rem', background: '#cce5ff', color: '#004085', padding: '0.1rem 0.4rem', borderRadius: '10px' }}>
                          You
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: '#888' }}>@{u.username}</div>
                  </td>
                  <td style={{ padding: '0.75rem 1rem', color: '#555' }}>{u.email}</td>
                  <td style={{ padding: '0.75rem 1rem' }}>
                    {u.roles.length === 0 ? (
                      <span style={{ color: '#aaa', fontSize: '0.85rem' }}>—</span>
                    ) : (
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                        {u.roles.map((r) => (
                          <span
                            key={r.id}
                            style={{ background: '#e2e3e5', color: '#383d41', padding: '0.1rem 0.5rem', borderRadius: '10px', fontSize: '0.75rem' }}
                          >
                            {r.name}
                          </span>
                        ))}
                      </div>
                    )}
                  </td>
                  <td style={{ padding: '0.75rem 1rem' }}>
                    <span
                      style={{
                        display: 'inline-block',
                        padding: '0.2rem 0.5rem',
                        borderRadius: '12px',
                        fontSize: '0.75rem',
                        background: u.is_active ? '#d4edda' : '#f8d7da',
                        color: u.is_active ? '#155724' : '#721c24',
                      }}
                    >
                      {u.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td style={{ padding: '0.75rem 1rem' }}>
                    {u.is_super_admin ? (
                      <span style={{ color: '#e83e8c', fontWeight: 500, fontSize: '0.85rem' }}>⭐ Super Admin</span>
                    ) : (
                      <span style={{ color: '#aaa', fontSize: '0.85rem' }}>—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {users && users.length === 0 && (
        <p style={{ color: '#888' }}>No users found.</p>
      )}
    </div>
  );
}
