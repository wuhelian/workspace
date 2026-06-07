#!/usr/bin/env python3
"""
简单实用的Python爬虫示例
爬取网页标题和链接
"""

import requests
from bs4 import BeautifulSoup
import time
import csv

def simple_crawler(url, max_pages=10):
    """
    简单爬虫：爬取网页标题和所有链接
    
    Args:
        url: 起始URL
        max_pages: 最大爬取页面数
    """
    print(f"开始爬取: {url}")
    print("=" * 50)
    
    visited = set()  # 已访问的URL
    to_visit = [url]  # 待访问的URL
    all_data = []  # 收集的数据
    
    page_count = 0
    
    while to_visit and page_count < max_pages:
        current_url = to_visit.pop(0)
        
        if current_url in visited:
            continue
        
        print(f"正在爬取 ({page_count + 1}/{max_pages}): {current_url}")
        
        try:
            # 发送请求
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(current_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 设置编码
            response.encoding = response.apparent_encoding
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取数据
            page_data = {
                'url': current_url,
                'title': '',
                'links_found': 0,
                'crawl_time': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 提取标题
            if soup.title:
                page_data['title'] = soup.title.string.strip()
            
            # 提取所有链接
            links = []
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                
                # 处理相对链接
                if href.startswith('/'):
                    full_url = requests.compat.urljoin(current_url, href)
                elif href.startswith('http'):
                    full_url = href
                else:
                    continue  # 跳过其他类型链接
                
                links.append({
                    'text': a_tag.get_text(strip=True)[:100],  # 限制长度
                    'url': full_url
                })
            
            page_data['links_found'] = len(links)
            all_data.append(page_data)
            
            # 添加新链接到待访问列表
            for link in links[:5]:  # 只添加前5个链接
                link_url = link['url']
                if link_url not in visited and link_url not in to_visit:
                    to_visit.append(link_url)
            
            visited.add(current_url)
            page_count += 1
            
            # 延迟，避免被封
            time.sleep(1)
            
        except Exception as e:
            print(f"  错误: {e}")
            visited.add(current_url)
            continue
    
    # 保存数据
    if all_data:
        save_to_csv(all_data, 'crawled_data.csv')
        print(f"\n爬取完成！共爬取 {page_count} 个页面")
        print(f"数据已保存到: crawled_data.csv")
        
        # 显示统计信息
        show_statistics(all_data)
    else:
        print("\n没有爬取到数据")

def save_to_csv(data, filename):
    """保存数据到CSV文件"""
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['url', 'title', 'links_found', 'crawl_time']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def show_statistics(data):
    """显示统计信息"""
    print("\n" + "=" * 50)
    print("爬取统计信息")
    print("=" * 50)
    
    total_links = sum(item['links_found'] for item in data)
    avg_links = total_links / len(data) if data else 0
    
    print(f"总页面数: {len(data)}")
    print(f"总链接数: {total_links}")
    print(f"平均每个页面链接数: {avg_links:.1f}")
    
    # 显示前5个页面的标题
    print("\n前5个页面标题:")
    for i, item in enumerate(data[:5]):
        title = item['title'] if item['title'] else '(无标题)'
        print(f"  {i+1}. {title[:50]}...")

def crawl_baidu_search(keyword, max_results=10):
    """
    百度搜索爬虫示例
    
    Args:
        keyword: 搜索关键词
        max_results: 最大结果数
    """
    print(f"\n百度搜索爬虫: {keyword}")
    print("=" * 50)
    
    # 构造搜索URL
    search_url = f"https://www.baidu.com/s?wd={keyword}"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        search_results = []
        
        # 提取搜索结果（百度搜索结果的选择器）
        result_divs = soup.select('.result, .c-container')
        
        for i, result in enumerate(result_divs[:max_results]):
            title_elem = result.select_one('h3 a')
            if title_elem:
                result_data = {
                    'rank': i + 1,
                    'title': title_elem.get_text(strip=True),
                    'url': title_elem.get('href', ''),
                    'brief': ''
                }
                
                # 提取摘要
                brief_elem = result.select_one('.c-abstract, .content-right_8Zs40')
                if brief_elem:
                    result_data['brief'] = brief_elem.get_text(strip=True)[:200]
                
                search_results.append(result_data)
        
        # 保存搜索结果
        if search_results:
            with open(f'baidu_{keyword}_results.csv', 'w', newline='', encoding='utf-8-sig') as f:
                fieldnames = ['rank', 'title', 'url', 'brief']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(search_results)
            
            print(f"找到 {len(search_results)} 个搜索结果")
            print(f"数据已保存到: baidu_{keyword}_results.csv")
            
            # 显示结果
            print("\n搜索结果:")
            for result in search_results[:5]:  # 显示前5个
                print(f"  {result['rank']}. {result['title'][:50]}...")
        else:
            print("没有找到搜索结果")
            
    except Exception as e:
        print(f"搜索失败: {e}")

def main():
    """主函数"""
    print("Python爬虫示例")
    print("=" * 50)
    print("选择爬虫类型:")
    print("1. 网站链接爬虫")
    print("2. 百度搜索爬虫")
    print("3. 退出")
    
    choice = input("\n请选择 (1-3): ").strip()
    
    if choice == '1':
        url = input("请输入起始URL (例如: https://www.example.com): ").strip()
        if url:
            if not url.startswith('http'):
                url = 'https://' + url
            simple_crawler(url, max_pages=5)
        else:
            # 使用示例URL
            print("使用示例URL: https://www.python.org")
            simple_crawler("https://www.python.org", max_pages=5)
    
    elif choice == '2':
        keyword = input("请输入搜索关键词: ").strip()
        if keyword:
            crawl_baidu_search(keyword, max_results=10)
        else:
            print("使用示例关键词: Python编程")
            crawl_baidu_search("Python编程", max_results=10)
    
    elif choice == '3':
        print("再见！")
        return
    
    else:
        print("无效选择")

if __name__ == "__main__":
    main()