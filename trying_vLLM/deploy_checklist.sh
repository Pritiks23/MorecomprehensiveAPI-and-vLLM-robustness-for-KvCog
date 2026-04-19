#!/bin/bash
# Pre-deployment checklist for KV Cognition

echo "🚀 KV Cognition - Vercel Deployment Checklist"
echo "=============================================="
echo ""

# Check if files exist
files=(
  "requirements.txt"
  "app/main.py"
  "app/static/index.html"
  "vercel.json"
  "api/index.py"
  ".vercelignore"
)

echo "✓ Checking required files..."
for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "  ✅ $file"
  else
    echo "  ❌ $file - MISSING!"
  fi
done

echo ""
echo "✓ Verifying Python imports..."
python3 -c "from app.main import app; print('  ✅ app.main imports successfully')" 2>/dev/null || echo "  ❌ Import error - check app/main.py"

echo ""
echo "✓ Requirements check..."
if [ -f "requirements.txt" ]; then
  echo "  ✅ requirements.txt found"
  echo ""
  echo "  Current dependencies:"
  cat requirements.txt | sed 's/^/    - /'
else
  echo "  ❌ requirements.txt not found"
fi

echo ""
echo "=============================================="
echo "📋 DEPLOYMENT STEPS:"
echo "=============================================="
echo ""
echo "1. Commit your changes:"
echo "   git add ."
echo "   git commit -m 'Deploy to Vercel'"
echo "   git push"
echo ""
echo "2. Go to https://vercel.com/dashboard"
echo "3. Click 'Add New Project'"
echo "4. Import your GitHub repository"
echo "5. Set Root Directory to: trying_vLLM"
echo "6. Click Deploy!"
echo ""
echo "✨ Your app will be live at: https://your-app.vercel.app"
echo ""
