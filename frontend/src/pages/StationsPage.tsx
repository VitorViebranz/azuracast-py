import { useState } from 'react';
import { useStations, useCreateStation, useDeleteStation } from '../api/stations';
import useAuthStore from '../store/authStore';

export default function StationsPage() {
  const { user } = useAuthStore();
  const { data: stations, isLoading, error } = useStations();
  const createStation = useCreateStation();
  const deleteStation = useDeleteStation();

  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState('');
  const [shortName, setShortName] = useState('');
  const [description, setDescription] = useState('');
  const [formError, setFormError] = useState('');

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError('');
    try {
      await createStation.mutateAsync({ name, short_name: shortName, description: description || undefined });
      setName('');
      setShortName('');
      setDescription('');
      setShowForm(false);
    } catch {
      setFormError('Failed to create station. Short name may already be in use.');
    }
  };

  const handleDelete = async (id: string, stationName: string) => {
    if (!window.confirm(`Delete station "${stationName}"?`)) return;
    try {
      await deleteStation.mutateAsync(id);
    } catch {
      alert('Failed to delete station.');
    }
  };

  return (
    <div style={{ padding: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h1 style={{ color: '#333', margin: 0 }}>📻 Stations</h1>
        {user?.is_super_admin && (
          <button
            onClick={() => setShowForm(!showForm)}
            style={{ background: '#007bff', color: 'white', border: 'none', borderRadius: '4px', padding: '0.5rem 1rem', cursor: 'pointer' }}
          >
            {showForm ? 'Cancel' : '+ New Station'}
          </button>
        )}
      </div>

      {showForm && (
        <div style={{ background: 'white', padding: '1.5rem', borderRadius: '8px', boxShadow: '0 1px 4px rgba(0,0,0,0.1)', marginBottom: '1.5rem' }}>
          <h3 style={{ marginTop: 0 }}>Create Station</h3>
          {formError && <div style={{ color: 'red', marginBottom: '1rem' }}>{formError}</div>}
          <form onSubmit={handleCreate}>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.25rem', color: '#555' }}>Name *</label>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ccc', borderRadius: '4px', boxSizing: 'border-box' }}
              />
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.25rem', color: '#555' }}>Short Name *</label>
              <input
                value={shortName}
                onChange={(e) => setShortName(e.target.value)}
                required
                placeholder="e.g. my-radio"
                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ccc', borderRadius: '4px', boxSizing: 'border-box' }}
              />
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.25rem', color: '#555' }}>Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ccc', borderRadius: '4px', boxSizing: 'border-box', resize: 'vertical' }}
              />
            </div>
            <button
              type="submit"
              disabled={createStation.isPending}
              style={{ background: '#28a745', color: 'white', border: 'none', borderRadius: '4px', padding: '0.5rem 1.5rem', cursor: 'pointer' }}
            >
              {createStation.isPending ? 'Creating...' : 'Create Station'}
            </button>
          </form>
        </div>
      )}

      {isLoading && <p style={{ color: '#666' }}>Loading stations...</p>}
      {error && <p style={{ color: 'red' }}>Failed to load stations.</p>}

      {stations && stations.length === 0 && (
        <p style={{ color: '#888' }}>No stations yet. {user?.is_super_admin ? 'Create one above.' : ''}</p>
      )}

      {stations && stations.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
          {stations.map((station) => (
            <div key={station.id} style={{ background: 'white', padding: '1.5rem', borderRadius: '8px', boxShadow: '0 1px 4px rgba(0,0,0,0.1)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <h3 style={{ margin: '0 0 0.25rem', color: '#333' }}>{station.name}</h3>
                  <code style={{ fontSize: '0.8rem', color: '#666', background: '#f0f0f0', padding: '0.1rem 0.4rem', borderRadius: '3px' }}>
                    {station.short_name}
                  </code>
                </div>
                <span
                  style={{
                    display: 'inline-block',
                    padding: '0.2rem 0.5rem',
                    borderRadius: '12px',
                    fontSize: '0.75rem',
                    background: station.is_enabled ? '#d4edda' : '#f8d7da',
                    color: station.is_enabled ? '#155724' : '#721c24',
                  }}
                >
                  {station.is_enabled ? 'Enabled' : 'Disabled'}
                </span>
              </div>
              {station.description && (
                <p style={{ color: '#666', fontSize: '0.9rem', margin: '0.75rem 0 0' }}>{station.description}</p>
              )}
              <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem', fontSize: '0.85rem', color: '#777' }}>
                <span>🕐 {station.timezone}</span>
                <span>⚡ {station.max_bitrate} kbps</span>
                <span>🔌 {station.mount_points?.length ?? 0} mounts</span>
              </div>
              {user?.is_super_admin && (
                <div style={{ marginTop: '1rem', borderTop: '1px solid #eee', paddingTop: '0.75rem' }}>
                  <button
                    onClick={() => handleDelete(station.id, station.name)}
                    disabled={deleteStation.isPending}
                    style={{ background: 'transparent', border: '1px solid #dc3545', color: '#dc3545', borderRadius: '4px', padding: '0.3rem 0.75rem', cursor: 'pointer', fontSize: '0.85rem' }}
                  >
                    Delete
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
