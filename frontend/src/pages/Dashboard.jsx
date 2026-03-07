import { useEffect, useState, useCallback } from 'react';
import { fetchVotes, fetchMembers, fetchHeatmap } from '../api';
import VoteHeatmap from '../components/VoteHeatmap';
import AllianceMatrix from '../components/AllianceMatrix';
import FilterBar from '../components/FilterBar';

export default function Dashboard() {
  const [votes, setVotes] = useState([]);
  const [members, setMembers] = useState([]);
  const [allianceData, setAllianceData] = useState([]);
  const [loading, setLoading] = useState(true);

  // Initial load
  useEffect(() => {
    Promise.all([fetchVotes(), fetchMembers(), fetchHeatmap()])
      .then(([v, m, h]) => {
        setVotes(v);
        setMembers(m);
        setAllianceData(h);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  // Re-fetch votes when filters change
  const handleFilterChange = useCallback((params) => {
    fetchVotes(params).then(setVotes).catch(console.error);
  }, []);

  if (loading) {
    return <div className="text-center py-20 text-gray-500">Loading vote data…</div>;
  }

  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-2xl font-bold mb-2">Council Voting Heatmap</h1>
        <p className="text-gray-600 mb-4">
          Visualize how San Diego's 9 council members vote on every agenda item.
        </p>
        <FilterBar onChange={handleFilterChange} members={members} />
        <div className="bg-white rounded-lg shadow p-6">
          <VoteHeatmap votes={votes} members={members} />
        </div>
      </section>

      <section>
        <h2 className="text-xl font-bold mb-2">Alliance Matrix</h2>
        <p className="text-gray-600 mb-4">
          Pairwise agreement rates between council members.
        </p>
        <div className="bg-white rounded-lg shadow p-6">
          <AllianceMatrix data={allianceData} members={members} />
        </div>
      </section>
    </div>
  );
}
