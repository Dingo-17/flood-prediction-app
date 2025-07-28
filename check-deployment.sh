#!/bin/bash
echo "🔍 COMPREHENSIVE DEPLOYMENT STATUS CHECK"
echo "========================================"
echo ""

echo "1. TESTING CURRENT DEPLOYMENT:"
echo "   URL: https://ai-flood-prediction-system.onrender.com"
echo ""

# Test current status
response=$(curl -s -w "%{http_code}" https://ai-flood-prediction-system.onrender.com/)
status_code="${response: -3}"
content="${response%???}"

echo "   Status Code: $status_code"
if [ "$status_code" = "200" ]; then
    echo "   ✅ DEPLOYMENT IS LIVE!"
    echo "   Response: $content" | head -3
    echo ""
    echo "🎉 SUCCESS! Backend is working properly."
    echo "✅ Ready to build iOS app: ./build-production.sh"
else
    echo "   ❌ DEPLOYMENT NOT WORKING"
    echo "   Response: $content" | head -1
    echo ""
    echo "🔧 MANUAL ACTION REQUIRED:"
    echo ""
    echo "The Render dashboard configuration needs to be updated manually."
    echo "This is the ONLY step that cannot be automated."
    echo ""
    echo "📋 EXACT STEPS NEEDED:"
    echo "1. Open: https://dashboard.render.com"
    echo "2. Click: ai-flood-prediction-system"
    echo "3. Click: Settings tab"
    echo "4. Scroll to: Build & Deploy section"
    echo "5. Change Start Command from: python app.py"
    echo "6. Change Start Command to: python app_production.py"
    echo "7. Click: Save Changes"
    echo "8. Click: Manual Deploy → Deploy latest commit"
    echo "9. Wait: 5-10 minutes for deployment"
    echo ""
    echo "🎯 WHY THIS IS NEEDED:"
    echo "- Current deployment is using: python app.py (complex ML version)"
    echo "- Production deployment needs: python app_production.py (simplified version)"
    echo "- Only you can access the Render dashboard to make this change"
    echo ""
fi

echo ""
echo "2. CHECKING GITHUB REPOSITORY STATUS:"
git_status=$(git status --porcelain 2>/dev/null)
if [ $? -eq 0 ]; then
    if [ -z "$git_status" ]; then
        echo "   ✅ Git repository is clean - all changes committed"
    else
        echo "   ⚠️ Uncommitted changes found:"
        echo "$git_status"
    fi
    
    latest_commit=$(git log -1 --oneline 2>/dev/null)
    echo "   Latest commit: $latest_commit"
else
    echo "   ❌ Not in a git repository"
fi

echo ""
echo "3. CHECKING PRODUCTION FILES:"

# Check in current directory or parent flood directory
prod_file=""
req_file=""

if [ -f "app_production.py" ]; then
    prod_file="app_production.py"
elif [ -f "../flood/app_production.py" ]; then
    prod_file="../flood/app_production.py"
fi

if [ -f "requirements.txt" ]; then
    req_file="requirements.txt"
elif [ -f "../flood/requirements.txt" ]; then
    req_file="../flood/requirements.txt"
fi

if [ -n "$prod_file" ]; then
    echo "   ✅ app_production.py exists at: $prod_file"
    echo "   Size: $(wc -l < "$prod_file") lines"
else
    echo "   ❌ app_production.py missing"
fi

if [ -n "$req_file" ]; then
    echo "   ✅ requirements.txt exists at: $req_file"
    echo "   Dependencies: $(wc -l < "$req_file") packages"
else
    echo "   ❌ requirements.txt missing"
fi

echo ""
echo "4. NEXT STEPS SUMMARY:"
if [ "$status_code" = "200" ]; then
    echo "   🎯 BACKEND IS READY!"
    echo "   → Run: ./build-production.sh"
    echo "   → Submit to App Store"
else
    echo "   🎯 MANUAL RENDER CONFIG NEEDED"
    echo "   → Update Start Command in Render dashboard"
    echo "   → Then re-run this script to verify"
    echo "   → Then build iOS app"
fi

echo ""
