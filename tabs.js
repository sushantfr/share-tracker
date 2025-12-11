// Tab switching function
function switchTab(tab) {
    // Update tab buttons
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

    if (tab === 'analysis') {
        document.getElementById('analysisTab').classList.add('active');
        document.getElementById('analysisContent').classList.add('active');
    } else if (tab === 'today') {
        document.getElementById('todayTab').classList.add('active');
        document.getElementById('todayContent').classList.add('active');
        loadTodayPrices();
    } else if (tab === 'predictions') {
        document.getElementById('predictionsTab').classList.add('active');
        document.getElementById('predictionsContent').classList.add('active');
        populatePredictionStocks();
    } else if (tab === 'market') {
        document.getElementById('marketTab').classList.add('active');
        document.getElementById('marketContent').classList.add('active');
        if (typeof marketOverview !== 'undefined') {
            loadMarketOverview();
        }
    }
}

// Load today's prices
async function loadTodayPrices() {
    const loadingEl = document.getElementById('todayLoading');
    const listEl = document.getElementById('todayStockList');
    const statsEl = document.getElementById('todayStats');

    try {
        loadingEl.classList.remove('hidden');
        listEl.innerHTML = '';

        const response = await fetch('/api/market/overview');
        const data = await response.json();

        // Update stats
        statsEl.innerHTML = `
            <div class="stat-card">
                <div class="stat-label">Total Stocks</div>
                <div class="stat-value">${data.statistics.total}</div>
            </div>
            <div class="stat-card positive">
                <div class="stat-label">Gainers</div>
                <div class="stat-value">${data.statistics.gainers}</div>
            </div>
            <div class="stat-card negative">
                <div class="stat-label">Losers</div>
                <div class="stat-value">${data.statistics.losers}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Change</div>
                <div class="stat-value ${data.statistics.avgChange >= 0 ? 'positive' : 'negative'}">
                    ${data.statistics.avgChange >= 0 ? '+' : ''}${data.statistics.avgChange.toFixed(2)}%
                </div>
            </div>
        `;

        // Update stock list
        listEl.innerHTML = data.stocks.map(stock => `
            <div class="stock-row">
                <div class="stock-symbol">${stock.symbol.replace('.NS', '')}</div>
                <div class="stock-name">${stock.name}</div>
                <div class="stock-price">₹${stock.price.toFixed(2)}</div>
                <div class="stock-change ${stock.changePercent >= 0 ? 'positive' : 'negative'}">
                    ${stock.changePercent >= 0 ? '+' : ''}${stock.changePercent.toFixed(2)}%
                </div>
                <div class="stock-volume">${formatVolume(stock.volume)}</div>
            </div>
        `).join('');

        loadingEl.classList.add('hidden');
    } catch (error) {
        loadingEl.innerHTML = '<div class="error-state"><p>Failed to load today\'s prices</p></div>';
    }
}

// Populate prediction stocks dropdown
async function populatePredictionStocks() {
    const select = document.getElementById('predictionStock');
    if (select.options.length > 1) return; // Already populated

    try {
        const response = await fetch('/api/market/overview');
        const data = await response.json();

        data.stocks.forEach(stock => {
            const option = document.createElement('option');
            option.value = stock.symbol;
            option.textContent = `${stock.symbol.replace('.NS', '')} - ${stock.name}`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Failed to load stocks:', error);
    }
}

// Load prediction for selected stock
let predictionChart = null;
async function loadPrediction() {
    const symbol = document.getElementById('predictionStock').value;
    if (!symbol) {
        alert('Please select a stock');
        return;
    }

    const loadingEl = document.getElementById('predictionLoading');
    const resultsEl = document.getElementById('predictionResults');

    try {
        loadingEl.classList.remove('hidden');
        resultsEl.classList.add('hidden');

        const response = await fetch(`/api/predict/${symbol}`);
        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        // Update summary
        document.getElementById('predSymbol').textContent = symbol.replace('.NS', '');
        document.getElementById('predCurrent').textContent = `₹${data.currentPrice.toFixed(2)}`;

        const targetPrice = data.prediction.values[data.prediction.values.length - 1];
        document.getElementById('predTarget').textContent = `₹${targetPrice.toFixed(2)}`;

        const change = ((targetPrice - data.currentPrice) / data.currentPrice * 100);
        const changeEl = document.getElementById('predChange');
        changeEl.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`;
        changeEl.className = `pred-value ${change >= 0 ? 'positive' : 'negative'}`;

        // Update table
        const tbody = document.getElementById('predictionTableBody');
        tbody.innerHTML = data.prediction.values.map((price, i) => `
            <tr>
                <td>Day ${i + 1}</td>
                <td>₹${price.toFixed(2)}</td>
                <td>₹${data.prediction.confidenceIntervals[i].lower.toFixed(2)}</td>
                <td>₹${data.prediction.confidenceIntervals[i].upper.toFixed(2)}</td>
            </tr>
        `).join('');

        // Render chart
        renderPredictionChart(data);

        loadingEl.classList.add('hidden');
        resultsEl.classList.remove('hidden');
    } catch (error) {
        loadingEl.innerHTML = `<div class="error-state"><p>${error.message}</p></div>`;
    }
}

function renderPredictionChart(data) {
    const ctx = document.getElementById('predictionChart').getContext('2d');

    if (predictionChart) {
        predictionChart.destroy();
    }

    const labels = data.prediction.values.map((_, i) => `Day ${i + 1}`);

    predictionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Predicted Price',
                data: data.prediction.values,
                borderColor: 'rgb(245, 158, 11)',
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                borderWidth: 2,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: 'rgb(209, 213, 219)' }
                }
            },
            scales: {
                y: {
                    ticks: { color: 'rgb(156, 163, 175)' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                },
                x: {
                    ticks: { color: 'rgb(156, 163, 175)' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                }
            }
        }
    });
}

function formatVolume(volume) {
    if (volume >= 1e9) return (volume / 1e9).toFixed(2) + 'B';
    if (volume >= 1e6) return (volume / 1e6).toFixed(2) + 'M';
    if (volume >= 1e3) return (volume / 1e3).toFixed(2) + 'K';
    return volume.toFixed(0);
}

// Load market overview
async function loadMarketOverview() {
    const loadingEl = document.getElementById('marketLoading');
    const listEl = document.getElementById('stockList');

    try {
        loadingEl.classList.remove('hidden');
        listEl.innerHTML = '';

        if (typeof marketOverview !== 'undefined') {
            await marketOverview.loadMarketData();
        }

        loadingEl.classList.add('hidden');
    } catch (error) {
        loadingEl.innerHTML = '<div class="error-state"><p>Failed to load market data</p></div>';
    }
}
