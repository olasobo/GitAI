# # GitAI - GitHub CLI Automation Tool

A powerful command-line interface for automating GitHub version control actions. GitAI provides seamless integration with GitHub's API to manage repositories, issues, branches, and more from your terminal.

## Features

- 🔐 **Secure Authentication** - Uses GitHub Personal Access Tokens
- 📁 **Repository Management** - List, create, and get detailed repo information
- 🌿 **Branch Operations** - View and manage repository branches
- 📝 **Commit History** - Browse recent commits with detailed information
- 🐛 **Issue Management** - Create and list repository issues
- 🚀 **Modal Integration** - Cloud-powered operations for scalable automation

## Installation

1. Clone this repository:
```bash
git clone https://github.com/olasobo/GitAI.git
cd GitAI
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Setup

### 1. Get a GitHub Personal Access Token

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a descriptive name like "GitAI CLI"
4. Select the following scopes:
   - `repo` (Full control of private repositories)
   - `user` (Read user profile data)
   - `admin:repo_hook` (if you plan to work with webhooks)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again!)

### 2. Authenticate GitAI

Set your token as an environment variable:
```bash
export GITHUB_TOKEN="your_token_here"
```

Or authenticate directly:
```bash
python cli.py auth --token your_token_here
```

## Usage

### Authentication
```bash
# Authenticate with GitHub
python cli.py auth

# Authenticate with token directly
python cli.py auth --token your_token_here
```

### Repository Operations
```bash
# List all your repositories
python cli.py repos

# List only public repositories
python cli.py repos --public-only

# Get detailed information about a repository
python cli.py repo owner/repository-name

# Create a new repository
python cli.py create my-new-repo --description "My awesome project"

# Create a private repository
python cli.py create my-private-repo --private --description "Secret project"
```

### Branch Management
```bash
# List all branches in a repository
python cli.py branches owner/repository-name
```

### Commit History
```bash
# List recent commits from main branch
python cli.py commits owner/repository-name

# List commits from specific branch
python cli.py commits owner/repository-name develop

# Limit number of commits shown
python cli.py commits owner/repository-name main --limit 5
```

### Issue Management
```bash
# List open issues
python cli.py issues owner/repository-name

# List closed issues
python cli.py issues owner/repository-name --state closed

# List all issues
python cli.py issues owner/repository-name --state all

# Create a new issue
python cli.py create-issue owner/repository-name "Bug: App crashes on startup"

# Create issue with description
python cli.py create-issue owner/repository-name "Feature Request" "Add dark mode support"
```

## Examples

### Quick Repository Overview
```bash
# Get a quick overview of your main project
python cli.py repo myusername/my-project
python cli.py branches myusername/my-project
python cli.py commits myusername/my-project --limit 3
```

### Project Setup Workflow
```bash
# Create a new project
python cli.py create awesome-project --description "My awesome new project"

# Check it was created
python cli.py repos | grep awesome-project
```

### Issue Tracking
```bash
# Check current issues
python cli.py issues myusername/my-project

# Create a bug report
python cli.py create-issue myusername/my-project "Bug: Login not working" "Users cannot log in with valid credentials"
```

## Configuration

GitAI stores configuration in `~/.gitai_config.json`. This file contains:
- Your GitHub username
- API base URL
- Other preferences

**Note:** Your GitHub token is never stored in the config file for security reasons. Always use environment variables or provide it when prompted.

## Security Best Practices

1. **Never commit your GitHub token** to version control
2. **Use environment variables** to store sensitive information
3. **Regularly rotate your tokens** for enhanced security
4. **Use minimal scopes** - only grant permissions you actually need

## Modal Integration

The project includes Modal integration for cloud-powered operations. See `modal_integration.py` for examples of running GitHub operations at scale.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test them
4. Commit your changes: `git commit -am 'Add some feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/olasobo/GitAI/issues) page
2. Create a new issue with detailed information
3. Include your OS, Python version, and error messages
