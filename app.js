// ===== Configuration =====
const CONFIG = {
    FORECAST_DAYS: 10,
    ARIMA_ORDER: { p: 5, d: 1, q: 0 },
    CHART_COLORS: {
        historical: 'rgb(59, 130, 246)',
        forecast: 'rgb(245, 158, 11)',
        confidence: 'rgba(245, 158, 11, 0.2)',
        grid: 'rgba(255, 255, 255, 0.1)'
    }
};

// ===== State Management =====
let currentChart = null;
let stockData = null;
let socket = null;
let currentSymbol = null;

// ===== DOM Elements =====
const elements = {
    stockSymbol: document.getElementById('stockSymbol'),
    analyzeBtn: document.getElementById('analyzeBtn'),
    loadingState: document.getElementById('loadingState'),
    errorState: document.getElementById('errorState'),
    errorMessage: document.getElementById('errorMessage'),
    resultsSection: document.getElementById('resultsSection'),
    stockName: document.getElementById('stockName'),
    stockSymbolDisplay: document.getElementById('stockSymbolDisplay'),
    currentPrice: document.getElementById('currentPrice'),
    priceChange: document.getElementById('priceChange'),
    high52w: document.getElementById('high52w'),
    low52w: document.getElementById('low52w'),
    avgVolume: document.getElementById('avgVolume'),
    forecastTrend: document.getElementById('forecastTrend'),
    targetPrice: document.getElementById('targetPrice'),
    confidenceRange: document.getElementById('confidenceRange'),
    volatility: document.getElementById('volatility'),
    priceChart: document.getElementById('priceChart')
};

// ===== Event Listeners =====
elements.analyzeBtn.addEventListener('click', () => analyzeStock());
elements.stockSymbol.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') analyzeStock();
});

// Popular stock chips
document.querySelectorAll('.stock-chip').forEach(chip => {
    chip.addEventListener('click', () => {
        elements.stockSymbol.value = chip.dataset.symbol;
        analyzeStock();
    });
});

// Chart view controls
document.querySelectorAll('.chart-control-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.chart-control-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        if (stockData) {
            updateChart(btn.dataset.view);
        }
    });
});

// ===== Main Analysis Function =====
async function analyzeStock() {
    const symbol = elements.stockSymbol.value.trim().toUpperCase();

    if (!symbol) {
        showError('Please enter a stock symbol');
        return;
    }

    showLoading();
    currentSymbol = symbol;

    try {
        // Fetch stock data
        const data = await fetchStockData(symbol);
        stockData = data;

        // Calculate metrics
        const metrics = calculateMetrics(data);

        // Fetch AI-powered prediction with news sentiment
        let forecast;
        try {
            const predictionData = await fetchAIPrediction(symbol);
            forecast = predictionData.prediction;

            // Update insights with AI prediction
            updateInsightsWithAI(forecast, metrics, predictionData.currentPrice);
        } catch (error) {
            console.log('Using fallback ARIMA prediction');
            forecast = performARIMAForecast(data.prices);
            updateInsights(forecast, metrics);
        }

        // Fetch and display news
        fetchAndDisplayNews(symbol);

        // Update UI
        updateStockInfo(symbol, data, metrics);
        renderChart(data, forecast);

        showResults();
    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message || 'Failed to analyze stock. Please check the symbol and try again.');
    }
}

// ===== Data Fetching =====
async function fetchStockData(symbol) {
    // Use our Flask backend API
    const url = `/api/stock/${symbol}`;

    try {
        const response = await fetch(url);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Stock not found or API error');
        }

        const data = await response.json();

        // Convert date strings back to Date objects
        data.dates = data.dates.map(dateStr => new Date(dateStr));

        return data;
    } catch (error) {
        throw new Error('Unable to fetch stock data. Please verify the symbol.');
    }
}

