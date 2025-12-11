/**
 * News and sentiment functionality
 */

class NewsManager {
    constructor() {
        this.currentNews = [];
        this.currentSentiment = null;
    }

    async fetchStockNews(symbol) {
        try {
            const response = await fetch(`/api/stock/${symbol}/news`);
            if (!response.ok) throw new Error('Failed to fetch news');

            const data = await response.json();
            this.currentNews = data.news;
            this.currentSentiment = data.sentiment;

            this.renderNews(data.news);
            this.renderSentiment(data.sentiment);

            return data;
        } catch (error) {
            console.error('Error fetching news:', error);
            return null;
        }
    }

    async fetchMarketNews() {
        try {
            const response = await fetch('/api/market/news');
            if (!response.ok) throw new Error('Failed to fetch market news');

            const data = await response.json();
            this.renderNews(data.news);
            this.renderSentiment(data.sentiment);

            return data;
        } catch (error) {
            console.error('Error fetching market news:', error);
            return null;
        }
    }

    renderNews(newsItems) {
        const container = document.getElementById('newsContainer');
        if (!container) return;

        if (!newsItems || newsItems.length === 0) {
            container.innerHTML = '<div class="no-news">No recent news available</div>';
            return;
        }

        container.innerHTML = newsItems.map(article => this.createNewsCard(article)).join('');
    }

    createNewsCard(article) {
        const sentimentClass = this.getSentimentClass(article.sentiment_score);
        const sentimentLabel = this.getSentimentLabel(article.sentiment_score);
        const publishedDate = new Date(article.publishedAt).toLocaleDateString();

        return `
            <div class="news-card">
                <div class="news-header">
                    <span class="news-source">${article.source || 'Unknown'}</span>
                    <span class="news-date">${publishedDate}</span>
                </div>
                <h4 class="news-title">${article.title}</h4>
                <p class="news-description">${article.description || ''}</p>
                <div class="news-footer">
                    <span class="sentiment-badge ${sentimentClass}">
                        ${sentimentLabel}
                    </span>
                    ${article.url && article.url !== '#' ?
                `<a href="${article.url}" target="_blank" class="news-link">Read more →</a>` :
                ''}
                </div>
            </div>
        `;
    }

    renderSentiment(sentiment) {
        const container = document.getElementById('sentimentOverview');
        if (!container) return;

        const sentimentClass = this.getSentimentClass(sentiment.score);
        const emoji = this.getSentimentEmoji(sentiment.label);

        container.innerHTML = `
            <div class="sentiment-card ${sentimentClass}">
                <div class="sentiment-icon">${emoji}</div>
                <div class="sentiment-content">
                    <div class="sentiment-label">${sentiment.label} Sentiment</div>
                    <div class="sentiment-score">Score: ${sentiment.score.toFixed(2)}</div>
                    <div class="sentiment-meta">
                        Based on ${sentiment.article_count} articles
                        <span class="confidence-badge">
                            ${(sentiment.confidence * 100).toFixed(0)}% confidence
                        </span>
                    </div>
                </div>
            </div>
        `;
    }

    getSentimentClass(score) {
        if (score > 0.2) return 'sentiment-positive';
        if (score < -0.2) return 'sentiment-negative';
        return 'sentiment-neutral';
    }

    getSentimentLabel(score) {
        if (score > 0.2) return 'Positive';
        if (score < -0.2) return 'Negative';
        return 'Neutral';
    }

    getSentimentEmoji(label) {
        const emojiMap = {
            'Positive': '😊',
            'Negative': '😟',
            'Neutral': '😐'
        };
        return emojiMap[label] || '😐';
    }

    showNewsPanel() {
        const panel = document.getElementById('newsPanel');
        if (panel) {
            panel.classList.remove('hidden');
        }
    }

    hideNewsPanel() {
        const panel = document.getElementById('newsPanel');
        if (panel) {
            panel.classList.add('hidden');
        }
    }
}

// Create global instance
const newsManager = new NewsManager();
