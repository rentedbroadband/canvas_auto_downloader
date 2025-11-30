# downloader.py
import os
import requests
from tqdm import tqdm
from config import load_config
import logging

logger = logging.getLogger(__name__)

def download_file(session, url, save_path, download_log):
    config = load_config()
    save_path_abs = os.path.abspath(save_path)

    if save_path_abs in download_log:
        return

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    if os.path.exists(save_path):
        download_log[save_path_abs] = True
        return

    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        with session.get(url, stream=True, headers=headers, timeout=15) as r:
            r.raise_for_status()
            total = int(r.headers.get('content-length', 0))
            with open(save_path, 'wb') as f, tqdm(
                desc=os.path.basename(save_path),
                total=total,
                unit='B',
                unit_scale=True,
                leave=False
            ) as bar:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    bar.update(len(chunk))
            download_log[save_path_abs] = True
    except requests.HTTPError as e:
        if e.response.status_code == 400:
            logger.debug(f"Skipping download (400 error): {os.path.basename(save_path)}")
        else:
            logger.info(f"Error downloading {os.path.basename(save_path)}: {e}")
        raise
    except Exception as e:
        logger.info(f"Error downloading {os.path.basename(save_path)}: {e}")
        raise
