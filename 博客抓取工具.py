#!/usr/bin/env python3
"""
Blogspot 博客抓取工具
抓取 chengx23.blogspot.com 的所有文章并转换为静态网页
"""

import requests
import re
import os
import time
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse

class BlogspotScraper:
    """Blogspot 博客抓取器"""
    
    def __init__(self, blog_url="https://chengx23.blogspot.com/"):
        self.blog_url = blog_url
        self.base_url = "https://chengx23.blogspot.com"
        self.posts = []
        self.session = requests.Session()
        
        # 设置请求头，模拟浏览器
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def get_page_content(self, url, retries=3):
        """获取页面内容"""
        for attempt in range(retries):
            try:
                print(f"🔄 正在获取: {url} (尝试 {attempt + 1}/{retries})")
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return response.text
            except requests.exceptions.RequestException as e:
                print(f"❌ 请求失败 (尝试 {attempt + 1}): {e}")
                if attempt < retries - 1:
                    time.sleep(2)
                else:
                    return None
        return None
    
    def extract_posts_from_page(self, html_content):
        """从页面中提取文章信息"""
        soup = BeautifulSoup(html_content, 'html.parser')
        posts = []
        
        # Blogspot 文章通常在 .post 或 .blog-post 类中
        post_elements = soup.find_all(['div', 'article'], class_=re.compile(r'post|blog-post|entry'))
        
        for post_element in post_elements:
            try:
                # 提取标题
                title_elem = post_element.find(['h1', 'h2', 'h3'], class_=re.compile(r'title|post-title'))
                if not title_elem:
                    title_elem = post_element.find('a', class_=re.compile(r'title'))
                
                title = title_elem.get_text(strip=True) if title_elem else "无标题"
                
                # 提取链接
                link_elem = post_element.find('a', href=True)
                if link_elem:
                    link = link_elem['href']
                    if link.startswith('/'):
                        link = urljoin(self.base_url, link)
                else:
                    continue
                
                # 提取日期
                date_elem = post_element.find(['time', 'span', 'abbr'], class_=re.compile(r'date|published|timestamp'))
                if date_elem:
                    date = date_elem.get_text(strip=True)
                else:
                    date = "未知日期"
                
                # 提取摘要
                content_elem = post_element.find(['div', 'p'], class_=re.compile(r'content|summary|excerpt'))
                if not content_elem:
                    content_elem = post_element.find('div', class_='post-body')
                
                summary = ""
                if content_elem:
                    # 获取前200个字符作为摘要
                    text = content_elem.get_text(strip=True)
                    summary = text[:200] + "..." if len(text) > 200 else text
                
                posts.append({
                    'title': title,
                    'link': link,
                    'date': date,
                    'summary': summary
                })
                
            except Exception as e:
                print(f"⚠️ 解析文章时出错: {e}")
                continue
        
        return posts
    
    def get_all_posts(self):
        """获取所有文章"""
        print("🚀 开始抓取博客文章...")
        
        # 首先获取主页
        main_content = self.get_page_content(self.blog_url)
        if not main_content:
            print("❌ 无法获取主页内容")
            return []
        
        # 从主页提取文章
        posts = self.extract_posts_from_page(main_content)
        print(f"📄 从主页找到 {len(posts)} 篇文章")
        
        # 尝试获取更多页面（如果有分页）
        soup = BeautifulSoup(main_content, 'html.parser')
        
        # 查找 older-posts 链接
        older_link = soup.find('a', class_=re.compile(r'older|next|previous'))
        
        page_count = 1
        while older_link and page_count < 10:  # 限制最多10页
            try:
                older_url = older_link.get('href')
                if older_url.startswith('/'):
                    older_url = urljoin(self.base_url, older_url)
                
                print(f"🔄 获取第 {page_count + 1} 页...")
                page_content = self.get_page_content(older_url)
                
                if not page_content:
                    break
                
                page_posts = self.extract_posts_from_page(page_content)
                if not page_posts:
                    break
                
                posts.extend(page_posts)
                print(f"📄 第 {page_count + 1} 页找到 {len(page_posts)} 篇文章")
                
                # 查找下一页链接
                soup = BeautifulSoup(page_content, 'html.parser')
                older_link = soup.find('a', class_=re.compile(r'older|next|previous'))
                
                page_count += 1
                time.sleep(1)  # 避免请求过快
                
            except Exception as e:
                print(f"❌ 获取第 {page_count + 1} 页时出错: {e}")
                break
        
        # 去重
        seen_links = set()
        unique_posts = []
        for post in posts:
            if post['link'] not in seen_links:
                seen_links.add(post['link'])
                unique_posts.append(post)
        
        self.posts = unique_posts
        print(f"✅ 总共找到 {len(self.posts)} 篇 unique 文章")
        return self.posts
    
    def get_post_content(self, post_url):
        """获取单篇文章的完整内容"""
        content = self.get_page_content(post_url)
        if not content:
            return None
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # 查找文章内容
        content_elem = soup.find(['div', 'article'], class_=re.compile(r'post-body|entry-content|content'))
        
        if not content_elem:
            content_elem = soup.find('div', class_='post-body')
        
        if not content_elem:
            return None
        
        # 清理内容
        # 移除不必要的标签
        for tag in content_elem.find_all(['script', 'style', 'nav', 'footer', 'aside']):
            tag.decompose()
        
        # 获取标题
        title_elem = soup.find(['h1', 'h2'], class_=re.compile(r'title|post-title'))
        title = title_elem.get_text(strip=True) if title_elem else "无标题"
        
        # 获取日期
        date_elem = soup.find(['time', 'span', 'abbr'], class_=re.compile(r'date|published|timestamp'))
        date = date_elem.get_text(strip=True) if date_elem else "未知日期"
        
        return {
            'title': title,
            'date': date,
            'content': str(content_elem),
            'url': post_url
        }
    
    def generate_html_page(self, post_data, filename):
        """生成HTML页面"""
        html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{post_data['title']} - Chengx Blog</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/css/bootstrap.min.css">
    <link rel="stylesheet" href="style.css">
    <meta name="description" content="{post_data['title']} - Chengx的个人博客文章">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="index.html">🚀 Chengx Blog</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="index.html">🏠 首页</a>
                <a class="nav-link" href="https://chengx23.blogspot.com" target="_blank">📝 原博客</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-lg-8">
                <article class="blog-post">
                    <header class="mb-4">
                        <h1 class="display-4">{post_data['title']}</h1>
                        <div class="text-muted mb-3">
                            <small>📅 发布时间: {post_data['date']}</small>
                        </div>
                    </header>
                    
                    <div class="post-content">
                        {post_data['content']}
                    </div>
                    
                    <footer class="mt-5 pt-4 border-top">
                        <div class="d-flex justify-content-between">
                            <a href="index.html" class="btn btn-outline-primary">← 返回首页</a>
                            <a href="{post_data['url']}" class="btn btn-outline-secondary" target="_blank">📖 查看原文</a>
                        </div>
                    </footer>
                </article>
            </div>
            
            <div class="col-lg-4">
                <div class="card">
                    <div class="card-header">
                        <h5 class="card-title mb-0">🔗 相关链接</h5>
                    </div>
                    <div class="card-body">
                        <ul class="list-unstyled">
                            <li><a href="https://cheng-os.github.io/Awesome-Stake-Guide/" target="_blank">🎰 Stake攻略</a></li>
                            <li><a href="https://chengx23.blogspot.com" target="_blank">📝 原博客</a></li>
                            <li><a href="https://github.com/cheng-os" target="_blank">💻 GitHub</a></li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-light mt-5 py-4">
        <div class="container text-center">
            <p>&copy; 2026 Chengx Blog. All rights reserved.</p>
        </div>
    </footer>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
        
        return html_template
    
    def save_posts_to_files(self, output_dir="posts"):
        """保存文章到文件"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print(f"💾 开始保存文章到 {output_path}...")
        
        for i, post in enumerate(self.posts):
            try:
                print(f"📄 正在处理: {post['title']}")
                
                # 获取完整内容
                full_post = self.get_post_content(post['link'])
                if not full_post:
                    print(f"⚠️ 跳过文章: {post['title']} (无法获取内容)")
                    continue
                
                # 生成文件名
                safe_title = re.sub(r'[^\w\s-]', '', post['title'])
                safe_title = re.sub(r'[-\s]+', '-', safe_title)
                filename = f"{i+1:03d}-{safe_title[:50]}.html"
                
                # 生成HTML
                html_content = self.generate_html_page(full_post, filename)
                
                # 保存文件
                file_path = output_path / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                print(f"✅ 已保存: {filename}")
                
                # 添加延迟避免请求过快
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ 处理文章失败: {post['title']} - {e}")
                continue
        
        print(f"🎉 文章保存完成! 保存在 {output_path} 目录")
    
    def generate_index_page(self, posts_dir="posts"):
        """生成主页索引"""
        posts_path = Path(posts_dir)
        if not posts_path.exists():
            return
        
        # 获取所有HTML文件
        html_files = list(posts_path.glob("*.html"))
        html_files.sort()
        
        # 生成文章列表
        articles_html = ""
        for html_file in html_files:
            try:
                # 从文件名提取标题
                title = html_file.stem[4:]  # 移除数字前缀
                title = title.replace('-', ' ').title()
                
                # 提取对应的信息
                post_info = next((p for p in self.posts if title.lower() in p['title'].lower()), None)
                
                if post_info:
                    articles_html += f"""
                    <div class="card mb-3">
                        <div class="card-body">
                            <h5 class="card-title">
                                <a href="{posts_dir}/{html_file.name}" class="text-decoration-none">
                                    {post_info['title']}
                                </a>
                            </h5>
                            <p class="card-text text-muted">{post_info['summary']}</p>
                            <small class="text-muted">📅 {post_info['date']}</small>
                        </div>
                    </div>
                    """
                
            except Exception as e:
                print(f"⚠️ 处理文件 {html_file} 时出错: {e}")
        
        index_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chengx Blog - 个人博客</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/css/bootstrap.min.css">
    <link rel="stylesheet" href="style.css">
    <meta name="description" content="Chengx的个人博客，分享技术心得和生活感悟">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="index.html">🚀 Chengx Blog</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link active" href="index.html">🏠 首页</a>
                <a class="nav-link" href="https://chengx23.blogspot.com" target="_blank">📝 原博客</a>
                <a class="nav-link" href="https://cheng-os.github.io/Awesome-Stake-Guide/" target="_blank">🎰 Stake攻略</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-lg-8">
                <header class="text-center mb-5">
                    <h1 class="display-4">🚀 Chengx Blog</h1>
                    <p class="lead">欢迎来到我的个人博客，这里记录着我的技术心得、项目经验和思考感悟。</p>
                </header>

                <section id="articles">
                    <h2 class="mb-4">📝 最新文章</h2>
                    {articles_html}
                </section>
            </div>
            
            <div class="col-lg-4">
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="card-title mb-0">🔗 相关链接</h5>
                    </div>
                    <div class="card-body">
                        <ul class="list-unstyled">
                            <li><a href="https://cheng-os.github.io/Awesome-Stake-Guide/" target="_blank">🎰 Stake攻略</a></li>
                            <li><a href="https://chengx23.blogspot.com" target="_blank">📝 原博客</a></li>
                            <li><a href="https://github.com/cheng-os" target="_blank">💻 GitHub</a></li>
                        </ul>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h5 class="card-title mb-0">📊 博客统计</h5>
                    </div>
                    <div class="card-body">
                        <ul class="list-unstyled">
                            <li>📄 文章总数: {len(html_files)}</li>
                            <li>🔄 最后更新: {datetime.now().strftime('%Y-%m-%d')}</li>
                            <li>🌐 原博客: <a href="https://chengx23.blogspot.com" target="_blank">Blogspot</a></li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-light mt-5 py-4">
        <div class="container text-center">
            <p>&copy; 2026 Chengx Blog. All rights reserved.</p>
        </div>
    </footer>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
        
        # 保存主页
        with open('blog_index.html', 'w', encoding='utf-8') as f:
            f.write(index_template)
        
        print("✅ 主页索引已生成: blog_index.html")
    
    def run(self):
        """运行完整的抓取流程"""
        try:
            # 1. 获取所有文章列表
            posts = self.get_all_posts()
            
            if not posts:
                print("❌ 没有找到任何文章")
                return
            
            # 2. 保存文章到文件
            self.save_posts_to_files()
            
            # 3. 生成主页索引
            self.generate_index_page()
            
            print("🎉 博客抓取完成!")
            print(f"📊 总共处理了 {len(posts)} 篇文章")
            print("📁 文件已保存在当前目录的 posts/ 文件夹中")
            print("🏠 主页索引: blog_index.html")
            
        except Exception as e:
            print(f"❌ 抓取过程中出错: {e}")

def main():
    """主函数"""
    print("🚀 Blogspot 博客抓取工具")
    print("=" * 50)
    
    scraper = BlogspotScraper()
    scraper.run()

if __name__ == "__main__":
    main()
