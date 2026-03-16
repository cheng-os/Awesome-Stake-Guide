#!/usr/bin/env python3
"""
GitHub仓库管理脚本
用于管理 cheng-os/Awesome-Stake-Guide 仓库
"""

import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# 添加父目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from github_auto_uploader import GitHubAutoUploader

class GitHubRepoManager:
    """GitHub仓库管理器"""
    
    def __init__(self):
        self.repo_path = "/Users/wuyicheng/整理后/开发项目/个人项目/开发工具/Windsurf（AI编辑器）/GitHub仓库/Awesome-Stake-Guide"
        self.uploader = GitHubAutoUploader(use_api=False)  # 使用Git方式
        
    def show_status(self):
        """显示仓库状态"""
        print("📁 仓库状态信息")
        print("=" * 50)
        
        try:
            os.chdir(self.repo_path)
            
            # Git状态
            result = subprocess.run(['git', 'status'], capture_output=True, text=True)
            print("🔍 Git状态:")
            print(result.stdout)
            
            # 远程信息
            result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
            print("🔗 远程仓库:")
            print(result.stdout)
            
            # 最近提交
            result = subprocess.run(['git', 'log', '--oneline', '-5'], capture_output=True, text=True)
            print("📝 最近提交:")
            print(result.stdout)
            
        except Exception as e:
            print(f"❌ 获取状态失败: {e}")
    
    def pull_latest(self):
        """拉取最新代码"""
        print("🔄 拉取最新代码...")
        
        try:
            os.chdir(self.repo_path)
            result = subprocess.run(['git', 'pull', 'origin', 'main'], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ 拉取成功!")
                print(result.stdout)
            else:
                print("❌ 拉取失败!")
                print(result.stderr)
                
        except Exception as e:
            print(f"❌ 拉取失败: {e}")
    
    def add_and_commit(self, message=None):
        """添加并提交更改"""
        if not message:
            message = f"Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        print(f"📝 提交更改: {message}")
        
        try:
            os.chdir(self.repo_path)
            
            # 添加所有更改
            subprocess.run(['git', 'add', '.'], check=True)
            print("✅ 文件已添加到暂存区")
            
            # 提交
            result = subprocess.run(['git', 'commit', '-m', message], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ 提交成功!")
                print(result.stdout)
                return True
            else:
                print("❌ 提交失败!")
                print(result.stderr)
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Git操作失败: {e}")
            return False
        except Exception as e:
            print(f"❌ 提交失败: {e}")
            return False
    
    def push_to_github(self):
        """推送到GitHub"""
        print("🚀 推送到GitHub...")
        
        try:
            os.chdir(self.repo_path)
            result = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ 推送成功!")
                print(result.stdout)
                return True
            else:
                print("❌ 推送失败!")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ 推送失败: {e}")
            return False
    
    def sync_changes(self, message=None):
        """同步更改到GitHub (add + commit + push)"""
        if not message:
            message = f"Auto sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        print(f"🔄 同步更改到GitHub: {message}")
        
        # 1. 先拉取最新代码
        self.pull_latest()
        
        # 2. 添加并提交
        if self.add_and_commit(message):
            # 3. 推送到GitHub
            return self.push_to_github()
        
        return False
    
    def list_files(self):
        """列出仓库文件"""
        print("📂 仓库文件列表:")
        print("=" * 50)
        
        try:
            repo_path = Path(self.repo_path)
            
            def print_tree(path, prefix=""):
                items = sorted(path.iterdir())
                for i, item in enumerate(items):
                    if item.name.startswith('.git'):
                        continue
                    
                    is_last = i == len(items) - 1
                    current_prefix = "└── " if is_last else "├── "
                    print(f"{prefix}{current_prefix}{item.name}")
                    
                    if item.is_dir():
                        next_prefix = prefix + ("    " if is_last else "│   ")
                        print_tree(item, next_prefix)
            
            print_tree(repo_path)
            
        except Exception as e:
            print(f"❌ 列出文件失败: {e}")
    
    def open_repo_folder(self):
        """打开仓库文件夹"""
        try:
            subprocess.run(['open', self.repo_path], check=True)
            print(f"📁 已打开仓库文件夹: {self.repo_path}")
        except Exception as e:
            print(f"❌ 打开文件夹失败: {e}")
    
    def create_new_file(self, file_path, content=""):
        """创建新文件"""
        try:
            full_path = Path(self.repo_path) / file_path
            
            # 创建目录（如果不存在）
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入文件
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ 文件创建成功: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ 创建文件失败: {e}")
            return False

def main():
    """主菜单"""
    manager = GitHubRepoManager()
    
    while True:
        print("\n🚀 GitHub仓库管理器")
        print("=" * 30)
        print("1. 📊 查看仓库状态")
        print("2. 📂 列出仓库文件")
        print("3. 🔄 拉取最新代码")
        print("4. 📝 提交更改")
        print("5. 🚀 推送到GitHub")
        print("6. 🔄 同步更改 (add+commit+push)")
        print("7. 📁 打开仓库文件夹")
        print("8. ➕ 创建新文件")
        print("0. 🚪 退出")
        print("=" * 30)
        
        choice = input("请选择操作 (0-8): ").strip()
        
        if choice == '0':
            print("👋 再见!")
            break
        elif choice == '1':
            manager.show_status()
        elif choice == '2':
            manager.list_files()
        elif choice == '3':
            manager.pull_latest()
        elif choice == '4':
            message = input("输入提交信息 (留空使用默认): ").strip()
            manager.add_and_commit(message if message else None)
        elif choice == '5':
            manager.push_to_github()
        elif choice == '6':
            message = input("输入提交信息 (留空使用默认): ").strip()
            manager.sync_changes(message if message else None)
        elif choice == '7':
            manager.open_repo_folder()
        elif choice == '8':
            file_path = input("输入文件路径 (如: docs/new_file.md): ").strip()
            content = input("输入文件内容 (可选): ").strip()
            manager.create_new_file(file_path, content)
        else:
            print("❌ 无效选择，请重试")

if __name__ == "__main__":
    main()
