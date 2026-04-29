/**
 * uDos System Widgets — embeddable dashboard widgets
 *
 * These widgets can be injected into any surface (BBC BASIC, NES Dashboard, Ceefax)
 * to show live system data: vault stats, snack count, MCP status, etc.
 */

(function(global) {
  'use strict';

  const uDosWidgets = {};

  // ── Data Sources ────────────────────────────────────────────────────────

  /** Simulated system metrics for demo/fallback */
  function getDemoMetrics() {
    return {
      vaultNotes: Math.floor(Math.random() * 300) + 100,
      snacks: Math.floor(Math.random() * 20) + 5,
      relics: Math.floor(Math.random() * 15) + 3,
      mcpStatus: Math.random() > 0.2 ? 'connected' : 'disconnected',
      uptime: formatUptime(Math.floor(Math.random() * 86400 * 7)),
      lastActivity: `${Math.floor(Math.random() * 6) + 1}h ago`,
      cpuLoad: Math.floor(Math.random() * 60) + 20,
    };
  }

  function formatUptime(seconds) {
    const d = Math.floor(seconds / 86400);
    const h = Math.floor((seconds % 86400) / 3600);
    if (d > 0) return `${d}d ${h}h`;
    const m = Math.floor((seconds % 3600) / 60);
    return `${h}h ${m}m`;
  }

  // ── Widget Renderers ────────────────────────────────────────────────────

  /** System status badge */
  uDosWidgets.statusBadge = function(metrics) {
    const status = metrics.mcpStatus;
    const color = status === 'connected' ? '#00cc00' : '#ff4444';
    const label = status === 'connected' ? 'ONLINE' : 'OFFLINE';
    return `<span style="display:inline-block;padding:2px 8px;border-radius:3px;background:${color};color:#fff;font-size:11px;font-weight:bold;">${label}</span>`;
  };

  /** Mini CPU gauge as a CSS bar */
  uDosWidgets.cpuGauge = function(metrics) {
    const pct = metrics.cpuLoad;
    const color = pct > 80 ? '#ff4444' : pct > 50 ? '#ffaa00' : '#00cc00';
    return `
      <div style="margin:4px 0;">
        <div style="font-size:10px;color:#888;margin-bottom:2px;">CPU ${pct}%</div>
        <div style="background:#333;height:8px;border-radius:4px;overflow:hidden;">
          <div style="width:${pct}%;height:100%;background:${color};border-radius:4px;transition:width 1s;"></div>
        </div>
      </div>
    `;
  };

  /** Stat card (key-value pair) */
  uDosWidgets.statCard = function(label, value, icon) {
    return `
      <div style="display:flex;align-items:center;gap:8px;padding:8px;background:rgba(255,255,255,0.05);border-radius:6px;margin:4px 0;">
        <span style="font-size:20px;">${icon || '📊'}</span>
        <div style="flex:1;">
          <div style="font-size:10px;color:#888;text-transform:uppercase;">${label}</div>
          <div style="font-size:16px;font-weight:bold;color:#e0e0e0;">${value}</div>
        </div>
      </div>
    `;
  };

  /** Full system dashboard panel */
  uDosWidgets.fullDashboard = function(metrics) {
    if (!metrics) metrics = getDemoMetrics();
    return `
      <div style="font-family:system-ui,sans-serif;background:#1a1a2e;padding:16px;border-radius:8px;border:1px solid #333;">
        <h3 style="margin:0 0 12px 0;color:#e94560;font-size:14px;text-transform:uppercase;letter-spacing:1px;">
          ⚡ System Dashboard
        </h3>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
          ${uDosWidgets.statCard('Vault Notes', metrics.vaultNotes, '💾')}
          ${uDosWidgets.statCard('Snacks', metrics.snacks, '⚡')}
          ${uDosWidgets.statCard('Relics', metrics.relics, '📦')}
          ${uDosWidgets.statCard('Uptime', metrics.uptime, '⏱️')}
        </div>
        ${uDosWidgets.cpuGauge(metrics)}
        <div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px;padding-top:8px;border-top:1px solid #333;">
          <span style="font-size:11px;color:#888;">MCP: ${uDosWidgets.statusBadge(metrics)}</span>
          <span style="font-size:11px;color:#888;">${metrics.lastActivity}</span>
        </div>
      </div>
    `;
  };

  /** Teletext-style status line */
  uDosWidgets.teletextStatus = function(metrics) {
    if (!metrics) metrics = getDemoMetrics();
    const status = metrics.mcpStatus === 'connected' ? 'ONLINE' : 'OFFLINE';
    return [
      `────────────────────────────────────────────`,
      ` uDos System  |  Notes:${metrics.vaultNotes}  Snacks:${metrics.snacks}  MCP:${status}`,
      `────────────────────────────────────────────`,
    ].join('\n');
  };

  /** Refresh and re-render all widgets on the page */
  uDosWidgets.refreshAll = function() {
    const metrics = getDemoMetrics();
    document.querySelectorAll('[data-udos-widget]').forEach(el => {
      const widget = el.dataset.udosWidget;
      if (typeof uDosWidgets[widget] === 'function') {
        el.innerHTML = uDosWidgets[widget](metrics);
      }
    });
  };

  // Auto-init: render widgets on page load, refresh every 30s
  if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
      uDosWidgets.refreshAll();
      setInterval(uDosWidgets.refreshAll, 30000);
    });
  }

  // Export
  global.uDosWidgets = uDosWidgets;

})(typeof window !== 'undefined' ? window : global);
