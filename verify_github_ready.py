#!/usr/bin/env python3
"""
GitHub Readiness Verification Script
Ensures all necessary files and configurations are in place for GitHub deployment
"""

import os
import sys
from pathlib import Path


def check_file_exists(file_path, description):
    """Check if a file exists and report status"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - MISSING")
        return False


def check_directory_exists(dir_path, description):
    """Check if a directory exists and report status"""
    if os.path.isdir(dir_path):
        print(f"✅ {description}: {dir_path}")
        return True
    else:
        print(f"❌ {description}: {dir_path} - MISSING")
        return False


def main():
    """Main verification function"""
    print("🔍 GitHub Readiness Verification")
    print("=" * 50)

    # Track verification results
    checks_passed = 0
    total_checks = 0

    # Core application files
    print("\n📁 Core Application Files:")
    core_files = [
        ("main.py", "Main application file"),
        ("requirements.txt", "Python dependencies"),
        ("test_main.py", "Test suite"),
        ("README.md", "Project documentation"),
        ("Dockerfile", "Docker configuration"),
        ("docker-compose.yml", "Docker Compose configuration"),
        (".gitignore", "Git ignore file"),
        ("Makefile", "Build automation"),
        ("pyproject.toml", "Python project configuration"),
        ("pytest.ini", "Pytest configuration"),
        (".flake8", "Linting configuration"),
    ]

    for file_path, description in core_files:
        total_checks += 1
        if check_file_exists(file_path, description):
            checks_passed += 1

    # Scripts directory
    print("\n📁 Scripts Directory:")
    scripts_dir = "scripts"
    total_checks += 1
    if check_directory_exists(scripts_dir, "Scripts directory"):
        checks_passed += 1

        script_files = [
            ("scripts/deploy.sh", "Deployment script"),
            ("scripts/test_pipeline.py", "Pipeline test script"),
            ("scripts/start_service.py", "Service startup script"),
            ("scripts/run_tests.py", "Test runner script"),
        ]

        for file_path, description in script_files:
            total_checks += 1
            if check_file_exists(file_path, description):
                checks_passed += 1

    # CI/CD configuration
    print("\n📁 CI/CD Configuration:")
    ci_files = [(".github/workflows/ci-cd.yml", "GitHub Actions workflow"), ("prometheus.yml", "Prometheus configuration")]

    for file_path, description in ci_files:
        total_checks += 1
        if check_file_exists(file_path, description):
            checks_passed += 1

    # Check for Windows-specific files
    print("\n📁 Platform-Specific Files:")
    platform_files = [("install.bat", "Windows installation script")]

    for file_path, description in platform_files:
        total_checks += 1
        if check_file_exists(file_path, description):
            checks_passed += 1

    # Check for essential directories
    print("\n📁 Essential Directories:")
    essential_dirs = [
        ("models", "Model storage directory"),
        ("logs", "Log storage directory"),
        ("data", "Data storage directory"),
    ]

    for dir_path, description in essential_dirs:
        total_checks += 1
        if check_directory_exists(dir_path, description):
            checks_passed += 1

    # Check file contents for completeness
    print("\n📄 File Content Verification:")

    # Check README.md has essential sections
    total_checks += 1
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as f:
            readme_content = f.read()
            if "API Anomaly Detection System" in readme_content and "Installation" in readme_content:
                print("✅ README.md: Contains essential sections")
                checks_passed += 1
            else:
                print("❌ README.md: Missing essential sections")

    # Check main.py has core functionality
    total_checks += 1
    if os.path.exists("main.py"):
        with open("main.py", "r", encoding="utf-8") as f:
            main_content = f.read()
            if "FastAPI" in main_content and "IsolationForest" in main_content:
                print("✅ main.py: Contains core functionality")
                checks_passed += 1
            else:
                print("❌ main.py: Missing core functionality")

    # Check test file has comprehensive tests
    total_checks += 1
    if os.path.exists("test_main.py"):
        with open("test_main.py", "r", encoding="utf-8") as f:
            test_content = f.read()
            if "pytest" in test_content and "TestClient" in test_content:
                print("✅ test_main.py: Contains comprehensive tests")
                checks_passed += 1
            else:
                print("❌ test_main.py: Missing comprehensive tests")

    # Final results
    print("\n" + "=" * 50)
    print("📊 VERIFICATION RESULTS")
    print("=" * 50)
    print(f"Total Checks: {total_checks}")
    print(f"Passed: {checks_passed}")
    print(f"Failed: {total_checks - checks_passed}")
    print(f"Success Rate: {(checks_passed/total_checks)*100:.1f}%")

    if checks_passed == total_checks:
        print("\n🎉 ALL CHECKS PASSED!")
        print("✅ Project is ready for GitHub deployment")
        print("\n📋 Next Steps:")
        print("1. Initialize git repository: git init")
        print("2. Add all files: git add .")
        print("3. Commit changes: git commit -m 'Initial commit: API Anomaly Detection System'")
        print("4. Create GitHub repository")
        print("5. Add remote: git remote add origin <repository-url>")
        print("6. Push to GitHub: git push -u origin main")
        print("\n🚀 Ready for deployment!")
        return True
    else:
        print(f"\n⚠️  {total_checks - checks_passed} checks failed.")
        print("Please fix the issues before pushing to GitHub.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
