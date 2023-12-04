#!/usr/bin/env python

import image_embedding_indexer
import os
import urllib.parse

iei = image_embedding_indexer.ImageEmbeddingIndexer(device="cuda")

def process_file(f):
    try:
        src_uri = iei.img_helper.file_path_to_file_uri(f)
        img_uri = src_uri
        title = f.encode('unicode_escape').decode('utf-8')
        x = iei.preprocess_img(img_uri, src_uri, title, None, "{}")
        return x
    except Exception as e:
        print(e)


def is_likely_image(file_path):
    image_extensions = [
        "jpg",
        "jpeg",
        "png",
        "gif",
        "bmp",
        "tiff",
        "webp",
        "jfif",
        "tga",
        "tif",
        "heic",
        "raw",
    ]
    pattern = rf'\b\w+\.(?:{"|".join(image_extensions)})$'
    match = re.search(pattern, file_path, re.IGNORECASE)
    return match


import os
import argparse
import re
import glob


def list_files(files, recurse=False, fileformat=None):
    for file in files:
        if recurse:
            file_pattern = os.path.join(
                file, "**", f"*.{fileformat}" if fileformat else "*"
            )
            print(file_pattern)
            for filepath in glob.glob(file_pattern, recursive=True):
                if fileformat is None:
                    if not is_likely_image(filepath):
                        continue
                result = process_file(filepath)
                # filesystems can contain non-utf-8 characters
                # avoid the exception 
                # unicodeEncodeError: 'utf-8' codec can't encode character '\uXXXX' in position YY: surrogates not allowed
                safe_filepath = filepath.encode('unicode_escape').decode('utf-8')
                print(result, safe_filepath)
        else:
            if os.path.exists(file) and (
                fileformat is None or file.endswith(f".{fileformat}")
            ):
                result = process_file(file)
                safe_filepath = file.encode('unicode_escape').decode('utf-8')
                print(result, safe_filepath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage="%(prog)s -r ~/tmp/'*pics*/**/2010-07-23'")
    parser.add_argument("files", nargs="+", help="Files to list")
    parser.add_argument("-r", "--recurse", action="store_true", help="Enable recursion")
    parser.add_argument("--filetype", "-f", help="Filetype filter")
    args = parser.parse_args()
    list_files(args.files, args.recurse, args.filetype)


# iei.make_all_faiss_indexes()
