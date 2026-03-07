import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchMemberProfile } from '../api';

export default function MemberProfile() {
  const { id } = useParams();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMemberProfile(id)
      .then(setProfile)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="text-center py-20 text-gray-500">Loading profile…</div>;
  if (!profile || profile.error) return <div className="text-center py-20 text-red-500">Member not found</div>;

  return (
    <div className="space-y-8">
      <Link to="/" className="text-blue-600 hover:underline text-sm">← Back to Dashboard</Link>
      <div className="flex items-center gap-6">
        {profile.photo_url && (
          <img src={profile.photo_url} alt={profile.name} className="w-24 h-24 rounded-full object-cover shadow" />
        )}
        <div>
          <h1 className="text-2xl font-bold">{profile.name}</h1>
          <p className="text-gray-500">District {profile.district}</p>
        </div>
      </div>

      {profile.ai_summary && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-1">AI Summary</h3>
          <p className="text-sm text-blue-800">{profile.ai_summary}</p>
        </div>
      )}

      {/* RadarChart and agreement bar chart will go here */}
      <section>
        <h2 className="text-xl font-bold mb-2">Policy Breakdown</h2>
        <div className="bg-white rounded-lg shadow p-6 min-h-[200px] flex items-center justify-center text-gray-400">
          RadarChart placeholder — {profile.policy_breakdown?.length || 0} categories
        </div>
      </section>

      <section>
        <h2 className="text-xl font-bold mb-2">Agreement Rates</h2>
        <div className="bg-white rounded-lg shadow p-6">
          {profile.agreement_rates?.length > 0 ? (
            <div className="space-y-2">
              {profile.agreement_rates.map((a) => (
                <div key={a.member} className="flex items-center gap-3">
                  <span className="w-40 text-sm font-medium">{a.member}</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-4">
                    <div
                      className="bg-blue-600 h-4 rounded-full"
                      style={{ width: `${a.agree_pct}%` }}
                    />
                  </div>
                  <span className="text-sm w-14 text-right">{a.agree_pct}%</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400 text-center">No agreement data yet</p>
          )}
        </div>
      </section>

      <section>
        <h2 className="text-xl font-bold mb-2">Vote History</h2>
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-4 py-2">Date</th>
                <th className="text-left px-4 py-2">Item</th>
                <th className="text-left px-4 py-2">Vote</th>
                <th className="text-left px-4 py-2">Tag</th>
              </tr>
            </thead>
            <tbody>
              {(profile.votes || []).slice(0, 50).map((v, i) => (
                <tr key={i} className="border-t">
                  <td className="px-4 py-2">{v.date}</td>
                  <td className="px-4 py-2">{v.item_title}</td>
                  <td className="px-4 py-2">
                    <span className={`inline-block px-2 py-0.5 rounded text-xs font-semibold
                      ${v.vote === 'yes' ? 'bg-green-100 text-green-800' : ''}
                      ${v.vote === 'no' ? 'bg-red-100 text-red-800' : ''}
                      ${v.vote === 'abstain' ? 'bg-yellow-100 text-yellow-800' : ''}
                      ${v.vote === 'absent' ? 'bg-gray-100 text-gray-500' : ''}
                    `}>
                      {v.vote}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-gray-500">{v.tag || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
