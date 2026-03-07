import { useState, useEffect } from 'react';

const TAGS = [
  'All Topics',
  'Housing',
  'Public Safety',
  'Climate',
  'Infrastructure',
  'Budget',
  'Transportation',
  'Land Use',
  'Health',
  'Education',
  'Other',
];

export default function FilterBar({ onChange, members }) {
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [tag, setTag] = useState('');
  const [member, setMember] = useState('');

  useEffect(() => {
    const params = {};
    if (dateFrom) params.dateFrom = dateFrom;
    if (dateTo) params.dateTo = dateTo;
    if (tag) params.tag = tag;
    if (member) params.member = member;
    onChange(params);
  }, [dateFrom, dateTo, tag, member]);

  const sortedMembers = members ? [...members].sort((a, b) => a.district - b.district) : [];

  return (
    <div className="flex flex-wrap items-end gap-3 mb-5">
      <div className="flex flex-col">
        <label className="text-xs text-gray-500 mb-1">From</label>
        <input
          type="date"
          value={dateFrom}
          onChange={(e) => setDateFrom(e.target.value)}
          className="border border-gray-300 rounded-md px-2 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>
      <div className="flex flex-col">
        <label className="text-xs text-gray-500 mb-1">To</label>
        <input
          type="date"
          value={dateTo}
          onChange={(e) => setDateTo(e.target.value)}
          className="border border-gray-300 rounded-md px-2 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>
      <div className="flex flex-col">
        <label className="text-xs text-gray-500 mb-1">Policy Topic</label>
        <select
          value={tag}
          onChange={(e) => setTag(e.target.value)}
          className="border border-gray-300 rounded-md px-2 py-1.5 text-sm bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">All Topics</option>
          {TAGS.slice(1).map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
      </div>
      <div className="flex flex-col">
        <label className="text-xs text-gray-500 mb-1">Member</label>
        <select
          value={member}
          onChange={(e) => setMember(e.target.value)}
          className="border border-gray-300 rounded-md px-2 py-1.5 text-sm bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">All Members</option>
          {sortedMembers.map((m) => (
            <option key={m.id} value={m.name}>
              D{m.district} — {m.name}
            </option>
          ))}
        </select>
      </div>
      {(dateFrom || dateTo || tag || member) && (
        <button
          onClick={() => {
            setDateFrom('');
            setDateTo('');
            setTag('');
            setMember('');
          }}
          className="text-sm text-blue-600 hover:text-blue-800 underline pb-1.5"
        >
          Clear filters
        </button>
      )}
    </div>
  );
}
