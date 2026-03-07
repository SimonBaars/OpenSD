import { useRef, useEffect, useState } from 'react';
import * as d3 from 'd3';
import { useNavigate } from 'react-router-dom';

export default function AllianceMatrix({ data, members }) {
  const svgRef = useRef(null);
  const tooltipRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!data.length || !members.length) return;

    const svg = d3.select(svgRef.current);
    const tooltip = d3.select(tooltipRef.current);
    svg.selectAll('*').remove();

    const sortedMembers = [...members].sort((a, b) => a.district - b.district);
    const names = sortedMembers.map((m) => m.name);
    const memberIdMap = Object.fromEntries(members.map((m) => [m.name, m.id]));
    const n = names.length;

    // Build lookup from pair data
    const pairLookup = {};
    for (const d of data) {
      pairLookup[`${d.member_a}|${d.member_b}`] = d;
      pairLookup[`${d.member_b}|${d.member_a}`] = { ...d, member_a: d.member_b, member_b: d.member_a };
    }

    const cellSize = 56;
    const margin = { top: 130, right: 20, bottom: 20, left: 140 };
    const width = margin.left + n * cellSize + margin.right;
    const height = margin.top + n * cellSize + margin.bottom;

    svg.attr('width', width).attr('height', height);

    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

    // Color scale: red (low agreement) → yellow (mid) → green (high)
    const colorScale = d3
      .scaleSequential(d3.interpolateRdYlGn)
      .domain([50, 100]);

    // Row labels (left)
    names.forEach((name, i) => {
      const lastName = name.split(' ').pop();
      const label = g
        .append('text')
        .attr('x', -8)
        .attr('y', i * cellSize + cellSize / 2)
        .attr('text-anchor', 'end')
        .attr('dominant-baseline', 'middle')
        .attr('font-size', '11px')
        .attr('fill', '#374151')
        .attr('cursor', 'pointer')
        .text(lastName)
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

    // Column labels (top, rotated)
    names.forEach((name, j) => {
      const lastName = name.split(' ').pop();
      g.append('text')
        .attr('x', 0)
        .attr('y', 0)
        .attr('text-anchor', 'start')
        .attr('dominant-baseline', 'middle')
        .attr('font-size', '11px')
        .attr('fill', '#374151')
        .attr('transform', `translate(${j * cellSize + cellSize / 2}, -8) rotate(-45)`)
        .text(lastName);
    });

    // Draw cells
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        const isSelf = i === j;
        const key = `${names[i]}|${names[j]}`;
        const pair = pairLookup[key];
        const pct = isSelf ? 100 : pair ? pair.agree_pct : null;

        // Cell background
        g.append('rect')
          .attr('x', j * cellSize + 1)
          .attr('y', i * cellSize + 1)
          .attr('width', cellSize - 2)
          .attr('height', cellSize - 2)
          .attr('rx', 4)
          .attr('fill', isSelf ? '#e5e7eb' : pct != null ? colorScale(pct) : '#f9fafb')
          .attr('stroke', '#fff')
          .attr('stroke-width', 1)
          .attr('cursor', isSelf ? 'default' : 'pointer')
          .attr('opacity', 0.9)
          .on('mouseenter', function (event) {
            if (isSelf) return;
            d3.select(this).attr('opacity', 1).attr('stroke', '#1e3a5f').attr('stroke-width', 2);
            tooltip
              .style('display', 'block')
              .style('left', `${event.pageX + 14}px`)
              .style('top', `${event.pageY - 10}px`)
              .html(
                `<div class="font-semibold">${names[i]} &amp; ${names[j]}</div>` +
                (pair
                  ? `<div class="mt-1">Agreement: <span class="font-bold">${pct.toFixed(1)}%</span></div>` +
                    `<div class="text-xs text-gray-500">${pair.agree_count} of ${pair.shared_votes} shared votes</div>`
                  : `<div class="text-xs text-gray-400">No shared votes</div>`)
              );
          })
          .on('mousemove', function (event) {
            tooltip.style('left', `${event.pageX + 14}px`).style('top', `${event.pageY - 10}px`);
          })
          .on('mouseleave', function () {
            d3.select(this).attr('opacity', 0.9).attr('stroke', '#fff').attr('stroke-width', 1);
            tooltip.style('display', 'none');
          });

        // Percentage label
        if (pct != null && !isSelf) {
          g.append('text')
            .attr('x', j * cellSize + cellSize / 2)
            .attr('y', i * cellSize + cellSize / 2)
            .attr('text-anchor', 'middle')
            .attr('dominant-baseline', 'middle')
            .attr('font-size', '11px')
            .attr('font-weight', '600')
            .attr('fill', pct > 75 ? '#14532d' : pct < 60 ? '#7f1d1d' : '#713f12')
            .attr('pointer-events', 'none')
            .text(`${Math.round(pct)}%`);
        }
      }
    }

    // Legend gradient
    const legendWidth = 200;
    const legendHeight = 12;
    const defs = svg.append('defs');
    const linearGradient = defs
      .append('linearGradient')
      .attr('id', 'alliance-legend-gradient');
    linearGradient.append('stop').attr('offset', '0%').attr('stop-color', colorScale(50));
    linearGradient.append('stop').attr('offset', '50%').attr('stop-color', colorScale(75));
    linearGradient.append('stop').attr('offset', '100%').attr('stop-color', colorScale(100));

    const legendG = svg
      .append('g')
      .attr('transform', `translate(${margin.left}, ${height - 10})`);
    legendG
      .append('rect')
      .attr('width', legendWidth)
      .attr('height', legendHeight)
      .attr('rx', 3)
      .style('fill', 'url(#alliance-legend-gradient)');
    legendG
      .append('text')
      .attr('x', 0)
      .attr('y', -4)
      .attr('font-size', '10px')
      .attr('fill', '#6b7280')
      .text('50%');
    legendG
      .append('text')
      .attr('x', legendWidth)
      .attr('y', -4)
      .attr('text-anchor', 'end')
      .attr('font-size', '10px')
      .attr('fill', '#6b7280')
      .text('100%');
    legendG
      .append('text')
      .attr('x', legendWidth / 2)
      .attr('y', -4)
      .attr('text-anchor', 'middle')
      .attr('font-size', '10px')
      .attr('fill', '#6b7280')
      .text('Agreement');

  }, [data, members, navigate]);

  if (!data.length) {
    return <div className="text-gray-400 text-center py-10">No alliance data available</div>;
  }

  return (
    <div className="relative">
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