// ===== Metrics Calculation =====
function calculateMetrics(data) {
    const prices = data.prices;
    const volumes = data.volumes;

    // 52-week high and low
    const high52w = Math.max(...prices);
    const low52w = Math.min(...prices);

    // Average volume
    const avgVolume = volumes.reduce((a, b) => a + b, 0) / volumes.length;

    // Price change
    const priceChange = data.currentPrice - data.previousPrice;
    const priceChangePercent = (priceChange / data.previousPrice) * 100;

    // Volatility (standard deviation of returns)
    const returns = [];
    for (let i = 1; i < prices.length; i++) {
        returns.push((prices[i] - prices[i - 1]) / prices[i - 1]);
    }
    const meanReturn = returns.reduce((a, b) => a + b, 0) / returns.length;
    const variance = returns.reduce((a, b) => a + Math.pow(b - meanReturn, 2), 0) / returns.length;
    const volatility = Math.sqrt(variance) * Math.sqrt(252) * 100; // Annualized

    return {
        high52w,
        low52w,
        avgVolume,
        priceChange,
        priceChangePercent,
        volatility
    };
}

// ===== ARIMA Forecasting =====
function performARIMAForecast(prices) {
    const { p, d, q } = CONFIG.ARIMA_ORDER;

    // Differencing
    let diffData = [...prices];
    for (let i = 0; i < d; i++) {
        diffData = difference(diffData);
    }

    // Simple AR(p) model for forecasting
    const forecast = [];
    const confidenceIntervals = [];

    // Calculate AR coefficients using least squares
    const coefficients = calculateARCoefficients(diffData, p);

    // Generate forecasts
    let forecastData = [...diffData];

    for (let i = 0; i < CONFIG.FORECAST_DAYS; i++) {
        let nextValue = 0;
        for (let j = 0; j < p; j++) {
            nextValue += coefficients[j] * forecastData[forecastData.length - 1 - j];
        }
        forecastData.push(nextValue);
    }

    // Integrate back to original scale
    let integratedForecast = forecastData.slice(-CONFIG.FORECAST_DAYS);
    for (let i = 0; i < d; i++) {
        integratedForecast = integrate(integratedForecast, prices[prices.length - 1 - i]);
    }

    // Calculate confidence intervals (simplified)
    const stdError = calculateStdError(diffData, coefficients, p);

    for (let i = 0; i < CONFIG.FORECAST_DAYS; i++) {
        const margin = 1.96 * stdError * Math.sqrt(i + 1); // 95% CI
        confidenceIntervals.push({
            lower: integratedForecast[i] - margin,
            upper: integratedForecast[i] + margin
        });
    }

    return {
        values: integratedForecast,
        confidenceIntervals: confidenceIntervals
    };
}

// Helper: Difference series
function difference(data) {
    const result = [];
    for (let i = 1; i < data.length; i++) {
        result.push(data[i] - data[i - 1]);
    }
    return result;
}

// Helper: Integrate series
function integrate(data, lastValue) {
    const result = [];
    let cumSum = lastValue;
    for (let i = 0; i < data.length; i++) {
        cumSum += data[i];
        result.push(cumSum);
    }
    return result;
}

// Helper: Calculate AR coefficients
function calculateARCoefficients(data, p) {
    // Simple method: use autocorrelation
    const coefficients = [];
    const n = data.length;

    for (let lag = 1; lag <= p; lag++) {
        let sum = 0;
        let count = 0;
        for (let i = lag; i < n; i++) {
            sum += data[i] * data[i - lag];
            count++;
        }
        coefficients.push(sum / count / (data.reduce((a, b) => a + b * b, 0) / n));
    }

    // Normalize
    const sumCoef = coefficients.reduce((a, b) => a + Math.abs(b), 0);
    return coefficients.map(c => c / sumCoef * 0.8); // Damping factor
}

// Helper: Calculate standard error
function calculateStdError(data, coefficients, p) {
    let sumSquaredErrors = 0;
    for (let i = p; i < data.length; i++) {
        let predicted = 0;
        for (let j = 0; j < p; j++) {
            predicted += coefficients[j] * data[i - 1 - j];
        }
        sumSquaredErrors += Math.pow(data[i] - predicted, 2);
    }
    return Math.sqrt(sumSquaredErrors / (data.length - p));
}

