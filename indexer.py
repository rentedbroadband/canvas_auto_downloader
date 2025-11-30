# indexer.py
import os
import json
import requests
from bs4 import BeautifulSoup
from config import load_config
from scraper import parse_courses, parse_modules_and_items, parse_file_download_link, is_downloadable_file, get_filename_from_url_or_text
import logging
from spinner import Spinner
from tqdm import tqdm
import sys

logger = logging.getLogger(__name__)

def load_index_file():
    """Load existing index file if it exists."""
    config = load_config()
    index_file = config["DATA_FILE"]
    if os.path.exists(index_file):
        try:
            with open(index_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.info(f"Failed to load index file: {e}")
    return None

def save_index_file(data):
    """Save the index data to file."""
    config = load_config()
    index_file = config["DATA_FILE"]
    os.makedirs(os.path.dirname(index_file) or '.', exist_ok=True)
    with open(index_file, "w") as f:
        json.dump(data, f, indent=2)

def check_downloaded_files(data):
    """Check which files in the index have already been downloaded."""
    for course in data["courses"]:
        for module in course["modules"]:
            for file in module["files"]:
                if os.path.exists(file["path"]):
                    file["downloaded"] = True
                    data["download_log"][os.path.abspath(file["path"])] = True
    return data

def index_courses_and_files(session):
    """Index all courses, modules, and files, including file sizes."""
    config = load_config()

    # Try to load existing index
    existing_data = load_index_file()
    if existing_data:
        logger.info(f"Loaded existing index with {existing_data['total_courses']} courses and {existing_data['total_files']} files")
        print(f"Found existing index with {existing_data['total_courses']} courses and {existing_data['total_files']} files")

        # Check if using static settings
        if config.get("static_settings", False):
            reindex = config.get("always_reindex", False)
            redownload = config.get("always_redownload", False)
        else:
            # Ask user if they want to re-index
            reindex = input("Do you want to re-index all courses? (y/n): ").strip().lower() == 'y'
            if not reindex:
                redownload = input("Do you want to re-download all files? (y/n): ").strip().lower() == 'y'

        if not reindex:
            # Check which files are already downloaded
            existing_data = check_downloaded_files(existing_data)

            if not redownload:
                # Mark all existing files as downloaded if not re-downloading
                for course in existing_data["courses"]:
                    for module in course["modules"]:
                        for file in module["files"]:
                            if os.path.exists(file["path"]):
                                file["downloaded"] = True
                return existing_data

    data = {"courses": [], "download_log": {}}

    # Step 1: Get courses
    html = session.get(f"{config['BASE_URL']}/courses").text
    courses = parse_courses(html)
    total_courses = len(courses)
    logger.info(f"Indexing {total_courses} courses and files...")

    # Main progress bar
    with tqdm(total=total_courses, unit="course", desc="Indexing courses", position=0, leave=True, file=sys.stdout) as course_pbar:
        for i, course in enumerate(courses, 1):
            course_name = course['name']

            # Spinner for current course
            spinner = Spinner(f"Fetching {course_name}")
            spinner.start()

            course_data = {"name": course_name, "id": course['id'], "modules": []}
            try:
                modules_html = session.get(f"{config['BASE_URL']}/courses/{course['id']}/modules").text
            except requests.HTTPError as e:
                logger.info(f"Failed to fetch modules page: {e}")
                spinner.stop()
                course_pbar.update(1)
                course_pbar.refresh()
                continue
            except Exception as e:
                logger.info(f"Failed to fetch modules page: {e}")
                spinner.stop()
                course_pbar.update(1)
                course_pbar.refresh()
                continue

            spinner.stop()
            modules = parse_modules_and_items(modules_html, course['id'])

            # Print course name with tqdm.write
            tqdm.write(f"  {course_name}")

            # Count total files for this course
            total_files = 0
            for module in modules:
                total_files += len(module['items'])

            # Nested progress bar for files in this course
            with tqdm(total=total_files, unit="file", desc="Files", position=1, leave=False, file=sys.stdout) as file_pbar:
                for module in modules:
                    module_data = {"name": module['name'], "files": []}
                    logger.info(f"Indexing module: {module['name']}")

                    for item in module['items']:
                        try:
                            item_page = session.get(item['url'], allow_redirects=True, stream=True)
                            item_page.raise_for_status()
                            redirected_url, page_html = item_page.url, item_page.text
                        except requests.HTTPError as e:
                            logger.info(f"Failed to fetch module item page: {e}")
                            file_pbar.update(1)
                            continue
                        except Exception as e:
                            logger.info(f"Failed to fetch module item page: {e}")
                            file_pbar.update(1)
                            continue

                        file_name, download_url = parse_file_download_link(page_html, config['BASE_URL'])
                        if file_name and download_url:
                            try:
                                head = session.head(download_url, allow_redirects=True)
                                file_size = int(head.headers.get('content-length', 0))
                                file_data = {
                                    "name": file_name,
                                    "url": download_url,
                                    "size": file_size,
                                    "downloaded": os.path.exists(os.path.join(config['DOWNLOAD_DIR'], course_name, module['name'], file_name)),
                                    "path": os.path.join(config['DOWNLOAD_DIR'], course_name, module['name'], file_name)
                                }
                                module_data["files"].append(file_data)
                                logger.info(f"Found file: {file_name} ({file_size} bytes)")
                            except Exception as e:
                                logger.info(f"Could not get file size for {file_name}: {e}")
                                file_data = {
                                    "name": file_name,
                                    "url": download_url,
                                    "size": 0,
                                    "downloaded": os.path.exists(os.path.join(config['DOWNLOAD_DIR'], course_name, module['name'], file_name)),
                                    "path": os.path.join(config['DOWNLOAD_DIR'], course_name, module['name'], file_name)
                                }
                                module_data["files"].append(file_data)
                        elif "/pages/" in redirected_url:
                            soup = BeautifulSoup(page_html, "html.parser")
                            for a in soup.find_all('a', href=True):
                                href = a['href']
                                text = a.text.strip()
                                if not href or href.startswith('mailto:') or href.startswith('#'):
                                    continue
                                if href.startswith("/"):
                                    full_url = config['BASE_URL'] + href
                                else:
                                    full_url = href
                                if is_downloadable_file(full_url, text):
                                    filename = get_filename_from_url_or_text(full_url, text)
                                    try:
                                        head = session.head(full_url, allow_redirects=True)
                                        file_size = int(head.headers.get('content-length', 0))
                                        file_data = {
                                            "name": filename,
                                            "url": full_url,
                                            "size": file_size,
                                            "downloaded": os.path.exists(os.path.join(config['DOWNLOAD_DIR'], course_name, module['name'], filename)),
                                            "path": os.path.join(config['DOWNLOAD_DIR'], course_name, module['name'], filename)
                                        }
                                        module_data["files"].append(file_data)
                                        logger.info(f"Found linked file: {filename} ({file_size} bytes)")
                                    except Exception as e:
                                        logger.info(f"Could not get file size for {filename}: {e}")
                                        file_data = {
                                            "name": filename,
                                            "url": full_url,
                                            "size": 0,
                                            "downloaded": os.path.exists(os.path.join(config['DOWNLOAD_DIR'], course_name, module['name'], filename)),
                                            "path": os.path.join(config['DOWNLOAD_DIR'], course_name, module['name'], filename)
                                        }
                                        module_data["files"].append(file_data)
                        file_pbar.update(1)
                    course_data["modules"].append(module_data)

            course_data["total_modules"] = len(course_data["modules"])
            course_data["total_files"] = sum(len(m["files"]) for m in course_data["modules"])
            course_data["total_size"] = sum(f["size"] for m in course_data["modules"] for f in m["files"])
            data["courses"].append(course_data)
            course_pbar.update(1)
            course_pbar.refresh()

    data["total_courses"] = len(data["courses"])
    data["total_files"] = sum(c["total_files"] for c in data["courses"])
    data["total_size"] = sum(c["total_size"] for c in data["courses"])

    # Save the index file
    save_index_file(data)
    return data
