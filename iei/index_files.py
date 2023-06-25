#!/usr/bin/env python

import image_embedding_indexer
import os
import urllib.parse

iei=image_embedding_indexer.ImageEmbeddingIndexer(device='cpu')


def get_file_uri(file_path):
    absolute_path = os.path.abspath(file_path)
    uri = urllib.parse.quote(absolute_path)
    uri = urllib.parse.urljoin('file:', uri)
    return uri

def process_file(f):
    img_uri = get_file_uri(f)
    src_uri = src_uri
    title = f
    x = iei.preprocess_img(img_uri,src_uri,title,None,"{}")

def is_likely_image(file_path):
   image_extensions = [
       'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp',
       'jfif', 'tga', 'tif', 'heic', 'raw',
    ]
   pattern = fr'\b\w+\.(?:{"|".join(image_extensions)})\b'
   match = re.search(pattern, file_path, re.IGNORECASE)
   return match
        

import os
import argparse
import re
import glob

def list_files(files, recurse=False, fileformat=None):
    for file in files:
        if recurse:
            file_pattern = os.path.join(file, '**', f'*.{fileformat}' if fileformat else '*')
            print(file_pattern)
            for filepath in glob.glob(file_pattern, recursive=True):
                if (fileformat is None):
                    if not is_likely_image(filepath):
                        continue
                print(filepath)
                process_file(f)
        else:
            if os.path.exists(file) and (fileformat is None or file.endswith(f".{fileformat}")):
                print(file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        usage="%(prog)s -r -r ~/tmp/'*pics*/**/2010-07-23' 
    )
    parser.add_argument('files', nargs='+', help='Files to list')
    parser.add_argument('-r', '--recurse', action='store_true', help='Enable recursion')
    parser.add_argument('--filetype', '-f', help='Filetype filter')
    args = parser.parse_args()
    list_files(args.files, args.recurse, args.filetype)





#iei.make_all_faiss_indexes()
