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

  // ── Display Scaling ─────────────────────────────────────────────────────

  /**
   * uDosDisplay — BBC/C64-style proportional grid scaling.
   *
   * Formula (per spec):
   *   Terminal occupies 80% of the smaller viewport dimension.
   *   cell_size = terminal_width / cols
   *   font_size = cell_size × 0.75
   *
   * Usage:
   *   uDosWidgets.Display.init(document.getElementById('terminal'), {
   *     cols: 80, rows: 24, baseFont: 24
   *   });
   */
  uDosWidgets.Display = {
    _surfaces: [],
    _rafId: null,

    init: function(el, opts) {
      if (!el) return;
      opts = opts || {};
      var cols = opts.cols || 80;
      var rows = opts.rows || 24;
      var baseFont = opts.baseFont || 24;

      el.classList.add('udos-surface');
      this._surfaces.push({ el: el, cols: cols, rows: rows, baseFont: baseFont });
      this._recalc();

      if (this._surfaces.length === 1) {
        var self = this;
        window.addEventListener('resize', function() {
          if (self._rafId) cancelAnimationFrame(self._rafId);
          self._rafId = requestAnimationFrame(function() { self._recalc(); });
        });
      }
      return this;
    },

    resize: function(el, cols, rows) {
      for (var i = 0; i < this._surfaces.length; i++) {
        if (this._surfaces[i].el === el) {
          this._surfaces[i].cols = cols;
          this._surfaces[i].rows = rows;
          break;
        }
      }
      this._recalc();
    },

    _recalc: function() {
      var vw = window.innerWidth;
      var vh = window.innerHeight;

      // Read shared font scale
      var scale = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--udos-font-scale')) || 1.0;

      // Responsive menu scale: 25% smaller at half-viewport, 50% bigger at full
      // formula: vw/960 * 0.75 → at 960px=0.75, at 1920px=1.5
      var menuScale = Math.max(0.6, Math.min(1.6, vw / 960 * 0.75));
      document.documentElement.style.setProperty('--menu-scale', menuScale.toFixed(3));

      for (var i = 0; i < this._surfaces.length; i++) {
        var s = this._surfaces[i];
        var el = s.el;

        // 80% of viewport (== 10% gap each side)
        var targetW = vw * 0.8;
        var targetH = vh * 0.8;

        // Apply shared font scale to base
        var aspect = parseFloat(el.getAttribute('data-aspect')) || 0.55;
        var fontFromW = targetW / (s.cols * aspect);
        var fontFromH = targetH / s.rows;
        var fontSize = Math.min(fontFromW, fontFromH) * scale;
        fontSize = Math.max(fontSize, 5);

        // Use explicit px for width/height (min 10% gap enforced by 0.8 factor)
        var gridW = fontSize * s.cols * aspect;
        var gridH = fontSize * s.rows;
        el.style.fontSize = fontSize + 'px';
        el.style.width = gridW + 'px';
        el.style.height = gridH + 'px';
        el.style.setProperty('--udos-font-size', fontSize + 'px');
        el.style.setProperty('--udos-font-scale', scale);
      }

      // Update toolbar buttons — disable presets that don't fit
      this._updateToolbarButtons(vw, vh);
    },

    /** Disable viewport buttons whose preset doesn't fit the current window */
    _updateToolbarButtons: function(vw, vh) {
      var presets = [
        { cols: 20, rows: 10, label: '20x10' }, { cols: 32, rows: 16, label: '32x16' },
        { cols: 40, rows: 24, label: '40x24' }, { cols: 80, rows: 30, label: '80x30' },
        { cols: 48, rows: 48, label: '48x48' },
      ];
      var targetW = vw * 0.8, targetH = vh * 0.8;
      document.querySelectorAll('.menu-btn[data-size]').forEach(function(btn) {
        var key = btn.getAttribute('data-size');
        var preset = null;
        for (var p = 0; p < presets.length; p++) {
          if (presets[p].label === key) { preset = presets[p]; break; }
        }
        if (!preset) return;
        var fontW = targetW / (preset.cols * 0.55);
        var fontH = targetH / preset.rows;
        var fits = Math.min(fontW, fontH) >= 3;
        btn.disabled = !fits;
        btn.style.opacity = fits ? '1' : '0.35';
        btn.style.cursor = fits ? 'pointer' : 'not-allowed';
        btn.title = fits ? 'Switch to ' + key : key + ' too large for window';
      });
    },

    refresh: function() { this._recalc(); },

    /** Get current font size for a surface */
    getFontSize: function(el) {
      return parseFloat(el.style.fontSize) || 0;
    },
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
