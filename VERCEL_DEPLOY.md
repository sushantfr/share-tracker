# Deploying to Vercel

## Quick Deploy

1. **Push to GitHub** (Already done ✅)
   ```bash
   git push origin main
   ```

2. **Import to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New Project"
   - Import your GitHub repository: `sushantfr/share-tracker`
   - Vercel will automatically detect the configuration from `vercel.json`

3. **Deploy**
   - Click "Deploy"
   - Wait for the build to complete
   - Your app will be live at `https://share-tracker-[random].vercel.app`

## What Was Changed for Vercel

### Files Added:
- **`vercel.json`** - Vercel configuration for routing
- **`requirements.txt`** - Python dependencies (yfinance, Flask, Flask-CORS)
- **`api/stock.py`** - Serverless function for stock data API

### How It Works:
1. **Frontend**: Static HTML/CSS/JS files served directly by Vercel
2. **Backend**: Serverless function at `/api/stock/[symbol]` handles Yahoo Finance requests
3. **CORS**: Enabled in the serverless function for cross-origin requests

## Vercel Configuration

The `vercel.json` file configures URL rewrites:
```json
{
  "rewrites": [
    {
      "source": "/api/stock/:symbol",
      "destination": "/api/stock"
    }
  ]
}
```

## Serverless Function

The `api/stock.py` file is a Vercel serverless function that:
- Accepts GET requests to `/api/stock/SYMBOL`
- Fetches 1 year of historical data from Yahoo Finance
- Returns JSON with prices, dates, volumes, and metadata
- Handles CORS automatically

## Environment Variables (Optional)

If needed, you can add environment variables in Vercel dashboard:
- Go to Project Settings → Environment Variables
- Add any API keys or configuration

## Troubleshooting

### Build Fails
- Check that `requirements.txt` has all dependencies
- Ensure Python version compatibility (Vercel uses Python 3.9+)

### API Not Working
- Verify the serverless function is deployed at `/api/stock`
- Check function logs in Vercel dashboard
- Ensure CORS headers are set correctly

### Data Not Loading
- Yahoo Finance API might be rate-limited
- Check browser console for errors
- Verify stock symbol format (use `.NS` for NSE stocks)

## Custom Domain (Optional)

1. Go to Project Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions
4. Wait for DNS propagation

## Monitoring

- View deployment logs in Vercel dashboard
- Monitor function invocations and errors
- Set up alerts for failures

---

**Your app is now live on Vercel!** 🚀

After Vercel deploys, you can access your dashboard at the provided URL and share it with anyone!
