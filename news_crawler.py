#!/usr/bin/env python3
"""
新闻网站爬虫示例
爬取新闻标题、内容、发布时间等信息
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import random
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NewsCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
    
    def fetch_page(self, url, max_retries=3):
        """获取页面内容"""
        for attempt in range(max_retries):
            try:
                # 随机延迟，避免被封
                time.sleep(random.uniform(1, 3))
                
                response = self.session.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                
                # 检查编码
                response.encoding = response.apparent_encoding
                
                logger.info(f"成功获取页面: {url}")
                return response.text
                
            except Exception as e:
                logger.warning(f"获取页面失败 (尝试 {attempt + 1}/{max_retries}): {url} - {e}")
                if attempt == max_retries - 1:
                    return None
                time.sleep(2 ** attempt)  # 指数退避
    
    def parse_news_list(self, html, base_url):
        """解析新闻列表页"""
        soup = BeautifulSoup(html, 'html.parser')
        news_links = []
        
        # 示例：查找新闻链接（需要根据实际网站调整）
        # 常见的新闻链接选择器
        selectors = [
            'a[href*="news"]', 
            'a[href*="article"]',
            '.news-item a',
            '.article-list a',
            'h3 a',
            'h2 a'
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href', '')
                if href and not href.startswith('javascript'):
                    # 处理相对链接
                    if href.startswith('/'):
                        full_url = base_url + href
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        full_url = base_url + '/' + href
                    
                    # 过滤非新闻链接
                    if any(keyword in full_url.lower() for keyword in ['news', 'article', 'detail', 'content']):
                        news_links.append({
                            'url': full_url,
                            'title': link.get_text(strip=True)
                        })
        
        # 去重
        seen = set()
        unique_links = []
        for item in news_links:
            if item['url'] not in seen:
                seen.add(item['url'])
                unique_links.append(item)
        
        return unique_links[:20]  # 限制数量
    
    def parse_news_detail(self, html, url):
        """解析新闻详情页"""
        soup = BeautifulSoup(html, 'html.parser')
        
        news_data = {
            'url': url,
            'title': '',
            'publish_time': '',
            'author': '',
            'source': '',
            'content': '',
            'keywords': '',
            'summary': '',
            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 提取标题（多种可能的选择器）
        title_selectors = [
            'h1.article-title',
            'h1.news-title',
            'h1.title',
            '.article-header h1',
            '.news-header h1',
            'h1'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                news_data['title'] = title_elem.get_text(strip=True)
                break
        
        # 提取发布时间
        time_selectors = [
            '.publish-time',
            '.article-time',
            '.news-time',
            '.time',
            'time',
            '[datetime]'
        ]
        
        for selector in time_selectors:
            time_elem = soup.select_one(selector)
            if time_elem:
                news_data['publish_time'] = time_elem.get_text(strip=True)
                # 尝试获取datetime属性
                datetime_attr = time_elem.get('datetime')
                if datetime_attr:
                    news_data['publish_time'] = datetime_attr
                break
        
        # 提取作者
        author_selectors = [
            '.author',
            '.article-author',
            '.news-author',
            '.editor',
            '[rel="author"]'
        ]
        
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                news_data['author'] = author_elem.get_text(strip=True)
                break
        
        # 提取来源
        source_selectors = [
            '.source',
            '.article-source',
            '.news-source'
        ]
        
        for selector in source_selectors:
            source_elem = soup.select_one(selector)
            if source_elem:
                news_data['source'] = source_elem.get_text(strip=True)
                break
        
        # 提取正文内容
        content_selectors = [
            '.article-content',
            '.news-content',
            '.content',
            '.article-body',
            '.news-body',
            'article'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # 清理内容，移除脚本、样式等
                for tag in content_elem.select('script, style, iframe, nav, footer, header'):
                    tag.decompose()
                
                news_data['content'] = content_elem.get_text(strip=True, separator='\n')
                break
        
        # 如果没有找到内容，尝试提取所有段落
        if not news_data['content']:
            paragraphs = soup.select('p')
            if paragraphs:
                content_text = []
                for p in paragraphs[:20]:  # 限制段落数量
                    text = p.get_text(strip=True)
                    if len(text) > 20:  # 过滤短文本
                        content_text.append(text)
                news_data['content'] = '\n'.join(content_text)
        
        # 提取关键词
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            news_data['keywords'] = meta_keywords.get('content', '')
        
        # 提取摘要
        meta_description = soup.find('meta', attrs={'name': 'description'})
        if meta_description:
            news_data['summary'] = meta_description.get('content', '')
        
        return news_data
    
    def save_to_csv(self, data_list, filename='news_data.csv'):
        """保存数据到CSV"""
        if not data_list:
            logger.warning("没有数据可保存")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = data_list[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data_list)
        
        logger.info(f"数据已保存到: {filename} (共 {len(data_list)} 条记录)")
    
    def crawl_news_site(self, start_url, max_news=50):
        """爬取新闻网站"""
        logger.info(f"开始爬取新闻网站: {start_url}")
        
        all_news_data = []
        
        # 1. 获取新闻列表页
        list_html = self.fetch_page(start_url)
        if not list_html:
            logger.error("无法获取新闻列表页")
            return
        
        # 2. 解析新闻链接
        news_links = self.parse_news_list(list_html, start_url)
        logger.info(f"找到 {len(news_links)} 条新闻链接")
        
        # 3. 爬取每条新闻详情
        for i, link_info in enumerate(news_links[:max_news]):
            logger.info(f"正在处理新闻 {i+1}/{min(len(news_links), max_news)}: {link_info['title']}")
            
            detail_html = self.fetch_page(link_info['url'])
            if detail_html:
                news_data = self.parse_news_detail(detail_html, link_info['url'])
                all_news_data.append(news_data)
            
            # 显示进度
            if (i + 1) % 10 == 0:
                logger.info(f"进度: 已处理 {i+1} 条新闻")
        
        # 4. 保存数据
        if all_news_data:
            self.save_to_csv(all_news_data)
        
        logger.info(f"爬取完成！共获取 {len(all_news_data)} 条新闻")

# ==================== 使用示例 ====================

def example_crawl_sina_news():
    """爬取新浪新闻示例（需要根据实际网站结构调整）"""
    crawler = NewsCrawler()
    
    # 新浪新闻首页
    start_url = "https://news.sina.com.cn/"
    
    # 注意：实际爬取时需要遵守robots.txt和网站条款
    # 这里只是示例代码，可能需要调整选择器
    
    crawler.crawl_news_site(start_url, max_news=20)

def example_crawl_tech_news():
    """爬取科技新闻示例"""
    crawler = NewsCrawler()
    
    # 示例科技新闻网站
    tech_sites = [
        "https://tech.163.com/",  # 网易科技
        "https://www.ithome.com/",  # IT之家
        "https://www.cnbeta.com/",  # cnBeta
    ]
    
    all_tech_news = []
    
    for site_url in tech_sites:
        logger.info(f"开始爬取: {site_url}")
        
        list_html = crawler.fetch_page(site_url)
        if list_html:
            news_links = crawler.parse_news_list(list_html, site_url)
            
            for link_info in news_links[:10]:  # 每个站点爬10条
                detail_html = crawler.fetch_page(link_info['url'])
                if detail_html:
                    news_data = crawler.parse_news_detail(detail_html, link_info['url'])
                    all_tech_news.append(news_data)
        
        # 站点间延迟
        time.sleep(5)
    
    # 保存所有科技新闻
    if all_tech_news:
        crawler.save_to_csv(all_tech_news, 'tech_news.csv')
        logger.info(f"科技新闻爬取完成，共 {len(all_tech_news)} 条")

# ==================== 主程序 ====================

if __name__ == "__main__":
    print("新闻爬虫示例")
    print("=" * 50)
    print("注意：")
    print("1. 请遵守目标网站的robots.txt")
    print("2. 尊重版权，仅用于学习研究")
    print("3. 避免频繁请求，设置合理延迟")
    print("=" * 50)
    
    # 运行示例
    # example_crawl_sina_news()
    # example_crawl_tech_news()
    
    print("\n使用方法：")
    print("1. 创建NewsCrawler实例")
    print("2. 调用crawl_news_site(start_url, max_news)")
    print("3. 数据将自动保存为CSV文件")
    
    # 简单测试
    crawler = NewsCrawler()
    
    # 测试页面获取
    test_url = "https://www.baidu.com"
    html = crawler.fetch_page(test_url)
    if html:
        print(f"\n测试成功！获取到页面长度: {len(html)} 字符")
        
        # 解析测试
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string if soup.title else "无标题"
        print(f"页面标题: {title}")
    else:
        print("\n测试失败，请检查网络连接")