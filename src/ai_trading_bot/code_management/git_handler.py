import logging
from typing import Dict, Any
import aiohttp
from pathlib import Path
import subprocess
import asyncio

class GitHandler:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.code_management.git')
        self.repo_dir = Path(__file__).parent.parent.parent.parent
        self.github_token = self._get_github_token()
        self.api_base = "https://api.github.com"

    def _get_github_token(self) -> str:
        # Implement token retrieval from secure storage
        return ""

    async def create_branch(self, branch_name: str) -> bool:
        try:
            result = await self._run_command(
                f"git checkout -b {branch_name}"
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Failed to create branch: {e}")
            return False

    async def commit_changes(self, message: str) -> bool:
        try:
            # Stage changes
            await self._run_command("git add .")
            
            # Commit
            result = await self._run_command(
                ["git", "commit", "-m", message]
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Failed to commit changes: {e}")
            return False

    async def push_branch(self, branch_name: str) -> bool:
        try:
            result = await self._run_command(
                f"git push origin {branch_name}"
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Failed to push branch: {e}")
            return False

    async def create_pull_request(
        self,
        branch_name: str,
        title: str,
        description: str
    ) -> str:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/repos/owner/repo/pulls",
                    headers={
                        "Authorization": f"token {self.github_token}",
                        "Accept": "application/vnd.github.v3+json"
                    },
                    json={
                        "title": title,
                        "body": description,
                        "head": branch_name,
                        "base": "main"
                    }
                ) as response:
                    if response.status == 201:
                        data = await response.json()
                        return data['html_url']
                    else:
                        raise Exception(f"Failed to create PR: {response.status}")
        except Exception as e:
            self.logger.error(f"Failed to create pull request: {e}")
            raise

    async def get_pr_status(self, pr_url: str) -> Dict[str, Any]:
        try:
            pr_number = self._extract_pr_number(pr_url)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base}/repos/owner/repo/pulls/{pr_number}",
                    headers={
                        "Authorization": f"token {self.github_token}",
                        "Accept": "application/vnd.github.v3+json"
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'approved': data['mergeable'] and self._check_approvals(data),
                            'status': data['state'],
                            'reviews': data['reviews']
                        }
                    else:
                        raise Exception(f"Failed to get PR status: {response.status}")
        except Exception as e:
            self.logger.error(f"Failed to get PR status: {e}")
            raise

    async def merge_pr(self, pr_url: str) -> Dict[str, Any]:
        try:
            pr_number = self._extract_pr_number(pr_url)
            
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    f"{self.api_base}/repos/owner/repo/pulls/{pr_number}/merge",
                    headers={
                        "Authorization": f"token {self.github_token}",
                        "Accept": "application/vnd.github.v3+json"
                    },
                    json={
                        "merge_method": "squash"
                    }
                ) as response:
                    if response.status == 200:
                        return {
                            'success': True,
                            'message': 'PR merged successfully'
                        }
                    else:
                        return {
                            'success': False,
                            'error': f"Failed to merge PR: {response.status}"
                        }
        except Exception as e:
            self.logger.error(f"Failed to merge PR: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _run_command(self, command: str) -> subprocess.CompletedProcess:
        process = await asyncio.create_subprocess_shell(
            command,
            cwd=self.repo_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            self.logger.error(f"Command failed: {stderr.decode()}")
            
        return subprocess.CompletedProcess(
            args=command,
            returncode=process.returncode,
            stdout=stdout,
            stderr=stderr
        )

    def _extract_pr_number(self, pr_url: str) -> str:
        return pr_url.split('/')[-1]

    def _check_approvals(self, pr_data: Dict[str, Any]) -> bool:
        required_approvals = 1  # Configure as needed
        approvals = sum(
            1 for review in pr_data['reviews']
            if review['state'] == 'APPROVED'
        )
        return approvals >= required_approvals