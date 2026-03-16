#!/bin/bash

echo "🚀 开始强制同步到GitHub..."

# 进入仓库目录
cd "/Users/wuyicheng/整理后/开发项目/个人项目/开发工具/Windsurf（AI编辑器）/GitHub仓库/Awesome-Stake-Guide"

# 检查状态
echo "📊 检查仓库状态..."
git status

# 强制推送
echo "🔄 强制推送所有更改..."
git push origin main --force

# 检查结果
if [ $? -eq 0 ]; then
    echo "✅ 同步成功！"
    echo "📝 最新提交："
    git log --oneline -1
else
    echo "❌ 同步失败，请检查网络连接"
    exit 1
fi

echo "🎯 云端仓库已更新完成！"
