# utils.py
import sys
import re
import logging

def safe_print(text, logger=None):
    try:
        print(text)
        if logger:
            logger.info(text)
    except UnicodeEncodeError:
        safe_text = text.encode('ascii', errors='ignore').decode('ascii')
        print(f"{safe_text} [Unicode characters removed]")
        if logger:
            logger.info(f"{safe_text} [Unicode characters removed]")

def clean_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)
