# scraper.py
from bs4 import BeautifulSoup
import re
import html
import html2text
import os
from config import load_config
from download_log import is_already_downloaded, add_to_download_log
from downloader import download_file

def parse_courses(html):
    soup = BeautifulSoup(html, "html.parser")
    courses = []
    for row in soup.select('tr.course-list-table-row'):
        name_el = row.select_one('.course-list-course-title-column .name')
        id_el = row.select_one('.course-list-star-column [data-course-id]')
        if name_el and id_el:
            course_name = name_el.text.strip()
            course_id = id_el['data-course-id']
            courses.append({'name': course_name, 'id': course_id})
    return courses

def parse_modules_and_items(html, course_id):
    config = load_config()
    soup = BeautifulSoup(html, "html.parser")
    modules = []
    for module_div in soup.select("div.item-group-condensed.context_module"):
        module_name_el = module_div.select_one("span.name")
        module_name = module_name_el.text.strip() if module_name_el else "UnknownModule"
        module_name = re.sub(r'[\\/*?:"<>|]', "", module_name)
        items = []
        for li in module_div.select("li.context_module_item"):
            link = li.select_one("a.item_link")
            if not link: continue
            item_title = link.text.strip()
            item_href = link.get("href")
            item_url = config["BASE_URL"] + item_href
            items.append({'title': item_title, 'url': item_url})
        modules.append({'name': module_name, 'items': items})
    return modules

def parse_file_download_link(file_page_html, base_url):
    """Parse a Canvas file page to find the download link."""
    soup = BeautifulSoup(file_page_html, "html.parser")
    a = soup.find('a', attrs={'download': 'true'})
    if a and '/download?download_frd=1' in a['href']:
        file_url = a['href']
        file_name = a.text.strip()
        if file_url.startswith("/"):
            file_url = base_url + file_url
        if file_name.lower().startswith("download "):
            file_name = file_name[8:]
        file_name = file_name.strip()
        return file_name, file_url
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.text.strip()
        if not href or href.startswith('#') or href.startswith('mailto:'):
            continue
        if href.startswith("/"):
            full_url = base_url + href
        else:
            full_url = href
        if is_downloadable_file(full_url, text):
            filename = get_filename_from_url_or_text(full_url, text)
            return filename, full_url
    return None, None

def is_downloadable_file(url, text):
    """Check if a URL likely points to a downloadable file."""
    downloadable_extensions = {
        '.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx',
        '.zip', '.rar', '.7z', '.tar', '.gz',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg',
        '.mp3', '.mp4', '.avi', '.mov', '.wav',
        '.txt', '.csv', '.json', '.xml', '.html', '.css', '.js',
        '.py', '.java', '.cpp', '.c', '.h',
        '.sql', '.db', '.sqlite', '.rtf', '.odt', '.ods', '.odp'
    }
    url_lower = url.lower()
    for ext in downloadable_extensions:
        if url_lower.endswith(ext) or f'{ext}?' in url_lower or f'{ext}#' in url_lower:
            return True
    canvas_file_patterns = [
        r'/courses/\d+/files/\d+',
        r'/files/\d+',
        r'/download\?download_frd=1',
        r'/courses/\d+/file_contents/',
        r'/users/\d+/files/\d+',
        r'instructure\.com.*files',
    ]
    for pattern in canvas_file_patterns:
        if re.search(pattern, url):
            return True
    file_indicators = ['download', 'attachment', 'file', '.pdf', '.doc', '.ppt', '.xls',
                      'handout', 'worksheet', 'assignment', 'syllabus', 'slides']
    text_lower = text.lower()
    for indicator in file_indicators:
        if indicator in text_lower:
            return True
    non_file_indicators = ['http://www.', 'https://www.', 'wiki', 'page', 'module',
                          'discussion', 'assignment submission', 'grade', 'course']
    for indicator in non_file_indicators:
        if indicator in text_lower and not any(ext in url_lower for ext in downloadable_extensions):
            return False
    return False

def get_filename_from_url_or_text(url, text):
    """Extract filename from URL or fallback to link text."""
    if '?' in url:
        url_path = url.split('?')[0]
    else:
        url_path = url
    filename = os.path.basename(url_path)
    if not filename or filename.isdigit() or not '.' in filename:
        filename = text.strip()
        if filename.lower().startswith("download "):
            filename = filename[9:]
        if not '.' in filename and '.' in url_path:
            url_parts = url_path.split('.')
            if len(url_parts) > 1:
                ext = '.' + url_parts[-1]
                if len(ext) <= 5:
                    filename += ext
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    return filename if filename else "downloaded_file"

def parse_canvas_page_content_and_downloads(page_html, download_dir, session, base_url, log):
    """Parse a Canvas page for downloadable links and save as markdown."""
    import os
    from download_log import is_already_downloaded, add_to_download_log
    from downloader import download_file
    body_match = re.search(r'"body":"((?:[^"\\]|\\.)*)"', page_html)
    if not body_match:
        print("          Warning: Could not find WIKI_PAGE body in page HTML.")
        return None
    body_html = body_match.group(1)
    body_html = body_html.encode('utf-8').decode('unicode_escape')
    body_html = html.unescape(body_html)
    soup = BeautifulSoup(body_html, "html.parser")
    download_links = []
    all_links_count = 0
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.text.strip()
        all_links_count += 1
        if not href or href.startswith('mailto:') or href.startswith('#'):
            continue
        if href.startswith("/"):
            full_url = base_url + href
        else:
            full_url = href
        if is_downloadable_file(full_url, text):
            filename = get_filename_from_url_or_text(full_url, text)
            print(f"          Found downloadable link: {text[:50]}... -> {full_url}")
            download_links.append({
                'name': filename,
                'url': full_url,
                'a_tag': a,
                'original_href': href
            })
    print(f"          Found {len(download_links)} downloadable links out of {all_links_count} total links")
    for link in download_links:
        local_path = os.path.join(download_dir, link['name'])
        try:
            print(f"          Downloading linked file: {link['name']}")
            download_file(session, link['url'], local_path, log)
            link['a_tag']['href'] = link['name']
        except Exception as e:
            print(f"          Error downloading linked file {link['name']}: {e}")
    html_content = str(soup)
    markdown_content = html2text.html2text(html_content)
    return markdown_content
