import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchMembers } from '../api';

export default function MembersList() {
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMembers()
      .then(setMembers)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-center py-20 text-gray-500">Loading members…</div>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Council Members</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {members.map((m) => (
          <Link
            key={m.id}
            to={`/member/${m.id}`}
            className="bg-white rounded-lg shadow p-5 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center gap-4">
              {m.photo_url ? (
                <img src={m.photo_url} alt={m.name} className="w-14 h-14 rounded-full object-cover" />
              ) : (
                <div className="w-14 h-14 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-lg">
                  {m.name?.charAt(0)}
                </div>
              )}
              <div>
                <h3 className="font-semibold">{m.name}</h3>
                <p className="text-sm text-gray-500">District {m.district}</p>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
