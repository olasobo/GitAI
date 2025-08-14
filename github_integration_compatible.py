# -*- coding: utf-8 -*-
"""
GitHub Integration Module for GitAI CLI

This module handles GitHub authentication and repository operations
using the GitHub API v4 (GraphQL) and REST API.
"""

import os
import json
import requests
from pathlib import Path


class GitHubConfig:
    """Configuration for GitHub integration"""
    
    def __init__(self, token=None, username=None, api_base_url="https://api.github.com", config_file=None):
        self.token = token
        self.username = username
        self.api_base_url = api_base_url
        self.config_file = config_file or os.path.expanduser("~/.gitai_config.json")


class GitHubIntegration:
    """Main class for GitHub API integration"""
    
    def __init__(self, config=None):
        self.config = config or GitHubConfig()
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """Setup requests session with authentication headers"""
        if self.config.token:
            self.session.headers.update({
                'Authorization': 'token {}'.format(self.config.token),
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'GitAI-CLI/1.0'
            })
    
    def authenticate(self, token=None):
        """
        Authenticate with GitHub using a personal access token
        
        Args:
            token: GitHub personal access token. If None, will try to load from config
            
        Returns:
            bool: True if authentication successful, False otherwise
        """
        if token:
            self.config.token = token
        elif not self.config.token:
            # Try to load from environment variable
            self.config.token = os.getenv('GITHUB_TOKEN')
        
        if not self.config.token:
            print("❌ No GitHub token provided. Please set GITHUB_TOKEN environment variable or provide token directly.")
            return False
        
        self._setup_session()
        
        # Test authentication by getting user info
        try:
            response = self.session.get("{}/user".format(self.config.api_base_url))
            if response.status_code == 200:
                user_data = response.json()
                self.config.username = user_data.get('login')
                print("✅ Successfully authenticated as {}".format(self.config.username))
                self._save_config()
                return True
            else:
                print("❌ Authentication failed: {} - {}".format(response.status_code, response.text))
                return False
        except Exception as e:
            print("❌ Authentication error: {}".format(str(e)))
            return False
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            config_data = {
                'username': self.config.username,
                'api_base_url': self.config.api_base_url
                # Note: We don't save the token for security reasons
            }
            with open(self.config.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            print("⚠️  Warning: Could not save config: {}".format(str(e)))
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config.config_file):
                with open(self.config.config_file, 'r') as f:
                    config_data = json.load(f)
                    self.config.username = config_data.get('username')
                    self.config.api_base_url = config_data.get('api_base_url', self.config.api_base_url)
        except Exception as e:
            print("⚠️  Warning: Could not load config: {}".format(str(e)))
    
    def get_user_repos(self, include_private=True):
        """
        Get list of user's repositories
        
        Args:
            include_private: Whether to include private repositories
            
        Returns:
            List of repository dictionaries
        """
        if not self.config.token:
            print("❌ Not authenticated. Please authenticate first.")
            return []
        
        repos = []
        page = 1
        per_page = 100
        
        while True:
            params = {
                'page': page,
                'per_page': per_page,
                'sort': 'updated',
                'direction': 'desc'
            }
            
            if include_private:
                params['visibility'] = 'all'
            else:
                params['visibility'] = 'public'
            
            try:
                response = self.session.get("{}/user/repos".format(self.config.api_base_url), params=params)
                if response.status_code == 200:
                    page_repos = response.json()
                    if not page_repos:
                        break
                    repos.extend(page_repos)
                    page += 1
                else:
                    print("❌ Failed to fetch repositories: {}".format(response.status_code))
                    break
            except Exception as e:
                print("❌ Error fetching repositories: {}".format(str(e)))
                break
        
        return repos
    
    def get_repo_info(self, owner, repo_name):
        """
        Get detailed information about a specific repository
        
        Args:
            owner: Repository owner username
            repo_name: Repository name
            
        Returns:
            Repository information dictionary or None if not found
        """
        try:
            response = self.session.get("{}/repos/{}/{}".format(self.config.api_base_url, owner, repo_name))
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print("❌ Repository {}/{} not found".format(owner, repo_name))
                return None
            else:
                print("❌ Failed to fetch repository info: {}".format(response.status_code))
                return None
        except Exception as e:
            print("❌ Error fetching repository info: {}".format(str(e)))
            return None
    
    def create_repository(self, name, description="", private=False):
        """
        Create a new repository
        
        Args:
            name: Repository name
            description: Repository description
            private: Whether the repository should be private
            
        Returns:
            Created repository information or None if failed
        """
        if not self.config.token:
            print("❌ Not authenticated. Please authenticate first.")
            return None
        
        data = {
            'name': name,
            'description': description,
            'private': private,
            'auto_init': True
        }
        
        try:
            response = self.session.post("{}/user/repos".format(self.config.api_base_url), json=data)
            if response.status_code == 201:
                repo_data = response.json()
                print("✅ Successfully created repository: {}".format(repo_data['full_name']))
                return repo_data
            else:
                print("❌ Failed to create repository: {} - {}".format(response.status_code, response.text))
                return None
        except Exception as e:
            print("❌ Error creating repository: {}".format(str(e)))
            return None
    
    def get_repo_branches(self, owner, repo_name):
        """
        Get list of branches for a repository
        
        Args:
            owner: Repository owner username
            repo_name: Repository name
            
        Returns:
            List of branch dictionaries
        """
        try:
            response = self.session.get("{}/repos/{}/{}/branches".format(self.config.api_base_url, owner, repo_name))
            if response.status_code == 200:
                return response.json()
            else:
                print("❌ Failed to fetch branches: {}".format(response.status_code))
                return []
        except Exception as e:
            print("❌ Error fetching branches: {}".format(str(e)))
            return []
    
    def get_repo_commits(self, owner, repo_name, branch="main", limit=10):
        """
        Get recent commits for a repository
        
        Args:
            owner: Repository owner username
            repo_name: Repository name
            branch: Branch name (default: main)
            limit: Number of commits to fetch
            
        Returns:
            List of commit dictionaries
        """
        params = {
            'sha': branch,
            'per_page': limit
        }
        
        try:
            response = self.session.get("{}/repos/{}/{}/commits".format(self.config.api_base_url, owner, repo_name), params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print("❌ Failed to fetch commits: {}".format(response.status_code))
                return []
        except Exception as e:
            print("❌ Error fetching commits: {}".format(str(e)))
            return []
    
    def create_issue(self, owner, repo_name, title, body="", labels=None):
        """
        Create a new issue in a repository
        
        Args:
            owner: Repository owner username
            repo_name: Repository name
            title: Issue title
            body: Issue body/description
            labels: List of label names
            
        Returns:
            Created issue information or None if failed
        """
        data = {
            'title': title,
            'body': body
        }
        
        if labels:
            data['labels'] = labels
        
        try:
            response = self.session.post("{}/repos/{}/{}/issues".format(self.config.api_base_url, owner, repo_name), json=data)
            if response.status_code == 201:
                issue_data = response.json()
                print("✅ Successfully created issue #{}: {}".format(issue_data['number'], title))
                return issue_data
            else:
                print("❌ Failed to create issue: {} - {}".format(response.status_code, response.text))
                return None
        except Exception as e:
            print("❌ Error creating issue: {}".format(str(e)))
            return None
    
    def get_repo_issues(self, owner, repo_name, state="open"):
        """
        Get issues for a repository
        
        Args:
            owner: Repository owner username
            repo_name: Repository name
            state: Issue state (open, closed, all)
            
        Returns:
            List of issue dictionaries
        """
        params = {
            'state': state,
            'sort': 'updated',
            'direction': 'desc'
        }
        
        try:
            response = self.session.get("{}/repos/{}/{}/issues".format(self.config.api_base_url, owner, repo_name), params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print("❌ Failed to fetch issues: {}".format(response.status_code))
                return []
        except Exception as e:
            print("❌ Error fetching issues: {}".format(str(e)))
            return []


def setup_github_integration():
    """
    Setup and return a configured GitHub integration instance
    
    Returns:
        GitHubIntegration instance
    """
    github = GitHubIntegration()
    github._load_config()
    
    # Try to authenticate if token is available
    if not github.authenticate():
        print("\n🔑 To use GitHub integration, you need a Personal Access Token:")
        print("1. Go to GitHub Settings > Developer settings > Personal access tokens")
        print("2. Generate a new token with 'repo' scope")
        print("3. Set it as GITHUB_TOKEN environment variable or provide it when prompted")
        print("4. Run the authentication again")
    
    return github


if __name__ == "__main__":
    # Example usage
    github = setup_github_integration()
    
    if github.config.token:
        print("\n📁 Your repositories:")
        repos = github.get_user_repos()
        for repo in repos[:5]:  # Show first 5 repos
            print("  • {} - {}".format(repo['full_name'], repo['description'] or 'No description'))
