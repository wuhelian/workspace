#!/usr/bin/env python3
"""
通用Python爬虫模板
支持：请求重试、代理、User-Agent轮换、数据保存
"""

import requests
import time
import random
import csv
import json
import os
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import urljoin, urlparse
import logging
from typing import List, Dict, Optional
import re

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebCrawler:
    """通用网页爬虫类"""
    
    def __init__(self, 
                 base_url: str,
                 output_dir: str = "data",
                 delay: float = 1.0,
                 max_retries: int = 3,
                 use_proxy: bool = False):
        """
        初始化爬虫
        
        Args:
            base_url: 基础URL
            output_dir: 输出目录
            delay: 请求延迟（秒）
            max_retries: 最大重试次数
            use_proxy: 是否使用代理
        """
        self.base_url = base_url
        self.output_dir = output_dir
        self.delay = delay
        self.max_retries = max_retries
        self.use_proxy = use_proxy
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 初始化User-Agent生成器
        self.ua = UserAgent()
        
        # 初始化会话
        self.session = requests.Session()
        
        # 设置请求头
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # 代理列表（如果需要）
        self.proxies = [
            # 添加您的代理服务器
            # 'http://user:pass@host:port',
            # 'https://user:pass@host:port',
        ]
        
        logger.info(f"爬虫初始化完成，目标网站: {base_url}")
    
    def get_random_headers(self) -> Dict:
        """获取随机请求头"""
        headers = self.headers.copy()
        headers['User-Agent'] = self.ua.random
        return headers
    
    def get_random_proxy(self) -> Optional[Dict]:
        """获取随机代理"""
        if self.proxies and self.use_proxy:
            proxy = random.choice(self.proxies)
            return {
                'http': proxy,
                'https': proxy
            }
        return None
    
    def make_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """
        发送HTTP请求，支持重试
        
        Args:
            url: 请求URL
            method: 请求方法
            **kwargs: 其他请求参数
            
        Returns:
            Response对象或None
        """
        for attempt in range(self.max_retries):
            try:
                # 随机延迟，避免被封
                time.sleep(self.delay + random.uniform(0, 0.5))
                
                # 准备请求参数
                headers = self.get_random_headers()
                proxies = self.get_random_proxy()
                
                # 发送请求
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    proxies=proxies,
                    timeout=30,
                    **kwargs
                )
                
                # 检查响应状态
                response.raise_for_status()
                
                # 检查内容类型
                content_type = response.headers.get('Content-Type', '')
                if 'text/html' not in content_type and 'application/json' not in content_type:
                    logger.warning(f"非文本/JSON响应: {content_type}")
                
                logger.info(f"成功获取: {url} (状态码: {response.status_code})")
                return response
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{self.max_retries}): {url} - {e}")
                if attempt == self.max_retries - 1:
                    logger.error(f"最终失败: {url}")
                    return None
                # 重试前等待
                time.sleep(2 ** attempt)  # 指数退避
    
    def extract_links(self, html: str, base_url: str) -> List[str]:
        """
        从HTML中提取链接
        
        Args:
            html: HTML内容
            base_url: 基础URL
            
        Returns:
            链接列表
        """
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            # 处理相对链接
            absolute_url = urljoin(base_url, href)
            # 过滤非HTTP链接和锚点
            if absolute_url.startswith('http') and '#' not in absolute_url:
                links.append(absolute_url)
        
        return list(set(links))  # 去重
    
    def save_to_csv(self, data: List[Dict], filename: str):
        """
        保存数据到CSV文件
        
        Args:
            data: 数据列表
            filename: 文件名
        """
        if not data:
            logger.warning("没有数据可保存")
            return
        
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            # 获取所有字段
            fieldnames = data[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        logger.info(f"数据已保存到: {filepath} (共 {len(data)} 条记录)")
    
    def save_to_json(self, data: List[Dict], filename: str):
        """
        保存数据到JSON文件
        
        Args:
            data: 数据列表
            filename: 文件名
        """
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据已保存到: {filepath} (共 {len(data)} 条记录)")
    
    def crawl_page(self, url: str) -> Optional[Dict]:
        """
        爬取单个页面（需要根据具体网站重写此方法）
        
        Args:
            url: 页面URL
            
        Returns:
            提取的数据字典
        """
        response = self.make_request(url)
        if not response:
            return None
        
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 示例：提取标题和正文
        data = {
            'url': url,
            'title': '',
            'content': '',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 提取标题
        title_tag = soup.find('title')
        if title_tag:
            data['title'] = title_tag.get_text(strip=True)
        
        # 提取正文（简单示例）
        # 这里需要根据具体网站结构调整
        content_div = soup.find('div', class_=re.compile(r'content|article|main'))
        if content_div:
            data['content'] = content_div.get_text(strip=True, separator='\n')
        else:
            # 备用方案：提取所有段落
            paragraphs = soup.find_all('p')
            if paragraphs:
                data['content'] = '\n'.join([p.get_text(strip=True) for p in paragraphs])
        
        return data
    
    def crawl_site(self, start_url: str, max_pages: int = 100):
        """
        爬取整个网站
        
        Args:
            start_url: 起始URL
            max_pages: 最大爬取页面数
        """
        visited = set()
        to_visit = [start_url]
        all_data = []
        
        page_count = 0
        
        while to_visit and page_count < max_pages:
            current_url = to_visit.pop(0)
            
            if current_url in visited:
                continue
            
            logger.info(f"正在爬取 ({page_count + 1}/{max_pages}): {current_url}")
            
            # 爬取当前页面
            data = self.crawl_page(current_url)
            if data:
                all_data.append(data)
            
            visited.add(current_url)
            page_count += 1
            
            # 获取页面中的链接
            response = self.make_request(current_url)
            if response:
                links = self.extract_links(response.text, current_url)
                # 只添加未访问过的链接
                new_links = [link for link in links if link not in visited and link not in to_visit]
                to_visit.extend(new_links[:10])  # 限制每次添加的链接数
            
            # 显示进度
            if page_count % 10 == 0:
                logger.info(f"进度: 已爬取 {page_count} 页，待爬取 {len(to_visit)} 页")
        
        # 保存数据
        if all_data:
            self.save_to_csv(all_data, 'crawled_data.csv')
            self.save_to_json(all_data, 'crawled_data.json')
        
        logger.info(f"爬取完成！共爬取 {page_count} 个页面")

# ==================== 使用示例 ====================

def example_news_crawler():
    """新闻网站爬虫示例"""
    crawler = WebCrawler(
        base_url="https://news.example.com",
        output_dir="news_data",
        delay=2.0,  # 增加延迟，避免被封
        max_retries=5
    )
    
    # 自定义新闻页面解析
    def parse_news_page(url: str) -> Optional[Dict]:
        response = crawler.make_request(url)
        if not response:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取新闻信息
        data = {
            'url': url,
            'title': '',
            'author': '',
            'publish_date': '',
            'content': '',
            'category': ''
        }
        
        # 根据实际网站结构调整选择器
        data['title'] = soup.select_one('h1.article-title').get_text(strip=True) if soup.select_one('h1.article-title') else ''
        data['author'] = soup.select_one('.author-name').get_text(strip=True) if soup.select_one('.author-name') else ''
        data['publish_date'] = soup.select_one('.publish-date').get_text(strip=True) if soup.select_one('.publish-date') else ''
        
        # 提取正文
        content_div = soup.select_one('.article-content')
        if content_div:
            data['content'] = content_div.get_text(strip=True, separator='\n')
        
        return data
    
    # 替换默认的爬取方法
    crawler.crawl_page = parse_news_page
    
    # 开始爬取
    crawler.crawl_site("https://news.example.com/latest", max_pages=50)

def example_ecommerce_crawler():
    """电商网站爬虫示例"""
    crawler = WebCrawler(
        base_url="https://shop.example.com",
        output_dir="product_data",
        delay=1.5
    )
    
    def parse_product_page(url: str) -> Optional[Dict]:
        response = crawler.make_request(url)
        if not response:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {
            'url': url,
            'name': '',
            'price': '',
            'description': '',
            'rating': '',
            'reviews_count': '',
            'category': ''
        }
        
        # 提取商品信息
        data['name'] = soup.select_one('h1.product-title').get_text(strip=True) if soup.select_one('h1.product-title') else ''
        data['price'] = soup.select_one('.product-price').get_text(strip=True) if soup.select_one('.product-price') else ''
        data['description'] = soup.select_one('.product-description').get_text(strip=True) if soup.select_one('.product-description') else ''
        
        return data
    
    crawler.crawl_page = parse_product_page
    crawler.crawl_site("https://shop.example.com/products", max_pages=100)

# ==================== 主程序 ====================

if __name__ == "__main__":
    print("Python爬虫模板")
    print("=" * 50)
    print("请根据您的需求修改以下部分：")
    print("1. 在 crawl_page 方法中编写页面解析逻辑")
    print("2. 调整请求参数（延迟、重试次数等）")
    print("3. 根据目标网站结构调整CSS选择器")
    print("=" * 50)
    
    # 示例：简单的百度搜索爬虫
    def simple_baidu_search():
        """百度搜索爬虫示例"""
        crawler = WebCrawler(
            base_url="https://www.baidu.com",
            output_dir="baidu_search",
            delay=1.0
        )
        
        # 搜索关键词
        keywords = ["人工智能", "机器学习", "深度学习"]
        
        all_results = []
        
        for keyword in keywords:
            logger.info(f"搜索关键词: {keyword}")
            
            # 构造搜索URL
            search_url = f"https://www.baidu.com/s?wd={keyword}"
            
            response = crawler.make_request(search_url)
            if response:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 提取搜索结果
                results = soup.select('.result')
                for i, result in enumerate(results[:10]):  # 只取前10个结果
                    title_elem = result.select_one('h3 a')
                    if title_elem:
                        result_data = {
                            'keyword': keyword,
                            'rank': i + 1,
                            'title': title_elem.get_text(strip=True),
                            'url': title_elem.get('href', ''),
                            'brief': result.select_one('.c-abstract').get_text(strip=True) if result.select_one('.c-abstract') else ''
                        }
                        all_results.append(result_data)
            
            # 避免请求过快
            time.sleep(2)
        
        # 保存结果
        if all_results:
            crawler.save_to_csv(all_results, 'baidu_search_results.csv')
            logger.info(f"搜索完成，共获取 {len(all_results)} 条结果")
    
    # 运行示例
    # simple_baidu_search()
    
    print("\n使用方法：")
    print("1. 根据目标网站修改 crawl_page 方法")
    print("2. 调用 crawler.crawl_site(start_url, max_pages) 开始爬取")
    print("3. 数据将自动保存到 output_dir 目录")