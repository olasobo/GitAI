"""
GitHub Integration Module for GitAI CLI

This module handles GitHub authentication and repository operations
using the GitHub API v4 (GraphQL) and REST API.
"""

import os
import json
import requests
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GitHubConfig:
    """Configuration for GitHub integration"""
    token: Optional[str] = None
    username: Optional[str] = None
    api_base_url: str = "https://api.github.com"
    config_file: str = os.path.expanduser("~/.gitai_config.json")


class GitHubIntegration:
    """Main class for GitHub API integration"""
    
    def __init__(self, config: Optional[GitHubConfig] = None):
        self.config = config or GitHubConfig()
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """Setup requests session with authentication headers"""
        if self.config.token:
            self.session.headers.update({
                'Authorization': f'token {self.config.token}',
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'GitAI-CLI/1.0'
            })
    
    def authenticate(self, token: Optional[str] = None) -> bool:
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
            response = self.session.get(f"{self.config.api_base_url}/user")
            if response.status_code == 200:
                user_data = response.json()
                self.config.username = user_data.get('login')
                print(f"✅ Successfully authenticated as {self.config.username}")
                self._save_config()
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
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
            print(f"⚠️  Warning: Could not save config: {str(e)}")
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config.config_file):
                with open(self.config.config_file, 'r') as f:
                    config_data = json.load(f)
                    self.config.username = config_data.get('username')
                    self.config.api_base_url = config_data.get('api_base_url', self.config.api_base_url)
        except Exception as e:
            print(f"⚠️  Warning: Could not load config: {str(e)}")
    
    def get_user_repos(self, include_private: bool = True) -> List[Dict[str, Any]]:
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
                response = self.session.get(f"{self.config.api_base_url}/user/repos", params=params)
                if response.status_code == 200:
                    page_repos = response.json()
                    if not page_repos:
                        break
                    repos.extend(page_repos)
                    page += 1
                else:
                    print(f"❌ Failed to fetch repositories: {response.status_code}")
                    break
            except Exception as e:
                print(f"❌ Error fetching repositories: {str(e)}")
                break
        
        return repos
    
    def get_repo_info(self, owner: str, repo_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific repository
        
        Args:
            owner: Repository owner username
            repo_name: Repository name
            
        Returns:
            Repository information dictionary or None if not found
        """
        try:
            response = self.session.get(f"{self.config.api_base_url}/repos/{owner}/{repo_name}")
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print(f"❌ Repository {owner}/{repo_name} not found")
                return None
            else:
                print(f"❌ Failed to fetch repository info: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error fetching repository info: {str(e)}")
            return None
    
    def create_repository(self, name: str, description: str = "", private: bool = False) -> Optional[Dict[str, Any]]:
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
            response = self.session.post(f"{self.config.api_base_url}/user/repos", json=data)
            if response.status_code == 201:
                repo_data = response.json()
                print(f"✅ Successfully created repository: {repo_data['full_name']}")
                return repo_data
            else:
                print(f"❌ Failed to create repository: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error creating repository: {str(e)}")
            return None
    
    def get_repo_branches(self, owner: str, repo_name: str) -> List[Dict[str, Any]]:
        """
        Get list of branches for a repository
        
        Args:
            owner: Repository owner username
            repo_name: Repository name
            
        Returns:
            List of branch dictionaries
        """
        try:
            response = self.session.get(f"{self.config.api_base_url}/repos/{owner}/{repo_name}/branches")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to fetch branches: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error fetching branches: {str(e)}")
            return []
    
    def get_repo_commits(self, owner: str, repo_name: str, branch: str = "main", limit: int = 10) -> List[Dict[str, Any]]:
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
            response = self.session.get(f"{self.config.api_base_url}/repos/{owner}/{repo_name}/commits", params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to fetch commits: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error fetching commits: {str(e)}")
            return []
    
    def create_issue(self, owner: str, repo_name: str, title: str, body: str = "", labels: List[str] = None) -> Optional[Dict[str, Any]]:
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
            response = self.session.post(f"{self.config.api_base_url}/repos/{owner}/{repo_name}/issues", json=data)
            if response.status_code == 201:
                issue_data = response.json()
                print(f"✅ Successfully created issue #{issue_data['number']}: {title}")
                return issue_data
            else:
                print(f"❌ Failed to create issue: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error creating issue: {str(e)}")
            return None
    
    def get_repo_issues(self, owner: str, repo_name: str, state: str = "open") -> List[Dict[str, Any]]:
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
            response = self.session.get(f"{self.config.api_base_url}/repos/{owner}/{repo_name}/issues", params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to fetch issues: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error fetching issues: {str(e)}")
            return []


def setup_github_integration() -> GitHubIntegration:
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
        print(f"\n📁 Your repositories:")
        repos = github.get_user_repos()
        for repo in repos[:5]:  # Show first 5 repos
            print(f"  • {repo['full_name']} - {repo['description'] or 'No description'}")
