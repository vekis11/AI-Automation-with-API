#!/bin/bash
# BRUTAL FIX: Instant deployment to multiple platforms

echo "🚀 BRUTAL FIX: Instant deployment options..."

# Check if docs folder exists
if [ ! -d "docs" ]; then
    echo "❌ docs folder not found!"
    exit 1
fi

echo "✅ docs folder found!"

# Option 1: Netlify (INSTANT)
echo ""
echo "🌐 NETLIFY DEPLOYMENT (30 seconds):"
echo "   1. Go to: https://netlify.com"
echo "   2. Click 'Sites' → 'Add new site' → 'Deploy manually'"
echo "   3. Drag & drop the 'docs' folder"
echo "   4. Get instant URL!"
echo ""

# Option 2: Vercel (INSTANT)
echo "⚡ VERCEL DEPLOYMENT (1 minute):"
echo "   1. Go to: https://vercel.com"
echo "   2. Click 'New Project'"
echo "   3. Import: vekis11/AI-Automation-with-API"
echo "   4. Root Directory: docs"
echo "   5. Deploy!"
echo ""

# Option 3: Railway (INSTANT)
echo "🚂 RAILWAY DEPLOYMENT (1 minute):"
echo "   1. Go to: https://railway.app"
echo "   2. Click 'New Project' → 'Deploy from GitHub repo'"
echo "   3. Select: vekis11/AI-Automation-with-API"
echo "   4. Deploy static site!"
echo ""

# Option 4: Surge.sh (INSTANT)
echo "💥 SURGE.SH DEPLOYMENT (30 seconds):"
echo "   1. Install: npm install -g surge"
echo "   2. Run: cd docs && surge"
echo "   3. Get instant URL!"
echo ""

# Option 5: GitHub Pages Manual
echo "📋 GITHUB PAGES MANUAL:"
echo "   1. Go to: https://github.com/vekis11/AI-Automation-with-API/settings/pages"
echo "   2. Source: GitHub Actions"
echo "   3. Save"
echo "   4. Go to Actions tab and run workflow"
echo ""

echo "🎉 BRUTAL FIX COMPLETE!"
echo "📊 Choose any option above for instant deployment!"