// ===== UI Update Functions =====
function updateStockInfo(symbol, data, metrics) {
    elements.stockName.textContent = data.name;
    elements.stockSymbolDisplay.textContent = symbol;

    const currencySymbol = data.currency === 'INR' ? '₹' : '$';
    elements.currentPrice.textContent = `${currencySymbol}${data.currentPrice.toFixed(2)}`;

    const changeClass = metrics.priceChange >= 0 ? 'positive' : 'negative';
    const changeSign = metrics.priceChange >= 0 ? '+' : '';
    elements.priceChange.className = `price-change ${changeClass}`;
    elements.priceChange.innerHTML = `
        <span class="change-value">${changeSign}${metrics.priceChange.toFixed(2)}</span>
        <span class="change-percent">(${changeSign}${metrics.priceChangePercent.toFixed(2)}%)</span>
    `;

    elements.high52w.textContent = `${currencySymbol}${metrics.high52w.toFixed(2)}`;
    elements.low52w.textContent = `${currencySymbol}${metrics.low52w.toFixed(2)}`;
    elements.avgVolume.textContent = formatVolume(metrics.avgVolume);
}

function updateInsights(forecast, metrics) {
    const currencySymbol = stockData.currency === 'INR' ? '₹' : '$';
    const targetValue = forecast.values[forecast.values.length - 1];
    const currentValue = stockData.currentPrice;
    const change = targetValue - currentValue;
    const changePercent = (change / currentValue) * 100;

    // Forecast trend
    const trendText = changePercent > 2 ? '📈 Bullish Trend' :
        changePercent < -2 ? '📉 Bearish Trend' :
            '➡️ Neutral Trend';
    elements.forecastTrend.textContent = trendText;
    elements.forecastTrend.style.color = changePercent > 0 ? 'var(--accent-green)' :
        changePercent < 0 ? 'var(--accent-red)' :
            'var(--text-secondary)';

    // Target price
    elements.targetPrice.textContent = `${currencySymbol}${targetValue.toFixed(2)}`;
    elements.targetPrice.style.color = changePercent > 0 ? 'var(--accent-green)' :
        changePercent < 0 ? 'var(--accent-red)' :
            'var(--text-primary)';

    // Confidence range
    const lastCI = forecast.confidenceIntervals[forecast.confidenceIntervals.length - 1];
    const range = (lastCI.upper - lastCI.lower) / 2;
    elements.confidenceRange.textContent = `±${currencySymbol}${range.toFixed(2)}`;

    // Volatility
    elements.volatility.textContent = `${metrics.volatility.toFixed(2)}%`;
    elements.volatility.style.color = metrics.volatility > 30 ? 'var(--accent-red)' :
        metrics.volatility > 20 ? 'var(--accent-yellow)' :
            'var(--accent-green)';
}

