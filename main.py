# main.py
from auth import create_session
from scraper import parse_courses, parse_modules_and_items, parse_file_download_link, is_downloadable_file, get_filename_from_url_or_text
from downloader import download_file
from utils import safe_print, clean_filename
from config import load_config
from indexer import index_courses_and_files, load_index_file, save_index_file, check_downloaded_files
import os
import json
import logging
from logger import setup_logging
from tqdm import tqdm

def main():
    logger = setup_logging()
    config = load_config()
    session = create_session()

    # Step 1: Index all courses and files (or load existing index)
    print("Indexing courses...")
    data = index_courses_and_files(session)

    # Count how many files need to be downloaded
    files_to_download = 0
    for course in data["courses"]:
        for module in course["modules"]:
            for file in module["files"]:
                if not file["downloaded"]:
                    files_to_download += 1

    print(f"\nIndexing complete. Found {data['total_courses']} courses, {data['total_files']} files ({data['total_size']/1024/1024:.2f} MB).")

    if files_to_download == 0:
        print("All files are already downloaded. No need to download anything.")
        return

    print(f"{files_to_download} files need to be downloaded.")

    # Check if using static settings for download confirmation
    if not config.get("static_settings", False):
        proceed = input("Do you want to download the missing files? (y/n): ").strip().lower()
        if proceed != 'y':
            print("Download cancelled.")
            return
    else:
        # In static mode, proceed with download if there are files to download
        print("Proceeding with download in static mode...")

    # Step 2: Download files
    print("\nStarting download...")
    with tqdm(total=files_to_download, unit="file", desc="Downloading") as pbar:
        for course in data["courses"]:
            for module in course["modules"]:
                if module["files"]:
                    os.makedirs(os.path.dirname(module["files"][0]["path"]), exist_ok=True)
                for file in module["files"]:
                    if not file["downloaded"] or config.get("always_redownload", False):
                        try:
                            download_file(session, file["url"], file["path"], data["download_log"])
                            file["downloaded"] = True
                            data["download_log"][os.path.abspath(file["path"])] = True
                        except Exception as e:
                            logger.info(f"Error downloading {file['name']}: {e}")
                        pbar.update(1)

    # Save updated data file
    save_index_file(data)
    print("\nDownload complete!")

if __name__ == "__main__":
    main()
