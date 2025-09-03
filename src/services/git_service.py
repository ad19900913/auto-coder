"""
Git服务模块 - 支持GitHub和GitLab等代码仓库操作
"""

import os
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import git
import requests


class GitService(ABC):
    """Git服务抽象基类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化Git服务
        
        Args:
            config: Git服务配置
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.token = config.get('token', '')
        self.username = config.get('username', '')
        
        if not self.token:
            raise ValueError("Git访问令牌不能为空")
    
    @abstractmethod
    def create_branch(self, repo_path: str, branch_name: str, base_branch: str = "main") -> bool:
        """
        创建新分支
        
        Args:
            repo_path: 仓库路径
            branch_name: 分支名称
            base_branch: 基础分支
            
        Returns:
            是否创建成功
        """
        pass
    
    @abstractmethod
    def commit_changes(self, repo_path: str, commit_message: str, files: List[str] = None) -> bool:
        """
        提交代码变更
        
        Args:
            repo_path: 仓库路径
            commit_message: 提交消息
            files: 要提交的文件列表，如果为None则提交所有变更
            
        Returns:
            是否提交成功
        """
        pass
    
    @abstractmethod
    def push_changes(self, repo_path: str, branch_name: str = None) -> bool:
        """
        推送代码变更
        
        Args:
            repo_path: 仓库路径
            branch_name: 分支名称，如果为None则使用当前分支
            
        Returns:
            是否推送成功
        """
        pass
    
    @abstractmethod
    def get_diff(self, repo_path: str, branch1: str, branch2: str = None) -> str:
        """
        获取分支差异
        
        Args:
            repo_path: 仓库路径
            branch1: 分支1
            branch2: 分支2，如果为None则与当前分支比较
            
        Returns:
            差异内容
        """
        pass
    
    @abstractmethod
    def clone_repository(self, repo_url: str, local_path: str) -> bool:
        """
        克隆仓库
        
        Args:
            repo_url: 仓库URL
            local_path: 本地路径
            
        Returns:
            是否克隆成功
        """
        pass


class GitHubService(GitService):
    """GitHub服务实现"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = "https://api.github.com"
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def create_branch(self, repo_path: str, branch_name: str, base_branch: str = "main") -> bool:
        """创建新分支"""
        try:
            # 检查目录是否存在
            if not os.path.exists(repo_path):
                os.makedirs(repo_path, exist_ok=True)
                self.logger.info(f"创建目录: {repo_path}")
            
            # 检查是否为Git仓库
            if not os.path.exists(os.path.join(repo_path, '.git')):
                self.logger.info(f"初始化Git仓库: {repo_path}")
                repo = git.Repo.init(repo_path)
                
                # 添加远程仓库（如果配置了repo_url）
                # 这里可以添加远程仓库配置逻辑
                
                # 创建初始提交
                try:
                    # 创建一个README文件作为初始提交
                    readme_path = os.path.join(repo_path, 'README.md')
                    with open(readme_path, 'w', encoding='utf-8') as f:
                        f.write(f"# {os.path.basename(repo_path)}\n\n自动生成的初始文件。")
                    
                    repo.index.add(['README.md'])
                    repo.index.commit("Initial commit")
                    self.logger.info("Git仓库初始化完成")
                except Exception as e:
                    self.logger.warning(f"创建初始提交失败: {e}")
            else:
                repo = git.Repo(repo_path)
            
            # 检查基础分支是否存在
            try:
                repo.git.checkout(base_branch)
            except git.exc.GitCommandError:
                # 如果基础分支不存在，创建它
                self.logger.info(f"基础分支 {base_branch} 不存在，创建新分支")
                repo.git.checkout('-b', base_branch)
            
            # 拉取最新代码（如果有远程仓库）
            try:
                repo.git.pull()
            except git.exc.GitCommandError:
                self.logger.debug("没有远程仓库或拉取失败，继续本地操作")
            
            # 创建新分支
            new_branch = repo.create_head(branch_name)
            new_branch.checkout()
            
            self.logger.info(f"分支创建成功: {branch_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"分支创建失败: {repo_path}")
            self.logger.error(f"错误详情: {e}")
            return False
    
    def commit_changes(self, repo_path: str, commit_message: str, files: List[str] = None) -> bool:
        """提交代码变更"""
        try:
            repo = git.Repo(repo_path)
            
            # 添加文件到暂存区
            if files:
                for file_path in files:
                    repo.index.add([file_path])
            else:
                repo.index.add('*')
            
            # 提交变更
            repo.index.commit(commit_message)
            
            self.logger.info(f"代码提交成功: {commit_message}")
            return True
            
        except Exception as e:
            self.logger.error(f"代码提交失败: {e}")
            return False
    
    def push_changes(self, repo_path: str, branch_name: str = None) -> bool:
        """推送代码变更"""
        try:
            repo = git.Repo(repo_path)
            
            if branch_name:
                current_branch = repo.active_branch
                if current_branch.name != branch_name:
                    repo.git.checkout(branch_name)
            
            # 推送到远程仓库
            origin = repo.remotes.origin
            origin.push()
            
            self.logger.info(f"代码推送成功: {branch_name or '当前分支'}")
            return True
            
        except Exception as e:
            self.logger.error(f"代码推送失败: {e}")
            return False
    
    def get_diff(self, repo_path: str, branch1: str, branch2: str = None) -> str:
        """获取分支差异"""
        try:
            repo = git.Repo(repo_path)
            
            if branch2 is None:
                branch2 = repo.active_branch.name
            
            # 获取差异
            diff = repo.git.diff(branch1, branch2)
            
            return diff
            
        except Exception as e:
            self.logger.error(f"获取差异失败: {e}")
            return ""
    
    def clone_repository(self, repo_url: str, local_path: str) -> bool:
        """克隆仓库"""
        try:
            # 构建带认证的URL
            if self.username and self.token:
                auth_url = repo_url.replace('https://', f'https://{self.username}:{self.token}@')
            else:
                auth_url = repo_url
            
            # 克隆仓库
            git.Repo.clone_from(auth_url, local_path)
            
            self.logger.info(f"仓库克隆成功: {local_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"仓库克隆失败: {e}")
            return False
    
    def create_pull_request(self, repo_owner: str, repo_name: str, title: str, 
                           body: str, head_branch: str, base_branch: str = "main") -> Optional[str]:
        """
        创建Pull Request
        
        Args:
            repo_owner: 仓库所有者
            repo_name: 仓库名称
            title: PR标题
            body: PR描述
            head_branch: 源分支
            base_branch: 目标分支
            
        Returns:
            PR URL，如果创建失败则返回None
        """
        try:
            url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/pulls"
            
            data = {
                'title': title,
                'body': body,
                'head': head_branch,
                'base': base_branch
            }
            
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code == 201:
                pr_data = response.json()
                pr_url = pr_data['html_url']
                self.logger.info(f"Pull Request创建成功: {pr_url}")
                return pr_url
            else:
                self.logger.error(f"Pull Request创建失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Pull Request创建异常: {e}")
            return None
    
    def get_repository_info(self, repo_owner: str, repo_name: str) -> Optional[Dict[str, Any]]:
        """获取仓库信息"""
        try:
            url = f"{self.base_url}/repos/{repo_owner}/{repo_name}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"获取仓库信息失败: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"获取仓库信息异常: {e}")
            return None


class GitLabService(GitService):
    """GitLab服务实现"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url', 'https://gitlab.com')
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def create_branch(self, repo_path: str, branch_name: str, base_branch: str = "main") -> bool:
        """创建新分支"""
        try:
            repo = git.Repo(repo_path)
            
            # 切换到基础分支
            repo.git.checkout(base_branch)
            repo.git.pull()
            
            # 创建新分支
            new_branch = repo.create_head(branch_name)
            new_branch.checkout()
            
            self.logger.info(f"分支创建成功: {branch_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"分支创建失败: {e}")
            return False
    
    def commit_changes(self, repo_path: str, commit_message: str, files: List[str] = None) -> bool:
        """提交代码变更"""
        try:
            repo = git.Repo(repo_path)
            
            # 添加文件到暂存区
            if files:
                for file_path in files:
                    repo.index.add([file_path])
            else:
                repo.index.add('*')
            
            # 提交变更
            repo.index.commit(commit_message)
            
            self.logger.info(f"代码提交成功: {commit_message}")
            return True
            
        except Exception as e:
            self.logger.error(f"代码提交失败: {e}")
            return False
    
    def push_changes(self, repo_path: str, branch_name: str = None) -> bool:
        """推送代码变更"""
        try:
            repo = git.Repo(repo_path)
            
            if branch_name:
                current_branch = repo.active_branch
                if current_branch.name != branch_name:
                    repo.git.checkout(branch_name)
            
            # 推送到远程仓库
            origin = repo.remotes.origin
            origin.push()
            
            self.logger.info(f"代码推送成功: {branch_name or '当前分支'}")
            return True
            
        except Exception as e:
            self.logger.error(f"代码推送失败: {e}")
            return False
    
    def get_diff(self, repo_path: str, branch1: str, branch2: str = None) -> str:
        """获取分支差异"""
        try:
            repo = git.Repo(repo_path)
            
            if branch2 is None:
                branch2 = repo.active_branch.name
            
            # 获取差异
            diff = repo.git.diff(branch1, branch2)
            
            return diff
            
        except Exception as e:
            self.logger.error(f"获取差异失败: {e}")
            return ""
    
    def clone_repository(self, repo_url: str, local_path: str) -> bool:
        """克隆仓库"""
        try:
            # 构建带认证的URL
            if self.username and self.token:
                auth_url = repo_url.replace('https://', f'https://{self.username}:{self.token}@')
            else:
                auth_url = repo_url
            
            # 克隆仓库
            git.Repo.clone_from(auth_url, local_path)
            
            self.logger.info(f"仓库克隆成功: {local_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"仓库克隆失败: {e}")
            return False
    
    def create_merge_request(self, project_id: str, title: str, body: str,
                           source_branch: str, target_branch: str = "main") -> Optional[str]:
        """
        创建Merge Request
        
        Args:
            project_id: 项目ID
            title: MR标题
            body: MR描述
            source_branch: 源分支
            target_branch: 目标分支
            
        Returns:
            MR URL，如果创建失败则返回None
        """
        try:
            url = f"{self.base_url}/api/v4/projects/{project_id}/merge_requests"
            
            data = {
                'title': title,
                'description': body,
                'source_branch': source_branch,
                'target_branch': target_branch
            }
            
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code == 201:
                mr_data = response.json()
                mr_url = mr_data['web_url']
                self.logger.info(f"Merge Request创建成功: {mr_url}")
                return mr_url
            else:
                self.logger.error(f"Merge Request创建失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Merge Request创建异常: {e}")
            return None
    
    def get_project_info(self, project_id: str) -> Optional[Dict[str, Any]]:
        """获取项目信息"""
        try:
            url = f"{self.base_url}/api/v4/projects/{project_id}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"获取项目信息失败: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"获取项目信息异常: {e}")
            return None


class GitServiceFactory:
    """Git服务工厂类"""
    
    @staticmethod
    def create_service(platform: str, config: Dict[str, Any]) -> GitService:
        """
        创建Git服务实例
        
        Args:
            platform: 平台名称（github, gitlab）
            config: 配置信息
            
        Returns:
            Git服务实例
        """
        if platform.lower() == 'github':
            return GitHubService(config)
        elif platform.lower() == 'gitlab':
            return GitLabService(config)
        else:
            raise ValueError(f"不支持的Git平台: {platform}")
    
    @staticmethod
    def create_service_from_config(config_manager, platform: str) -> GitService:
        """
        从配置管理器创建Git服务实例
        
        Args:
            config_manager: 配置管理器实例
            platform: 平台名称
            
        Returns:
            Git服务实例
        """
        git_config = config_manager.get_git_config(platform)
        if not git_config:
            raise ValueError(f"未找到{platform}的Git配置")
        
        return GitServiceFactory.create_service(platform, git_config)