function renderChart(data, forecast) {
    const ctx = elements.priceChart.getContext('2d');

    // Destroy existing chart
    if (currentChart) {
        currentChart.destroy();
    }

    // Generate forecast dates
    const forecastDates = [];
    let lastDate = new Date(data.dates[data.dates.length - 1]);
    for (let i = 0; i < CONFIG.FORECAST_DAYS; i++) {
        lastDate = addBusinessDays(lastDate, 1);
        forecastDates.push(new Date(lastDate));
    }

    // Prepare datasets
    const historicalData = {
        labels: data.dates.map(d => d.toLocaleDateString()),
        data: data.prices
    };

    const forecastData = {
        labels: forecastDates.map(d => d.toLocaleDateString()),
        data: forecast.values
    };

    const confidenceUpper = forecast.confidenceIntervals.map(ci => ci.upper);
    const confidenceLower = forecast.confidenceIntervals.map(ci => ci.lower);

    currentChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [...historicalData.labels, ...forecastData.labels],
            datasets: [
                {
                    label: 'Historical Price',
                    data: [...historicalData.data, ...Array(CONFIG.FORECAST_DAYS).fill(null)],
                    borderColor: CONFIG.CHART_COLORS.historical,
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    tension: 0.4,
                    fill: false
                },
                {
                    label: 'Forecast',
                    data: [...Array(historicalData.data.length).fill(null), ...forecastData.data],
                    borderColor: CONFIG.CHART_COLORS.forecast,
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    tension: 0.4,
                    fill: false
                },
                {
                    label: 'Upper CI',
                    data: [...Array(historicalData.data.length).fill(null), ...confidenceUpper],
                    borderColor: 'transparent',
                    backgroundColor: CONFIG.CHART_COLORS.confidence,
                    pointRadius: 0,
                    fill: '+1',
                    tension: 0.4
                },
                {
                    label: 'Lower CI',
                    data: [...Array(historicalData.data.length).fill(null), ...confidenceLower],
                    borderColor: 'transparent',
                    backgroundColor: CONFIG.CHART_COLORS.confidence,
                    pointRadius: 0,
                    fill: false,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: 'rgb(209, 213, 219)',
                        font: {
                            family: 'Inter',
                            size: 12
                        },
                        filter: (item) => item.text !== 'Upper CI' && item.text !== 'Lower CI'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(17, 24, 39, 0.95)',
                    titleColor: 'rgb(249, 250, 251)',
                    bodyColor: 'rgb(209, 213, 219)',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        label: function (context) {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y;
                            if (value !== null && label !== 'Upper CI' && label !== 'Lower CI') {
                                const currencySymbol = stockData.currency === 'INR' ? '₹' : '$';
                                return `${label}: ${currencySymbol}${value.toFixed(2)}`;
                            }
                            return '';
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: CONFIG.CHART_COLORS.grid,
                        drawBorder: false
                    },
                    ticks: {
                        color: 'rgb(156, 163, 175)',
                        maxRotation: 45,
                        minRotation: 45,
                        maxTicksLimit: 15,
                        font: {
                            family: 'Inter',
                            size: 10
                        }
                    }
                },
                y: {
                    grid: {
                        color: CONFIG.CHART_COLORS.grid,
                        drawBorder: false
                    },
                    ticks: {
                        color: 'rgb(156, 163, 175)',
                        font: {
                            family: 'JetBrains Mono',
                            size: 11
                        },
                        callback: function (value) {
                            const currencySymbol = stockData.currency === 'INR' ? '₹' : '$';
                            return currencySymbol + value.toFixed(0);
                        }
                    }
                }
            }
        }
    });
}

function updateChart(view) {
    if (!stockData) return;

    // This would filter the data based on view
    // For simplicity, we'll just re-render with the same data
    // You can implement filtering logic here
    const data = stockData;
    const forecast = performARIMAForecast(data.prices);
    renderChart(data, forecast);
}

// ===== State Management Functions =====
function showLoading() {
    elements.loadingState.classList.remove('hidden');
    elements.errorState.classList.add('hidden');
    elements.resultsSection.classList.add('hidden');
}

function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorState.classList.remove('hidden');
    elements.loadingState.classList.add('hidden');
    elements.resultsSection.classList.add('hidden');
}

function showResults() {
    elements.resultsSection.classList.remove('hidden');
    elements.loadingState.classList.add('hidden');
    elements.errorState.classList.add('hidden');
}

// ===== Utility Functions =====
function formatVolume(volume) {
    if (volume >= 1e9) return (volume / 1e9).toFixed(2) + 'B';
    if (volume >= 1e6) return (volume / 1e6).toFixed(2) + 'M';
    if (volume >= 1e3) return (volume / 1e3).toFixed(2) + 'K';
    return volume.toFixed(0);
}

