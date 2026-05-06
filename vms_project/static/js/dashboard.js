// static/js/dashboard.js
let visitorChartInstance = null;

document.addEventListener('DOMContentLoaded', function() {
    // Get data passed from Django
    const chartData = window.dashboardData?.chartData || getDefaultChartData();
    
    // Initialize chart
    initializeVisitorChart(chartData);
    
    // Add metric card interactions
    initializeMetricCards();
    
    // Add sidebar animations
    initializeSidebarAnimations();

    // AJAX Timeframe Toggling
    initializeTimeframeToggling();
});

function getDefaultChartData() {
    return {
        labels: [],
        values: []
    };
}

function initializeVisitorChart(chartData) {
    const labels = chartData.labels || [];
    const values = chartData.values || [];

    const ctx = document.getElementById('visitorChart');
    if (!ctx) return;

    const context = ctx.getContext('2d');

    // ── Threshold logic ─────────────────────────────────────
    const maxVal = Math.max(...values, 1);
    const highThreshold   = maxVal * 0.66;
    const mediumThreshold = maxVal * 0.33;

    // Classify each point
    function getLevel(v) {
        if (v >= highThreshold)   return 'high';
        if (v >= mediumThreshold) return 'medium';
        return 'low';
    }

    const levelColors = {
        high:   '#22c55e',   // green
        medium: '#f97316',   // orange
        low:    '#ef4444',   // red
    };

    // Per-point dot colors
    const pointColors = values.map(v => levelColors[getLevel(v)]);

    // Overall trend = average level (drives gradient)
    const avg = values.reduce((a, b) => a + b, 0) / (values.length || 1);
    const overallLevel = getLevel(avg);
    const lineColor = levelColors[overallLevel];

    // ── Gradient fill based on overall level ────────────────
    const gradientAlphas = {
        high:   ['rgba(34,197,94,0.32)',   'rgba(34,197,94,0.04)'],
        medium: ['rgba(249,115,22,0.32)',  'rgba(249,115,22,0.04)'],
        low:    ['rgba(239,68,68,0.32)',   'rgba(239,68,68,0.04)'],
    };
    const [gradTop, gradBot] = gradientAlphas[overallLevel];

    const gradient = context.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, gradTop);
    gradient.addColorStop(1, gradBot);

    // ── Trend badge ─────────────────────────────────────────
    const badgeEl = document.getElementById('analytics-trend-badge');
    if (badgeEl) {
        const badgeMap = {
            high:   { label: '↑ High Traffic',   cls: 'badge-trend-high'   },
            medium: { label: '~ Moderate Traffic', cls: 'badge-trend-medium' },
            low:    { label: '↓ Low Traffic',     cls: 'badge-trend-low'    },
        };
        const b = badgeMap[overallLevel];
        badgeEl.textContent = b.label;
        badgeEl.className = 'analytics-trend-badge ' + b.cls;
    }

    // ── Destroy old chart ────────────────────────────────────
    if (visitorChartInstance) {
        visitorChartInstance.destroy();
    }

    visitorChartInstance = new Chart(context, {
        type: 'line',
        data: {
            labels: labels.length > 0 ? labels : ['No data'],
            datasets: [{
                label: 'Visitors',
                data: values.length > 0 ? values : [0],
                fill: true,
                backgroundColor: gradient,
                borderWidth: 3,
                tension: 0.4,
                segment: {
                    borderColor: ctx => {
                        if (!ctx.p1) return levelColors.low;
                        const v = ctx.p1.parsed.y;
                        return levelColors[getLevel(v)];
                    }
                },
                pointBackgroundColor: pointColors,
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 6,
                pointHoverRadius: 9,
                pointHoverBorderWidth: 3,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(ctx) {
                            const v = ctx.parsed.y;
                            const lvl = getLevel(v);
                            const emoji = { high: '🟢', medium: '🟠', low: '🔴' };
                            return ` ${emoji[lvl]} ${v} visitor${v !== 1 ? 's' : ''} (${lvl})`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { precision: 0 },
                    grid: { color: 'rgba(99,102,241,0.08)' }
                },
                x: {
                    grid: { color: 'rgba(99,102,241,0.06)' }
                }
            }
        }
    });
}


function initializeTimeframeToggling() {
    const toggleButtons = document.querySelectorAll('.timeframe-toggle .btn');
    
    toggleButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const url = this.getAttribute('href');
            const timeframe = url.split('=')[1].split('#')[0];
            
            // UI Update: Active class
            toggleButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            // Fetch Data via AJAX
            fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                // Update chart with new data
                initializeVisitorChart(data);
                
                // Optional: Update URL without page reload
                window.history.pushState({}, '', url);
            })
            .catch(err => console.error('Error fetching dashboard data:', err));
        });
    });
}

function initializeMetricCards() {
    const metricCards = document.querySelectorAll('.metric-card');
    metricCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

function initializeSidebarAnimations() {
    const sidebarItems = document.querySelectorAll('.sidebar-item');
    sidebarItems.forEach((item, index) => {
        item.style.animationDelay = `${index * 0.1}s`;
        item.classList.add('fade-in-up');
    });
}
