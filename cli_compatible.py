#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitAI CLI - Command Line Interface for GitHub automation

Usage:
    python cli_compatible.py auth                              # Authenticate with GitHub
    python cli_compatible.py repos                             # List your repositories
    python cli_compatible.py repo <owner>/<name>               # Get repository info
    python cli_compatible.py create <name> [--private]         # Create new repository
    python cli_compatible.py branches <owner>/<name>           # List repository branches
    python cli_compatible.py commits <owner>/<name> [branch]   # List recent commits
    python cli_compatible.py issues <owner>/<name>             # List repository issues
    python cli_compatible.py create-issue <owner>/<name> <title> [body] # Create new issue
"""

import sys
import argparse
import os
from github_integration_compatible import GitHubIntegration, setup_github_integration


class GitAICLI:
    """Command Line Interface for GitAI"""
    
    def __init__(self):
        self.github = setup_github_integration()
    
    def authenticate(self, token=None):
        """Handle authentication command"""
        if not token:
            token = input("Enter your GitHub Personal Access Token: ").strip()
        
        if self.github.authenticate(token):
            print("🎉 Authentication successful! You can now use all GitAI commands.")
        else:
            print("❌ Authentication failed. Please check your token and try again.")
            sys.exit(1)
    
    def list_repos(self, include_private=True):
        """List user repositories"""
        if not self.github.config.token:
            print("❌ Please authenticate first using: python cli_compatible.py auth")
            return
        
        print("📁 Your GitHub repositories:\n")
        repos = self.github.get_user_repos(include_private)
        
        if not repos:
            print("No repositories found.")
            return
        
        for repo in repos:
            visibility = "🔒 Private" if repo['private'] else "🌐 Public"
            updated = repo['updated_at'][:10]  # Just the date part
            stars = repo['stargazers_count']
            
            print("  📂 {}".format(repo['full_name']))
            print("     {} | ⭐ {} stars | Updated: {}".format(visibility, stars, updated))
            if repo['description']:
                print("     📝 {}".format(repo['description']))
            print("     🔗 {}".format(repo['html_url']))
            print()
    
    def get_repo_info(self, repo_path):
        """Get detailed repository information"""
        try:
            owner, repo_name = repo_path.split('/')
        except ValueError:
            print("❌ Invalid repository format. Use: owner/repository")
            return
        
        repo_info = self.github.get_repo_info(owner, repo_name)
        if not repo_info:
            return
        
        print("📂 Repository: {}".format(repo_info['full_name']))
        print("📝 Description: {}".format(repo_info['description'] or 'No description'))
        print("🌐 Visibility: {}".format('Private' if repo_info['private'] else 'Public'))
        print("⭐ Stars: {}".format(repo_info['stargazers_count']))
        print("🍴 Forks: {}".format(repo_info['forks_count']))
        print("👁️  Watchers: {}".format(repo_info['watchers_count']))
        print("🐛 Open Issues: {}".format(repo_info['open_issues_count']))
        print("📅 Created: {}".format(repo_info['created_at'][:10]))
        print("🔄 Updated: {}".format(repo_info['updated_at'][:10]))
        print("💻 Language: {}".format(repo_info['language'] or 'Not specified'))
        print("🔗 URL: {}".format(repo_info['html_url']))
        
        if repo_info['homepage']:
            print("🏠 Homepage: {}".format(repo_info['homepage']))
    
    def create_repo(self, name, description="", private=False):
        """Create a new repository"""
        if not self.github.config.token:
            print("❌ Please authenticate first using: python cli_compatible.py auth")
            return
        
        repo_data = self.github.create_repository(name, description, private)
        if repo_data:
            print("🎉 Repository created successfully!")
            print("🔗 URL: {}".format(repo_data['html_url']))
            print("📋 Clone URL: {}".format(repo_data['clone_url']))
    
    def list_branches(self, repo_path):
        """List repository branches"""
        try:
            owner, repo_name = repo_path.split('/')
        except ValueError:
            print("❌ Invalid repository format. Use: owner/repository")
            return
        
        branches = self.github.get_repo_branches(owner, repo_name)
        if not branches:
            return
        
        print("🌿 Branches for {}:\n".format(repo_path))
        for branch in branches:
            protected = "🔒" if branch.get('protected', False) else "🌿"
            print("  {} {}".format(protected, branch['name']))
            print("     📝 Latest commit: {}".format(branch['commit']['sha'][:8]))
            print()
    
    def list_commits(self, repo_path, branch="main", limit=10):
        """List recent commits"""
        try:
            owner, repo_name = repo_path.split('/')
        except ValueError:
            print("❌ Invalid repository format. Use: owner/repository")
            return
        
        commits = self.github.get_repo_commits(owner, repo_name, branch, limit)
        if not commits:
            return
        
        print("📝 Recent commits for {} ({} branch):\n".format(repo_path, branch))
        for commit in commits:
            sha = commit['sha'][:8]
            message = commit['commit']['message'].split('\n')[0]  # First line only
            author = commit['commit']['author']['name']
            date = commit['commit']['author']['date'][:10]
            
            print("  🔸 {} - {}".format(sha, message))
            print("     👤 {} on {}".format(author, date))
            print()
    
    def list_issues(self, repo_path, state="open"):
        """List repository issues"""
        try:
            owner, repo_name = repo_path.split('/')
        except ValueError:
            print("❌ Invalid repository format. Use: owner/repository")
            return
        
        issues = self.github.get_repo_issues(owner, repo_name, state)
        if not issues:
            print("No {} issues found.".format(state))
            return
        
        print("{} {} issues for {}:\n".format("🐛", state.title(), repo_path))
        for issue in issues:
            labels = ", ".join([label['name'] for label in issue['labels']]) if issue['labels'] else "No labels"
            created = issue['created_at'][:10]
            
            print("  #{} - {}".format(issue['number'], issue['title']))
            print("     👤 {} | 📅 {} | 🏷️  {}".format(issue['user']['login'], created, labels))
            print("     🔗 {}".format(issue['html_url']))
            print()
    
    def create_issue(self, repo_path, title, body=""):
        """Create a new issue"""
        try:
            owner, repo_name = repo_path.split('/')
        except ValueError:
            print("❌ Invalid repository format. Use: owner/repository")
            return
        
        if not self.github.config.token:
            print("❌ Please authenticate first using: python cli_compatible.py auth")
            return
        
        issue_data = self.github.create_issue(owner, repo_name, title, body)
        if issue_data:
            print("🎉 Issue created successfully!")
            print("🔗 URL: {}".format(issue_data['html_url']))


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="GitAI - GitHub CLI Automation Tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Auth command
    auth_parser = subparsers.add_parser('auth', help='Authenticate with GitHub')
    auth_parser.add_argument('--token', help='GitHub Personal Access Token')
    
    # Repos command
    repos_parser = subparsers.add_parser('repos', help='List your repositories')
    repos_parser.add_argument('--public-only', action='store_true', help='Show only public repositories')
    
    # Repo info command
    repo_parser = subparsers.add_parser('repo', help='Get repository information')
    repo_parser.add_argument('path', help='Repository path (owner/name)')
    
    # Create repo command
    create_parser = subparsers.add_parser('create', help='Create new repository')
    create_parser.add_argument('name', help='Repository name')
    create_parser.add_argument('--description', default='', help='Repository description')
    create_parser.add_argument('--private', action='store_true', help='Make repository private')
    
    # Branches command
    branches_parser = subparsers.add_parser('branches', help='List repository branches')
    branches_parser.add_argument('path', help='Repository path (owner/name)')
    
    # Commits command
    commits_parser = subparsers.add_parser('commits', help='List recent commits')
    commits_parser.add_argument('path', help='Repository path (owner/name)')
    commits_parser.add_argument('branch', nargs='?', default='main', help='Branch name (default: main)')
    commits_parser.add_argument('--limit', type=int, default=10, help='Number of commits to show')
    
    # Issues command
    issues_parser = subparsers.add_parser('issues', help='List repository issues')
    issues_parser.add_argument('path', help='Repository path (owner/name)')
    issues_parser.add_argument('--state', choices=['open', 'closed', 'all'], default='open', help='Issue state')
    
    # Create issue command
    create_issue_parser = subparsers.add_parser('create-issue', help='Create new issue')
    create_issue_parser.add_argument('path', help='Repository path (owner/name)')
    create_issue_parser.add_argument('title', help='Issue title')
    create_issue_parser.add_argument('body', nargs='?', default='', help='Issue body/description')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = GitAICLI()
    
    # Execute commands
    if args.command == 'auth':
        cli.authenticate(args.token)
    elif args.command == 'repos':
        cli.list_repos(include_private=not args.public_only)
    elif args.command == 'repo':
        cli.get_repo_info(args.path)
    elif args.command == 'create':
        cli.create_repo(args.name, args.description, args.private)
    elif args.command == 'branches':
        cli.list_branches(args.path)
    elif args.command == 'commits':
        cli.list_commits(args.path, args.branch, args.limit)
    elif args.command == 'issues':
        cli.list_issues(args.path, args.state)
    elif args.command == 'create-issue':
        cli.create_issue(args.path, args.title, args.body)


if __name__ == "__main__":
    main()
