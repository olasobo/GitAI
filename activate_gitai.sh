#!/bin/bash
# GitAI Virtual Environment Activation Script

echo "🚀 Activating GitAI virtual environment..."
source venv/bin/activate

echo "✅ Virtual environment activated!"
echo "📋 Available GitAI commands:"
echo "  python cli_compatible.py auth                    # Authenticate with GitHub"
echo "  python cli_compatible.py repos                   # List your repositories"
echo "  python cli_compatible.py repo owner/name         # Get repository info"
echo "  python cli_compatible.py create repo-name        # Create new repository"
echo "  python cli_compatible.py branches owner/name     # List branches"
echo "  python cli_compatible.py commits owner/name      # List commits"
echo "  python cli_compatible.py issues owner/name       # List issues"
echo ""
echo "💡 To get help for any command, add --help"
echo "🔑 Don't forget to authenticate first with: python cli_compatible.py auth"
echo ""
