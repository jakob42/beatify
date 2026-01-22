/**
 * Analytics Dashboard JavaScript (Story 19.2)
 *
 * Fetches analytics data from API and renders stat cards
 * with trend indicators and period filtering.
 */
(function() {
    'use strict';

    var API_URL = '/beatify/api/analytics';
    var currentPeriod = '30d';
    var retryCount = 0;
    var maxRetries = 3;

    /**
     * Load analytics data from API
     * @param {string} period - Time period (7d, 30d, 90d, all)
     */
    async function loadAnalytics(period) {
        showLoading(true);
        hideError();

        try {
            var response = await fetch(API_URL + '?period=' + encodeURIComponent(period));
            if (!response.ok) {
                throw new Error('API returned ' + response.status);
            }
            var data = await response.json();
            renderStats(data);
            updateLastUpdated(data.generated_at);
            retryCount = 0;
            showLoading(false);
        } catch (err) {
            console.error('Analytics API error:', err);
            showLoading(false);

            if (retryCount < maxRetries) {
                retryCount++;
                setTimeout(function() {
                    loadAnalytics(period);
                }, 1000 * retryCount);
            } else {
                showError();
            }
        }
    }

    /**
     * Render stat cards with data
     * @param {Object} data - Analytics data from API
     */
    function renderStats(data) {
        updateStatCard('stat-total-games', data.total_games, data.trends.games);
        updateStatCard('stat-avg-players', data.avg_players_per_game.toFixed(1), data.trends.players);
        updateStatCard('stat-avg-score', data.avg_score.toFixed(1), data.trends.score);

        // Format error rate as percentage
        var errorPct = (data.error_rate * 100).toFixed(1) + '%';
        // For error rate, negative trend (fewer errors) is good
        updateStatCard('stat-error-rate', errorPct, data.trends.errors, true);

        // Render additional sections (Stories 19.4, 19.5, 19.6)
        if (data.playlists) {
            renderPlaylists(data.playlists);
        }
        if (data.chart_data) {
            renderChart(data.chart_data);
        }
        if (data.error_stats) {
            renderErrorStats(data.error_stats);
        }
    }

    /**
     * Render playlist section (Story 19.4)
     * @param {Array} playlists - Playlist stats array
     */
    function renderPlaylists(playlists) {
        var listEl = document.getElementById('playlist-list');
        var emptyEl = document.getElementById('playlist-empty');

        if (!playlists || playlists.length === 0) {
            listEl.innerHTML = '';
            emptyEl.classList.remove('hidden');
            return;
        }

        emptyEl.classList.add('hidden');
        var maxCount = playlists[0].play_count;

        listEl.innerHTML = playlists.map(function(p) {
            var barWidth = (p.play_count / maxCount * 100).toFixed(1);
            return '<div class="playlist-row">' +
                '<div class="playlist-info">' +
                    '<span class="playlist-name">' + escapeHtml(p.name) + '</span>' +
                    '<span class="playlist-stats">' + p.play_count + ' games (' + p.percentage + '%)</span>' +
                '</div>' +
                '<div class="playlist-bar-container">' +
                    '<div class="playlist-bar" style="width: ' + barWidth + '%;"></div>' +
                '</div>' +
            '</div>';
        }).join('');
    }

    /**
     * Render games chart (Story 19.5)
     * @param {Object} chartData - Chart data with labels and values
     */
    function renderChart(chartData) {
        var canvas = document.getElementById('games-chart');
        if (!canvas || !canvas.getContext) return;

        var ctx = canvas.getContext('2d');
        var container = canvas.parentElement;

        // Responsive canvas sizing
        canvas.width = container.offsetWidth;
        canvas.height = 300;

        var labels = chartData.labels || [];
        var values = chartData.values || [];

        if (labels.length === 0) {
            ctx.fillStyle = '#888';
            ctx.font = '14px system-ui';
            ctx.textAlign = 'center';
            ctx.fillText('No data available', canvas.width / 2, canvas.height / 2);
            return;
        }

        var maxValue = Math.max.apply(null, values.concat([1]));
        var padding = {top: 20, right: 20, bottom: 40, left: 50};
        var chartWidth = canvas.width - padding.left - padding.right;
        var chartHeight = canvas.height - padding.top - padding.bottom;
        var barWidth = chartWidth / labels.length * 0.7;
        var barGap = chartWidth / labels.length * 0.3;

        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw gridlines
        ctx.strokeStyle = '#333';
        ctx.lineWidth = 1;
        for (var i = 0; i <= 5; i++) {
            var y = padding.top + (chartHeight / 5) * i;
            ctx.beginPath();
            ctx.moveTo(padding.left, y);
            ctx.lineTo(canvas.width - padding.right, y);
            ctx.stroke();
        }

        // Draw bars with neon gradient
        var gradient = ctx.createLinearGradient(0, chartHeight, 0, 0);
        gradient.addColorStop(0, '#9d4edd');
        gradient.addColorStop(1, '#00f5ff');

        values.forEach(function(value, idx) {
            var barHeight = (value / maxValue) * chartHeight;
            var x = padding.left + idx * (barWidth + barGap) + barGap / 2;
            var y = padding.top + chartHeight - barHeight;

            ctx.fillStyle = gradient;
            ctx.shadowColor = '#00f5ff';
            ctx.shadowBlur = 10;
            ctx.fillRect(x, y, barWidth, barHeight);
            ctx.shadowBlur = 0;
        });

        // Draw x-axis labels
        ctx.fillStyle = '#888';
        ctx.font = '12px system-ui';
        ctx.textAlign = 'center';
        labels.forEach(function(label, idx) {
            var x = padding.left + idx * (barWidth + barGap) + barGap / 2 + barWidth / 2;
            ctx.fillText(label, x, canvas.height - 10);
        });

        // Draw y-axis labels
        ctx.textAlign = 'right';
        for (var j = 0; j <= 5; j++) {
            var yPos = padding.top + (chartHeight / 5) * j;
            var val = Math.round(maxValue - (maxValue / 5) * j);
            ctx.fillText(val, padding.left - 10, yPos + 4);
        }

        // Update accessible data table
        updateChartDataTable(labels, values);

        // Store for resize handling
        window.currentChartData = chartData;
    }

    /**
     * Update accessible data table for chart
     */
    function updateChartDataTable(labels, values) {
        var tbody = document.querySelector('#games-chart-data tbody');
        if (!tbody) return;
        tbody.innerHTML = labels.map(function(label, i) {
            return '<tr><td>' + label + '</td><td>' + values[i] + '</td></tr>';
        }).join('');
    }

    /**
     * Render error stats panel (Story 19.6)
     * @param {Object} errorStats - Error statistics
     */
    function renderErrorStats(errorStats) {
        var rateEl = document.getElementById('error-rate-value');
        var badgeEl = document.getElementById('health-badge');
        var expandBtn = document.getElementById('error-expand-btn');
        var listContainer = document.getElementById('error-list-container');
        var listEl = document.getElementById('error-list');
        var noErrorsMsg = document.getElementById('no-errors-msg');

        // Display error rate
        var ratePercent = (errorStats.error_rate * 100).toFixed(1) + '%';
        if (rateEl) rateEl.textContent = ratePercent;

        // Update health badge
        if (badgeEl) {
            badgeEl.className = 'health-badge ' + errorStats.status;
            var badgeText = {
                healthy: 'Healthy',
                warning: 'Warning',
                critical: 'Critical'
            };
            var badgeIcon = {
                healthy: '✓',
                warning: '⚠',
                critical: '✕'
            };
            var textEl = badgeEl.querySelector('.badge-text');
            var iconEl = badgeEl.querySelector('.badge-icon');
            if (textEl) textEl.textContent = badgeText[errorStats.status] || 'Healthy';
            if (iconEl) iconEl.textContent = badgeIcon[errorStats.status] || '✓';
        }

        // Handle error list
        if (errorStats.recent_errors && errorStats.recent_errors.length > 0) {
            if (noErrorsMsg) noErrorsMsg.classList.add('hidden');
            if (expandBtn) expandBtn.classList.remove('hidden');

            if (listEl) {
                listEl.innerHTML = errorStats.recent_errors.map(function(err) {
                    var timeAgo = formatRelativeTime(err.timestamp);
                    var icon = getErrorTypeIcon(err.type);
                    return '<li class="error-item">' +
                        '<span class="error-icon">' + icon + '</span>' +
                        '<div class="error-content">' +
                            '<span class="error-type">' + escapeHtml(err.type) + '</span>' +
                            '<span class="error-message">' + escapeHtml(err.message) + '</span>' +
                            '<span class="error-time">' + timeAgo + '</span>' +
                        '</div>' +
                    '</li>';
                }).join('');
            }
        } else {
            if (expandBtn) expandBtn.classList.add('hidden');
            if (listContainer) listContainer.classList.add('hidden');
            if (noErrorsMsg) noErrorsMsg.classList.remove('hidden');
        }
    }

    /**
     * Get icon for error type
     */
    function getErrorTypeIcon(type) {
        var icons = {
            'WEBSOCKET_DISCONNECT': '🔌',
            'MEDIA_PLAYER_ERROR': '🔇',
            'PLAYBACK_FAILURE': '⏸',
            'STATE_TRANSITION_ERROR': '⚙️'
        };
        return icons[type] || '❌';
    }

    /**
     * Format timestamp as relative time
     */
    function formatRelativeTime(timestamp) {
        var now = Date.now() / 1000;
        var diff = now - timestamp;

        if (diff < 60) return 'just now';
        if (diff < 3600) return Math.floor(diff / 60) + ' min ago';
        if (diff < 86400) return Math.floor(diff / 3600) + ' hours ago';
        return Math.floor(diff / 86400) + ' days ago';
    }

    /**
     * Escape HTML special characters
     */
    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    /**
     * Update a single stat card
     * @param {string} id - Card element ID
     * @param {string|number} value - Display value
     * @param {number} trend - Trend percentage (-1 to 1)
     * @param {boolean} invertTrend - If true, negative is positive (for errors)
     */
    function updateStatCard(id, value, trend, invertTrend) {
        var card = document.getElementById(id);
        if (!card) return;

        card.classList.remove('loading');

        var valueEl = card.querySelector('.stat-value');
        var trendEl = card.querySelector('.stat-trend');

        if (valueEl) {
            valueEl.textContent = value;
        }

        if (trendEl) {
            if (trend === 0) {
                trendEl.textContent = '— 0%';
                trendEl.className = 'stat-trend neutral';
            } else {
                var isPositive = invertTrend ? trend < 0 : trend > 0;
                var arrow = trend > 0 ? '↑' : '↓';
                var pct = Math.abs(trend * 100).toFixed(0) + '%';
                trendEl.textContent = arrow + ' ' + pct;
                trendEl.className = 'stat-trend ' + (isPositive ? 'positive' : 'negative');
            }
        }
    }

    /**
     * Show/hide loading state
     * @param {boolean} show
     */
    function showLoading(show) {
        var loadingEl = document.getElementById('loading-state');
        var cardsEl = document.querySelector('.stat-cards');

        if (loadingEl) {
            loadingEl.classList.toggle('hidden', !show);
        }

        if (cardsEl) {
            cardsEl.classList.toggle('hidden', show);
        }

        // Add skeleton loading to cards
        document.querySelectorAll('.stat-card').forEach(function(card) {
            card.classList.toggle('loading', show);
        });
    }

    /**
     * Show error state
     */
    function showError() {
        var errorEl = document.getElementById('error-state');
        var cardsEl = document.querySelector('.stat-cards');

        if (errorEl) {
            errorEl.classList.remove('hidden');
        }

        if (cardsEl) {
            cardsEl.classList.add('hidden');
        }
    }

    /**
     * Hide error state
     */
    function hideError() {
        var errorEl = document.getElementById('error-state');
        if (errorEl) {
            errorEl.classList.add('hidden');
        }
    }

    /**
     * Update last updated timestamp
     * @param {number} timestamp - Unix timestamp
     */
    function updateLastUpdated(timestamp) {
        var el = document.getElementById('last-updated');
        if (!el) return;

        var date = new Date(timestamp * 1000);
        var timeStr = date.toLocaleTimeString(undefined, {
            hour: '2-digit',
            minute: '2-digit'
        });

        var t = window.t || function(key, fallback) { return fallback; };
        el.textContent = t('analytics.lastUpdated', 'Updated') + ': ' + timeStr;
    }

    /**
     * Handle period button click
     * @param {Event} e
     */
    function handlePeriodClick(e) {
        var btn = e.target.closest('.period-btn');
        if (!btn) return;

        var period = btn.dataset.period;
        if (!period || period === currentPeriod) return;

        // Update active state
        document.querySelectorAll('.period-btn').forEach(function(b) {
            b.classList.remove('period-btn--active');
        });
        btn.classList.add('period-btn--active');

        currentPeriod = period;
        retryCount = 0;
        loadAnalytics(period);
    }

    /**
     * Handle refresh button click
     */
    function handleRefreshClick() {
        retryCount = 0;
        loadAnalytics(currentPeriod);
    }

    /**
     * Handle retry button click
     */
    function handleRetryClick() {
        retryCount = 0;
        hideError();
        loadAnalytics(currentPeriod);
    }

    /**
     * Initialize analytics dashboard
     */
    function init() {
        // Period selector
        var periodSelector = document.querySelector('.period-selector');
        if (periodSelector) {
            periodSelector.addEventListener('click', handlePeriodClick);
        }

        // Refresh button
        var refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', handleRefreshClick);
        }

        // Retry button
        var retryBtn = document.getElementById('retry-btn');
        if (retryBtn) {
            retryBtn.addEventListener('click', handleRetryClick);
        }

        // Error panel expand/collapse (Story 19.6)
        var errorExpandBtn = document.getElementById('error-expand-btn');
        if (errorExpandBtn) {
            errorExpandBtn.addEventListener('click', function() {
                var container = document.getElementById('error-list-container');
                var icon = this.querySelector('.expand-icon');
                if (container) {
                    container.classList.toggle('hidden');
                    if (icon) icon.textContent = container.classList.contains('hidden') ? '▼' : '▲';
                }
            });
        }

        // Window resize handler for chart (Story 19.5)
        var resizeTimeout;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(function() {
                if (window.currentChartData) {
                    renderChart(window.currentChartData);
                }
            }, 150);
        });

        // Initial load
        loadAnalytics(currentPeriod);
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
