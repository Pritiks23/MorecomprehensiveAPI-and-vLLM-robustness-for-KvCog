# Deployment Guide - Vercel

## Quick Setup (5 minutes)

### Prerequisites
- GitHub account with your repository pushed
- Vercel account (free tier available at https://vercel.com)

### Step 1: Connect Your Repository

1. Go to [https://vercel.com/dashboard](https://vercel.com/dashboard)
2. Click **"Add New Project"**
3. Select your GitHub repository: `MorecomprehensiveAPI-and-vLLM-robustness-for-KvCog`
4. Click **"Import"**

### Step 2: Configure Project Settings

When prompted, use these settings:

**Framework Preset:** Other (FastAPI)

**Root Directory:** `trying_vLLM` (or leave empty if deploying from root)

**Build Command:** (leave as default)

**Output Directory:** (leave as default)

**Install Command:** (leave as default)

### Step 3: Environment Variables

In the **Environment Variables** section, add any required variables:

```
PYTHONUNBUFFERED=true
```

If your app uses other env vars (Redis, API keys, etc.), add them here.

### Step 4: Deploy!

Click **"Deploy"** - Vercel will automatically:
- Install dependencies from `requirements.txt`
- Build and deploy your FastAPI app
- Provide you with a live URL (e.g., `https://your-username-appname.vercel.app`)

## Post-Deployment

### ✅ Test Your Deployment

```bash
# Replace with your Vercel URL
curl https://your-app.vercel.app/health

# Test the optimizer endpoint
curl -X POST https://your-app.vercel.app/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "monthly_tokens": 1000000,
    "avg_input_tokens": 256,
    "avg_output_tokens": 512,
    "traffic_pattern": "steady",
    "latency_target_sec": 1.0,
    "current_budget_monthly": 5000,
    "similarity_ratio": 0.5
  }'
```

### 🔧 Custom Domain

To connect a custom domain (e.g., `kvcognition.com`):

1. Go to your Vercel project → **Settings** → **Domains**
2. Click **"Add"** and enter your domain
3. Follow the DNS configuration instructions provided by Vercel
4. Update your domain's DNS records at your registrar

### 📊 Monitor Deployment

- **Logs:** Vercel Dashboard → **Deployments** → Click on a deployment → **Logs**
- **Analytics:** Vercel Dashboard → **Project** → **Analytics**
- **Performance:** Vercel Dashboard → **Project** → **Experience**

## Troubleshooting

### 502 Bad Gateway Error
- Check the logs: Dashboard → Deployments → Click latest → View logs
- Ensure all imports in `app/main.py` are correct
- Verify `requirements.txt` has all dependencies

### Static Files Not Loading
- Verify `app/static/index.html` exists
- Check that the path in `api/index.py` is correct
- Look at deployment logs for exact errors

### Import Errors
- Ensure the project root is correctly set in Vercel settings
- Verify all relative imports use proper paths
- Check that all files referenced are committed to GitHub

### Out of Memory
- FastAPI is lightweight, but vLLM model loading uses significant memory
- Consider: 
  - Lazy-loading models (load on first request)
  - Using a smaller model variant
  - Or deploying inference separately on Railway/Render with GPU

## Performance Tips

1. **Cold Start Optimization**
   - Vercel shows cold start time in logs
   - Minimize imports and initialization code
   - Consider using `app.py` file bundling

2. **Concurrency**
   - By default Vercel Serverless functions handle one request at a time
   - For high concurrency, upgrade to Pro plan

3. **Timeout**
   - Default: 60 seconds
   - Can be increased to 900 seconds on Pro plan

## Database/Redis Setup

If your app uses Redis or databases:

1. **Railway (Recommended)**
   - Create Redis instance on Railway
   - Copy connection string
   - Add to Vercel env vars

2. **Redis Cloud (Free tier available)**
   - Sign up at https://redis.com/cloud
   - Create database
   - Add `REDIS_URL` to Vercel environment

## Rollback

To rollback to a previous deployment:

1. Vercel Dashboard → Project → **Deployments**
2. Find the deployment you want
3. Click the **"..."** menu → **Promote to Production**

## Next Steps

- Set up GitHub integrations for auto-deployment on push
- Configure custom domain DNS
- Set up monitoring and error tracking (Sentry, etc.)
- Add GitHub branch protection rules

---

**Need Help?**
- Vercel Documentation: https://vercel.com/docs
- FastAPI on Vercel: https://vercel.com/guides/deploying-python-with-fastapi-on-vercel
