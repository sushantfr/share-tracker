/**
 * Market Overview functionality
 */

class MarketOverview {
    constructor() {
        this.stocks = [];
        this.filteredStocks = [];
        this.currentSort = { field: 'marketCap', direction: 'desc' };
        this.currentFilter = 'all';
    }

    async loadMarketData() {
        try {
            const response = await fetch('/api/market/overview');
            if (!response.ok) throw new Error('Failed to fetch market data');

            const data = await response.json();
            this.stocks = data.stocks;
            this.filteredStocks = [...this.stocks];

            this.renderMarketStats(data.statistics);
            this.renderTopMovers(data.topGainers, data.topLosers);
            this.renderStockList(this.filteredStocks);
            this.renderCategories(data.categories);

            return data;
        } catch (error) {
            console.error('Error loading market data:', error);
            throw error;
        }
    }

    renderMarketStats(stats) {
        const statsContainer = document.getElementById('marketStats');
        if (!statsContainer) return;

        statsContainer.innerHTML = `
            <div class="stat-card">
                <div class="stat-label">Total Stocks</div>
                <div class="stat-value">${stats.total}</div>
            </div>
            <div class="stat-card positive">
                <div class="stat-label">Gainers</div>
                <div class="stat-value">${stats.gainers}</div>
            </div>
            <div class="stat-card negative">
                <div class="stat-label">Losers</div>
                <div class="stat-value">${stats.losers}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Change</div>
                <div class="stat-value ${stats.avgChange >= 0 ? 'positive' : 'negative'}">
                    ${stats.avgChange >= 0 ? '+' : ''}${stats.avgChange.toFixed(2)}%
                </div>
            </div>
        `;
    }

    renderTopMovers(gainers, losers) {
        const gainersContainer = document.getElementById('topGainers');
        const losersContainer = document.getElementById('topLosers');

        if (gainersContainer) {
            gainersContainer.innerHTML = gainers.map(stock => this.createMoverCard(stock, 'gainer')).join('');
        }

        if (losersContainer) {
            losersContainer.innerHTML = losers.map(stock => this.createMoverCard(stock, 'loser')).join('');
        }
    }

    createMoverCard(stock, type) {
        const icon = type === 'gainer' ? '📈' : '📉';
        const changeClass = type === 'gainer' ? 'positive' : 'negative';

        return `
            <div class="mover-card ${type}" onclick="marketOverview.selectStock('${stock.symbol}')">
                <div class="mover-icon">${icon}</div>
                <div class="mover-info">
                    <div class="mover-symbol">${stock.symbol.replace('.NS', '')}</div>
                    <div class="mover-name">${stock.name}</div>
                </div>
                <div class="mover-change ${changeClass}">
                    ${stock.changePercent >= 0 ? '+' : ''}${stock.changePercent.toFixed(2)}%
                </div>
            </div>
        `;
    }

    renderStockList(stocks) {
        const listContainer = document.getElementById('stockList');
        if (!listContainer) return;

        if (stocks.length === 0) {
            listContainer.innerHTML = '<div class="no-results">No stocks found</div>';
            return;
        }

        listContainer.innerHTML = stocks.map(stock => `
            <div class="stock-row" onclick="marketOverview.selectStock('${stock.symbol}')">
                <div class="stock-symbol">${stock.symbol.replace('.NS', '')}</div>
                <div class="stock-name">${stock.name}</div>
                <div class="stock-price">₹${stock.price.toFixed(2)}</div>
                <div class="stock-change ${stock.changePercent >= 0 ? 'positive' : 'negative'}">
                    ${stock.changePercent >= 0 ? '+' : ''}${stock.changePercent.toFixed(2)}%
                </div>
                <div class="stock-volume">${this.formatVolume(stock.volume)}</div>
            </div>
        `).join('');
    }

    renderCategories(categories) {
        const container = document.getElementById('categoryTabs');
        if (!container) return;

        const categoryHTML = Object.entries(categories).map(([name, data]) => `
            <button class="category-tab" onclick="marketOverview.filterByCategory('${name}')">
                <span class="category-name">${name.toUpperCase()}</span>
                <span class="category-change ${data.avgChange >= 0 ? 'positive' : 'negative'}">
                    ${data.avgChange >= 0 ? '+' : ''}${data.avgChange.toFixed(2)}%
                </span>
            </button>
        `).join('');

        container.innerHTML = `
            <button class="category-tab active" onclick="marketOverview.filterByCategory('all')">
                <span class="category-name">ALL</span>
            </button>
            ${categoryHTML}
        `;
    }

    filterByCategory(category) {
        this.currentFilter = category;

        // Update active tab
        document.querySelectorAll('.category-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        event.target.closest('.category-tab').classList.add('active');

        if (category === 'all') {
            this.filteredStocks = [...this.stocks];
        } else {
            const categoryStocks = config.MARKET_CATEGORIES[category] || [];
            this.filteredStocks = this.stocks.filter(s => categoryStocks.includes(s.symbol));
        }

        this.renderStockList(this.filteredStocks);
    }

    searchStocks(query) {
        if (!query) {
            this.filteredStocks = [...this.stocks];
        } else {
            const lowerQuery = query.toLowerCase();
            this.filteredStocks = this.stocks.filter(stock =>
                stock.symbol.toLowerCase().includes(lowerQuery) ||
                stock.name.toLowerCase().includes(lowerQuery)
            );
        }
        this.renderStockList(this.filteredStocks);
    }

    sortStocks(field) {
        if (this.currentSort.field === field) {
            this.currentSort.direction = this.currentSort.direction === 'asc' ? 'desc' : 'asc';
        } else {
            this.currentSort.field = field;
            this.currentSort.direction = 'desc';
        }

        this.filteredStocks.sort((a, b) => {
            const aVal = a[field] || 0;
            const bVal = b[field] || 0;
            return this.currentSort.direction === 'asc' ? aVal - bVal : bVal - aVal;
        });

        this.renderStockList(this.filteredStocks);
    }

    selectStock(symbol) {
        // Switch to analysis tab and analyze the stock
        document.getElementById('analysisTab').click();
        document.getElementById('stockSymbol').value = symbol;
        analyzeStock();
    }

    formatVolume(volume) {
        if (volume >= 1e9) return (volume / 1e9).toFixed(2) + 'B';
        if (volume >= 1e6) return (volume / 1e6).toFixed(2) + 'M';
        if (volume >= 1e3) return (volume / 1e3).toFixed(2) + 'K';
        return volume.toFixed(0);
    }
}

// Create global instance
const marketOverview = new MarketOverview();