function addBusinessDays(date, days) {
    const result = new Date(date);
    let addedDays = 0;
    while (addedDays < days) {
        result.setDate(result.getDate() + 1);
        if (result.getDay() !== 0 && result.getDay() !== 6) {
            addedDays++;
        }
    }
    return result;
}

// ===== WebSocket Connection =====
function initializeWebSocket() {
    if (typeof io === 'undefined') {
        console.log('Socket.IO not loaded, real-time updates disabled');
        return;
    }

    socket = io();

    socket.on('connect', () => {
        console.log('WebSocket connected');
        updateMarketStatus('Live', true);
    });

    socket.on('disconnect', () => {
        console.log('WebSocket disconnected');
        updateMarketStatus('Disconnected', false);
    });

    socket.on('connection_status', (data) => {
        console.log('Connection status:', data);
    });

    socket.on('market_update', (data) => {
        console.log('Market update received:', data);
        // Update market stats if on market overview tab
        if (document.getElementById('marketContent').classList.contains('active')) {
            updateMarketStatsRealtime(data);
        }
    });
}

function updateMarketStatus(text, isConnected) {
    const statusText = document.getElementById('marketStatusText');
    if (statusText) {
        statusText.textContent = text;
        statusText.style.color = isConnected ? 'var(--accent-green)' : 'var(--accent-red)';
    }
}

function updateMarketStatsRealtime(data) {
    // Update top gainers/losers in real-time
    if (data.topGainers && marketOverview) {
        marketOverview.renderTopMovers(data.topGainers, data.topLosers);
    }
}

// ===== AI Prediction with News =====
async function fetchAIPrediction(symbol) {
    const response = await fetch(`/api/stock/${symbol}/predict`);
    if (!response.ok) throw new Error('Prediction failed');
    return await response.json();
}

async function fetchAndDisplayNews(symbol) {
    try {
        await newsManager.fetchStockNews(symbol);
        newsManager.showNewsPanel();
    } catch (error) {
        console.error('Failed to fetch news:', error);
    }
}

function updateInsightsWithAI(forecast, metrics, currentPrice) {
    const currencySymbol = stockData.currency === 'INR' ? '₹' : '$';
    const targetValue = forecast.values[forecast.values.length - 1];
    const change = targetValue - currentPrice;
    const changePercent = (change / currentPrice) * 100;

    // Forecast trend with sentiment
    const sentiment = forecast.sentiment;
    let trendText = changePercent > 2 ? '📈 Bullish Trend' :
        changePercent < -2 ? '📉 Bearish Trend' :
            '➡️ Neutral Trend';

    if (sentiment) {
        trendText += ` (${sentiment.label} News)`;
    }

    elements.forecastTrend.textContent = trendText;
    elements.forecastTrend.style.color = changePercent > 0 ? 'var(--accent-green)' :
        changePercent < 0 ? 'var(--accent-red)' :
            'var(--text-secondary)';

    // Target price
    elements.targetPrice.textContent = `${currencySymbol}${targetValue.toFixed(2)}`;
    elements.targetPrice.style.color = changePercent > 0 ? 'var(--accent-green)' :
        changePercent < 0 ? 'var(--accent-red)' :
            'var(--text-primary)';

    // Confidence range
    const lastCI = forecast.confidenceIntervals[forecast.confidenceIntervals.length - 1];
    const range = (lastCI.upper - lastCI.lower) / 2;
    elements.confidenceRange.textContent = `±${currencySymbol}${range.toFixed(2)}`;

    // Volatility
    elements.volatility.textContent = `${metrics.volatility.toFixed(2)}%`;
    elements.volatility.style.color = metrics.volatility > 30 ? 'var(--accent-red)' :
        metrics.volatility > 20 ? 'var(--accent-yellow)' :
            'var(--accent-green)';
}

// ===== Initialize =====
// Auto-analyze default stock on load
window.addEventListener('load', () => {
    // Initialize WebSocket
    initializeWebSocket();

    // Auto-analyze default stock
    setTimeout(() => {
        analyzeStock();
    }, 500);
});
