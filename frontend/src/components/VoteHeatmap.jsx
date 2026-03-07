import { useRef, useEffect, useState } from 'react';
import * as d3 from 'd3';
import { useNavigate } from 'react-router-dom';

const VOTE_COLORS = {
  yes: '#22c55e',
  no: '#ef4444',
  abstain: '#eab308',
  absent: '#d1d5db',
};

const VOTE_LABELS = {
  yes: 'Yes',
  no: 'No',
  abstain: 'Abstain',
  absent: 'Absent',
};

export default function VoteHeatmap({ votes, members }) {
  const svgRef = useRef(null);
  const tooltipRef = useRef(null);
  const containerRef = useRef(null);
  const navigate = useNavigate();
  const [dimensions, setDimensions] = useState({ width: 900, height: 500 });

  // Recompute dimensions on resize
  useEffect(() => {
    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const w = entry.contentRect.width;
        if (w > 0) setDimensions((d) => ({ ...d, width: w }));
      }
    });
    if (containerRef.current) observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!votes.length || !members.length) return;

    const svg = d3.select(svgRef.current);
    const tooltip = d3.select(tooltipRef.current);
    svg.selectAll('*').remove();

    // Sort members by district
    const sortedMembers = [...members].sort((a, b) => a.district - b.district);
    const memberNames = sortedMembers.map((m) => m.name);
    const memberIdMap = Object.fromEntries(members.map((m) => [m.name, m.id]));

    // Group votes by item (date + item_number + item_title)
    const itemMap = new Map();
    for (const v of votes) {
      const key = `${v.date}|${v.item_number}|${v.item_title}`;
      if (!itemMap.has(key)) {
        itemMap.set(key, {
          date: v.date,
          item_number: v.item_number,
          item_title: v.item_title,
          tag: v.tag,
          votes: {},
        });
      }
      itemMap.get(key).votes[v.member_name] = v.vote;
    }

    const items = Array.from(itemMap.values()).sort((a, b) => {
      if (a.date !== b.date) return a.date.localeCompare(b.date);
      return (a.item_number || '').localeCompare(b.item_number || '');
    });

    // Dimensions
    const margin = { top: 10, right: 20, bottom: 80, left: 140 };
    const cellSize = Math.max(4, Math.min(14, (dimensions.width - margin.left - margin.right) / items.length));
    const cellHeight = 28;
    const width = margin.left + items.length * cellSize + margin.right;
    const height = margin.top + memberNames.length * cellHeight + margin.bottom;

    svg.attr('width', width).attr('height', height);

    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

    // Y axis — member names
    memberNames.forEach((name, i) => {
      const label = g
        .append('text')
        .attr('x', -8)
        .attr('y', i * cellHeight + cellHeight / 2)
        .attr('text-anchor', 'end')
        .attr('dominant-baseline', 'middle')
        .attr('font-size', '12px')
        .attr('fill', '#374151')
        .attr('cursor', 'pointer')
        .text(name)
        .on('click', () => {
          const id = memberIdMap[name];
          if (id) navigate(`/member/${id}`);
        });
      label.on('mouseenter', function () {
        d3.select(this).attr('fill', '#2563eb').attr('font-weight', 'bold');
      });
      label.on('mouseleave', function () {
        d3.select(this).attr('fill', '#374151').attr('font-weight', 'normal');
      });
    });

    // Cells
    items.forEach((item, col) => {
      memberNames.forEach((name, row) => {
        const vote = item.votes[name] || 'absent';
        g.append('rect')
          .attr('x', col * cellSize)
          .attr('y', row * cellHeight + 2)
          .attr('width', Math.max(cellSize - 1, 2))
          .attr('height', cellHeight - 4)
          .attr('rx', 1)
          .attr('fill', VOTE_COLORS[vote] || VOTE_COLORS.absent)
          .attr('opacity', 0.9)
          .attr('cursor', 'pointer')
          .on('mouseenter', function (event) {
            d3.select(this).attr('opacity', 1).attr('stroke', '#000').attr('stroke-width', 1.5);
            tooltip
              .style('display', 'block')
              .style('left', `${event.pageX + 12}px`)
              .style('top', `${event.pageY - 10}px`)
              .html(
                `<div class="font-semibold">${name}</div>` +
                `<div class="text-xs text-gray-500">${item.date} · Item ${item.item_number}</div>` +
                `<div class="mt-1">${item.item_title.substring(0, 120)}${item.item_title.length > 120 ? '…' : ''}</div>` +
                `<div class="mt-1 font-semibold" style="color:${VOTE_COLORS[vote]}">${VOTE_LABELS[vote] || vote}</div>` +
                (item.tag ? `<div class="text-xs mt-1 text-blue-600">${item.tag}</div>` : '')
              );
          })
          .on('mousemove', function (event) {
            tooltip.style('left', `${event.pageX + 12}px`).style('top', `${event.pageY - 10}px`);
          })
          .on('mouseleave', function () {
            d3.select(this).attr('opacity', 0.9).attr('stroke', 'none');
            tooltip.style('display', 'none');
          });
      });
    });

    // Date labels on bottom (sampled)
    const dates = [...new Set(items.map((d) => d.date))].sort();
    const datePositions = dates.map((date) => {
      const idx = items.findIndex((i) => i.date === date);
      return { date, x: idx * cellSize };
    });
    // Show every Nth date to avoid crowding
    const step = Math.max(1, Math.floor(datePositions.length / 10));
    datePositions.filter((_, i) => i % step === 0).forEach(({ date, x }) => {
      g.append('text')
        .attr('x', x)
        .attr('y', memberNames.length * cellHeight + 16)
        .attr('text-anchor', 'start')
        .attr('font-size', '10px')
        .attr('fill', '#6b7280')
        .attr('transform', `rotate(45, ${x}, ${memberNames.length * cellHeight + 16})`)
        .text(date);
    });

  }, [votes, members, dimensions, navigate]);

  if (!votes.length) {
    return <div className="text-gray-400 text-center py-10">No vote data available</div>;
  }

  return (
    <div ref={containerRef} className="relative">
      {/* Legend */}
      <div className="flex gap-4 mb-3 text-xs">
        {Object.entries(VOTE_COLORS).map(([key, color]) => (
          <div key={key} className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: color }} />
            <span className="capitalize">{key}</span>
          </div>
        ))}
      </div>
      <div className="overflow-x-auto">
        <svg ref={svgRef} />
      </div>
      <div
        ref={tooltipRef}
        className="fixed z-50 bg-white border border-gray-200 rounded-lg shadow-lg p-3 text-sm max-w-xs pointer-events-none"
        style={{ display: 'none' }}
      />
    </div>
  );
}
