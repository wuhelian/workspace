#!/usr/bin/env python3
"""
电商商品爬虫示例
爬取商品信息：名称、价格、评价、详情等
"""

import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import random
import re
import logging
from urllib.parse import urljoin, urlparse
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EcommerceCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
        }
        
        # 电商网站配置
        self.site_configs = {
            'jd': {
                'list_selector': '.gl-item',
                'title_selector': '.p-name em',
                'price_selector': '.p-price i',
                'comment_selector': '.p-commit a',
                'shop_selector': '.p-shop span a',
                'next_page_selector': '.pn-next'
            },
            'taobao': {
                'list_selector': '.item.J_MouserOnverReq',
                'title_selector': '.title a',
                'price_selector': '.price strong',
                'sales_selector': '.deal-cnt',
                'shop_selector': '.shopname span',
                'next_page_selector': '.next'
            },
            'tmall': {
                'list_selector': '.product-iWrap',
                'title_selector': '.productTitle a',
                'price_selector': '.productPrice em',
                'sales_selector': '.productStatus em',
                'shop_selector': '.productShop-name a',
                'next_page_selector': '.ui-page-next'
            }
        }
    
    def detect_site(self, url):
        """检测网站类型"""
        domain = urlparse(url).netloc.lower()
        
        if 'jd.com' in domain or 'jingdong' in domain:
            return 'jd'
        elif 'taobao.com' in domain:
            return 'taobao'
        elif 'tmall.com' in domain:
            return 'tmall'
        else:
            return 'unknown'
    
    def fetch_page(self, url, max_retries=3):
        """获取页面内容"""
        for attempt in range(max_retries):
            try:
                # 随机延迟
                delay = random.uniform(2, 5)  # 电商网站需要更长的延迟
                time.sleep(delay)
                
                response = self.session.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                
                # 处理编码
                if 'charset' in response.headers.get('Content-Type', ''):
                    response.encoding = response.apparent_encoding
                else:
                    response.encoding = 'utf-8'
                
                logger.info(f"成功获取页面: {url}")
                return response.text
                
            except Exception as e:
                logger.warning(f"获取页面失败 (尝试 {attempt + 1}/{max_retries}): {url} - {e}")
                if attempt == max_retries - 1:
                    return None
                time.sleep(3 ** attempt)  # 更长的退避时间
    
    def parse_product_list(self, html, base_url, site_type='unknown'):
        """解析商品列表页"""
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # 获取网站配置
        config = self.site_configs.get(site_type, {})
        
        # 查找商品列表
        list_selector = config.get('list_selector', '.item, .product, .goods')
        product_items = soup.select(list_selector)
        
        logger.info(f"找到 {len(product_items)} 个商品项")
        
        for item in product_items[:50]:  # 限制数量
            product_info = {
                'site': site_type,
                'url': '',
                'title': '',
                'price': '',
                'original_price': '',
                'sales': '',
                'comments': '',
                'shop': '',
                'location': '',
                'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 提取商品链接
            link_selectors = ['a', '.title a', '.name a', '.pic a']
            for selector in link_selectors:
                link_elem = item.select_one(selector)
                if link_elem and link_elem.get('href'):
                    href = link_elem['href']
                    if href.startswith('//'):
                        href = 'https:' + href
                    elif href.startswith('/'):
                        href = urljoin(base_url, href)
                    elif not href.startswith('http'):
                        href = urljoin(base_url, '/' + href)
                    
                    product_info['url'] = href
                    break
            
            # 提取商品标题
            title_selector = config.get('title_selector', '.title, .name, h3, h4')
            title_elem = item.select_one(title_selector)
            if title_elem:
                product_info['title'] = title_elem.get_text(strip=True)
            
            # 提取价格
            price_selector = config.get('price_selector', '.price, .cost, .money')
            price_elem = item.select_one(price_selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                # 提取数字
                price_numbers = re.findall(r'\d+\.?\d*', price_text)
                if price_numbers:
                    product_info['price'] = price_numbers[0]
            
            # 提取原价（如果有）
            original_price_elem = item.select_one('.original-price, .market-price, del')
            if original_price_elem:
                original_text = original_price_elem.get_text(strip=True)
                original_numbers = re.findall(r'\d+\.?\d*', original_text)
                if original_numbers:
                    product_info['original_price'] = original_numbers[0]
            
            # 提取销量
            sales_selector = config.get('sales_selector', '.sales, .deal-cnt, .volume')
            sales_elem = item.select_one(sales_selector)
            if sales_elem:
                sales_text = sales_elem.get_text(strip=True)
                # 提取数字
                sales_numbers = re.findall(r'\d+', sales_text)
                if sales_numbers:
                    product_info['sales'] = sales_numbers[0]
            
            # 提取评价数
            comment_selector = config.get('comment_selector', '.comment, .review, .rate')
            comment_elem = item.select_one(comment_selector)
            if comment_elem:
                comment_text = comment_elem.get_text(strip=True)
                comment_numbers = re.findall(r'\d+', comment_text)
                if comment_numbers:
                    product_info['comments'] = comment_numbers[0]
            
            # 提取店铺
            shop_selector = config.get('shop_selector', '.shop, .store, .seller')
            shop_elem = item.select_one(shop_selector)
            if shop_elem:
                product_info['shop'] = shop_elem.get_text(strip=True)
            
            # 提取发货地
            location_elem = item.select_one('.location, .place, .addr')
            if location_elem:
                product_info['location'] = location_elem.get_text(strip=True)
            
            # 只保存有标题和价格的产品
            if product_info['title'] and product_info['price']:
                products.append(product_info)
        
        return products
    
    def parse_product_detail(self, html, url, site_type='unknown'):
        """解析商品详情页"""
        soup = BeautifulSoup(html, 'html.parser')
        
        detail_info = {
            'url': url,
            'site': site_type,
            'brand': '',
            'model': '',
            'category': '',
            'description': '',
            'specifications': {},
            'images': [],
            'rating': '',
            'review_count': '',
            'positive_rate': '',
            'service_score': '',
            'logistics_score': '',
            'warranty': '',
            'delivery': '',
            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 提取品牌
        brand_selectors = ['.brand', '[itemprop="brand"]', 'li:contains("品牌")']
        for selector in brand_selectors:
            brand_elem = soup.select_one(selector)
            if brand_elem:
                detail_info['brand'] = brand_elem.get_text(strip=True).replace('品牌：', '').replace('品牌:', '')
                break
        
        # 提取型号
        model_selectors = ['.model', '[itemprop="model"]', 'li:contains("型号")']
        for selector in model_selectors:
            model_elem = soup.select_one(selector)
            if model_elem:
                detail_info['model'] = model_elem.get_text(strip=True).replace('型号：', '').replace('型号:', '')
                break
        
        # 提取分类
        breadcrumb = soup.select('.breadcrumb, .crumb, .path a')
        if breadcrumb:
            categories = [item.get_text(strip=True) for item in breadcrumb]
            detail_info['category'] = ' > '.join(categories)
        
        # 提取商品描述
        desc_selectors = ['.description', '.detail', '.desc', '[itemprop="description"]']
        for selector in desc_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                detail_info['description'] = desc_elem.get_text(strip=True, separator='\n')[:1000]  # 限制长度
                break
        
        # 提取规格参数
        spec_table = soup.select_one('.spec-table, .params-table, .Ptable')
        if spec_table:
            specs = {}
            rows = spec_table.select('tr')
            for row in rows:
                cells = row.select('td, th')
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    if key and value:
                        specs[key] = value
            detail_info['specifications'] = json.dumps(specs, ensure_ascii=False)
        
        # 提取图片
        img_selectors = ['.main-img img', '.thumb img', '[itemprop="image"]']
        for selector in img_selectors:
            img_elems = soup.select(selector)
            if img_elems:
                for img in img_elems[:5]:  # 只取前5张图片
                    src = img.get('src', '') or img.get('data-src', '')
                    if src:
                        if src.startswith('//'):
                            src = 'https:' + src
                        detail_info['images'].append(src)
                break
        
        # 提取评分
        rating_elem = soup.select_one('.rating, .score, '[itemprop="ratingValue"]')
        if rating_elem:
            detail_info['rating'] = rating_elem.get_text(strip=True)
        
        # 提取评价数量
        review_elem = soup.select_one('.review-count, .comment-count, '[itemprop="reviewCount"]')
        if review_elem:
            review_text = review_elem.get_text(strip=True)
            numbers = re.findall(r'\d+', review_text)
            if numbers:
                detail_info['review_count'] = numbers[0]
        
        # 提取好评率
        positive_elem = soup.select_one('.positive-rate, .good-rate')
        if positive_elem:
            detail_info['positive_rate'] = positive_elem.get_text(strip=True)
        
        # 提取服务评分
        service_elem = soup.select_one('.service-score, '.dsr-score')
        if service_elem:
            detail_info['service_score'] = service_elem.get_text(strip=True)
        
        # 提取物流评分
        logistics_elem = soup.select_one('.logistics-score, '.wl-score')
        if logistics_elem:
            detail_info['logistics_score'] = logistics_elem.get_text(strip=True)
        
        # 提取保修信息
        warranty_elem = soup.select_one('.warranty, '.guarantee')
        if warranty_elem:
            detail_info['warranty'] = warranty_elem.get_text(strip=True)
        
        # 提取配送信息
        delivery_elem = soup.select_one('.delivery, '.shipping')
        if delivery_elem:
            detail_info['delivery'] = delivery_elem.get_text(strip=True)
        
        return detail_info
    
    def save_products(self, products, filename='products.csv'):
        """保存商品数据到CSV"""
        if not products:
            logger.warning("没有商品数据可保存")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = products[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(products)
        
        logger.info(f"商品数据已保存到: {filename} (共 {len(products)} 条记录)")
    
    def save_details(self, details, filename='product_details.csv'):
        """保存商品详情到CSV"""
        if not details:
            logger.warning("没有商品详情可保存")
            return
        
        # 处理嵌套字段
        flat_details = []
        for detail in details:
            flat_detail = detail.copy()
            # 将列表转换为字符串
            if 'images' in flat_detail:
                flat_detail['images'] = ';'.join(flat_detail['images'])
            flat_details.append(flat_detail)
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = flat_details[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flat_details)
        
        logger.info(f"商品详情已保存到: {filename} (共 {len(details)} 条记录)")
    
    def crawl_search_results(self, search_url, max_pages=5):
        """爬取搜索结果页"""
        site_type = self.detect_site(search_url)
        logger.info(f"检测到网站类型: {site_type}")
        
        all_products = []
        current_url = search_url
        
        for page in range(1, max_pages + 1):
            logger.info(f"正在爬取第 {page} 页: {current_url}")
            
            html = self.fetch_page(current_url)
            if not html:
                logger.error(f"无法获取第 {page} 页")
                break
            
            # 解析商品列表
            products = self.parse_product_list(html, current_url, site_type)
            all_products.extend(products)
            
            logger.info(f"第 {page} 页找到 {len(products)} 个商品")
            
            # 查找下一页
            soup = BeautifulSoup(html, 'html.parser')
            config = self.site_configs.get(site_type, {})
            next_selector = config.get('next_page_selector', '.next, .pn-next')
            
            next_elem = soup.select_one(next_selector)
            if next_elem and next_elem.get('href'):
                next_href = next_elem['href']
                if next_href.startswith('//'):
                    next_href = 'https:' + next_href
                elif next_href.startswith('/'):
                    next_href = urljoin(current_url, next_href)
                elif not next_href.startswith('http'):
                    next_href = urljoin(current_url, '/' + next_href)
                
                current_url = next_href
            else:
                logger.info("没有找到下一页，爬取结束")
                break
            
            # 页间延迟
            time.sleep(random.uniform(3, 6))
        
        return all_products
    
    def crawl_product_details(self, product_urls, max_details=20):
        """爬取商品详情"""
        site_type = self.detect_site(product_urls[0]) if product_urls else 'unknown'
        
        all_details = []
        
        for i, url in enumerate(product_urls[:max_details]):
            logger.info(f"正在爬取商品详情 {i+1}/{min(len(product_urls), max_details)}: {url}")
            
            html = self.fetch_page(url)
            if html:
                detail = self.parse_product_detail(html, url, site_type)
                all_details.append(detail)
            
            # 显示进度
            if (i + 1) % 5 == 0:
                logger.info(f"进度: 已处理 {i+1} 个商品详情")
        
        return all_details

# ==================== 使用示例 ====================

def example_crawl_jd_search():
    """爬取京东搜索结果的示例"""
    crawler = EcommerceCrawler()
    
    # 京东手机搜索（示例URL，实际可能需要调整）
    search_url = "https://search.jd.com/Search?keyword=手机&enc=utf-8"
    
    # 爬取搜索结果
    products = crawler.crawl_search_results(search_url, max_pages=3)
    
    if products:
        # 保存商品列表
        crawler.save_products(products, 'jd_phones.csv')
        
        # 爬取部分商品详情
        product_urls = [p['url'] for p in products[:10] if p['url']]
        details = crawler.crawl_product_details(product_urls, max_details=10)
        
        if details:
            crawler.save_details(details, 'jd_phone_details.csv')

def example_price_comparison():
    """价格对比爬虫示例"""
    crawler = EcommerceCrawler()
    
    # 不同平台的搜索关键词
    search_queries = {
        'jd': 'https://search.jd.com/Search?keyword=笔记本电脑&enc=utf-8',
        'taobao': 'https://s.taobao.com/search?q=笔记本电脑',
        'tmall': 'https://list.tmall.com/search_product.htm?q=笔记本电脑'
    }
    
    all_products = []
    
    for site, search_url in search_queries.items():
        logger.info(f"开始爬取 {site}: {search_url}")
        
        products = crawler.crawl_search_results(search_url, max_pages=2)
        for product in products:
            product['platform'] = site
            all_products.append(product)
        
        # 平台间延迟
        time.sleep(10)
    
    # 保存所有平台数据
    if all_products:
        crawler.save_products(all_products, 'laptop_price_comparison.csv')
        
        # 分析价格
        analyze_prices(all_products)

def analyze_prices(products):
    """分析价格数据"""
    if not products:
        return
    
    print("\n" + "="*50)
    print("价格分析报告")
    print("="*50)
    
    # 按平台分组
    platforms = {}
    for product in products:
        platform = product.get('platform', 'unknown')
        if platform not in platforms:
            platforms[platform] = []
        
        try:
            price = float(product.get('price', 0))
            if price > 0:
                platforms[platform].append(price)
        except:
            pass
    
    # 计算统计信息
    for platform, prices in platforms.items():
        if prices:
            avg_price = sum(prices) / len(prices)
            min_price = min(prices)
            max_price = max(prices)
            
            print(f"\n{platform.upper()}平台:")
            print(f"  商品数量: {len(prices)}")
            print(f"  平均价格: ¥{avg_price:.2f}")
            print(f"  最低价格: ¥{min_price:.2f}")
            print(f"  最高价格: ¥{max_price:.2f}")
            print(f"  价格范围: ¥{min_price:.2f} - ¥{max_price:.2f}")

# ==================== 主程序 ====================

if __name__ == "__main__":
    print("电商商品爬虫示例")
    print("=" * 50)
    print("重要提示：")
    print("1. 请遵守电商网站的robots.txt和使用条款")
    print("2. 避免频繁请求，设置合理延迟（3-5秒）")
    print("3. 仅用于学习研究，不得用于商业用途")
    print("4. 实际使用时需要根据网站结构调整选择器")
    print("=" * 50)
    
    # 运行示例
    # example_crawl_jd_search()
    # example_price_comparison()
    
    print("\n使用方法：")
    print("1. 创建EcommerceCrawler实例")
    print("2. 调用crawl_search_results(search_url, max_pages)")
    print("3. 可选：调用crawl_product_details(product_urls, max_details)")
    print("4. 数据将自动保存为CSV文件")
    
    # 简单测试
    crawler = EcommerceCrawler()
    
    # 测试网站检测
    test_urls = [
        "https://www.jd.com",
        "https://www.taobao.com",
        "https://www.tmall.com"
    ]
    
    print("\n网站检测测试：")
    for url in test_urls:
        site_type = crawler.detect_site(url)
        print(f"  {url} -> {site_type}")
    
    print("\n爬虫准备就绪！")