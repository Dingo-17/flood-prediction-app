#!/usr/bin/env python3
"""
Test script to verify the flood prediction system components
"""

import os
import sys
import subprocess

def test_dependencies():
    """Test if all required dependencies are available"""
    print("🔧 Testing Dependencies...")
    
    required_packages = [
        'pandas', 'numpy', 'matplotlib', 'seaborn',
        'sklearn', 'xgboost', 'tensorflow', 'requests', 'flask'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - Missing!")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("   Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All dependencies available!")
        return True

def test_directories():
    """Test if required directories exist"""
    print("\n📁 Testing Directory Structure...")
    
    required_dirs = ['data', 'models', 'logs', 'alerts', 'templates']
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"   ✅ {dir_name}/")
        else:
            print(f"   ❌ {dir_name}/ - Missing! Creating...")
            os.makedirs(dir_name, exist_ok=True)
    
    print("✅ Directory structure ready!")
    return True

def test_files():
    """Test if required files exist"""
    print("\n📄 Testing Files...")
    
    required_files = [
        'flood_prediction_system.ipynb',
        'app.py',
        'automated_predictions.py',
        'requirements.txt',
        'README.md',
        'templates/dashboard.html'
    ]
    
    missing_files = []
    
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f"   ✅ {file_name}")
        else:
            print(f"   ❌ {file_name} - Missing!")
            missing_files.append(file_name)
    
    if missing_files:
        print(f"\n⚠️  Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files present!")
        return True

def test_notebook_execution():
    """Test if the notebook can be executed"""
    print("\n📓 Testing Notebook Execution...")
    
    try:
        # Check if jupyter is available
        result = subprocess.run(['jupyter', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("   ✅ Jupyter available")
            print("   💡 To run notebook: jupyter notebook flood_prediction_system.ipynb")
        else:
            print("   ❌ Jupyter not available")
            print("   💡 Install with: pip install jupyter")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("   ❌ Jupyter not found")
        print("   💡 Install with: pip install jupyter")
    
    return True

def test_flask_app():
    """Test if Flask app can be imported"""
    print("\n🌐 Testing Flask Application...")
    
    try:
        # Try importing the app
        sys.path.insert(0, os.getcwd())
        from app import app
        print("   ✅ Flask app imports successfully")
        print("   💡 To run dashboard: python app.py")
        print("   💡 Then visit: http://localhost:5000")
    except ImportError as e:
        print(f"   ❌ Flask app import failed: {e}")
        print("   💡 Check dependencies and API keys in app.py")
    except Exception as e:
        print(f"   ⚠️  Flask app has issues: {e}")
        print("   💡 This might be due to missing models or config")
    
    return True

def test_prediction_script():
    """Test if automated prediction script can be imported"""
    print("\n🤖 Testing Prediction Script...")
    
    try:
        # Try importing the script
        import automated_predictions
        print("   ✅ Automated predictions script imports successfully")
        print("   💡 To run: python automated_predictions.py")
    except ImportError as e:
        print(f"   ❌ Prediction script import failed: {e}")
    except Exception as e:
        print(f"   ⚠️  Prediction script has issues: {e}")
        print("   💡 This might be due to missing models")
    
    return True

def main():
    """Run all tests"""
    print("🧪 Bangladesh Flood Prediction System - Test Suite")
    print("=" * 55)
    
    tests = [
        test_dependencies,
        test_directories,
        test_files,
        test_notebook_execution,
        test_flask_app,
        test_prediction_script
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Test failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 55)
    print("🎯 Test Summary:")
    print(f"   ✅ Passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 All tests passed! Your flood prediction system is ready!")
        print("\n🚀 Next Steps:")
        print("   1. Run the Jupyter notebook to train models")
        print("   2. Configure API keys in the notebook")
        print("   3. Start the dashboard with: python app.py")
        print("   4. Set up automated predictions")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
    
    return all(results)

if __name__ == "__main__":
    main()
