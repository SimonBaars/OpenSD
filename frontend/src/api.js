const API_BASE = import.meta.env.VITE_API_URL || '/api';

export async function fetchVotes(params = {}) {
  const url = new URL(`${API_BASE}/votes`, window.location.origin);
  Object.entries(params).forEach(([k, v]) => {
    if (v) url.searchParams.set(k, v);
  });
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to fetch votes: ${res.status}`);
  return res.json();
}

export async function fetchMembers() {
  const res = await fetch(`${API_BASE}/members`);
  if (!res.ok) throw new Error(`Failed to fetch members: ${res.status}`);
  return res.json();
}

export async function fetchMemberProfile(id) {
  const res = await fetch(`${API_BASE}/members/${id}/profile`);
  if (!res.ok) throw new Error(`Failed to fetch member profile: ${res.status}`);
  return res.json();
}

export async function fetchHeatmap() {
  const res = await fetch(`${API_BASE}/heatmap`);
  if (!res.ok) throw new Error(`Failed to fetch heatmap: ${res.status}`);
  return res.json();
}
