#!/usr/bin/env python
# coding: utf-8

# # Image Functions
# 
# * Schema design
# 
#   * img_metadata - has properties about uri, sources
#   
#     * img_uri -> metadata_id
#     * metadata_id -> img_uri
#     
#   * img_data     - properties of the image itself
#   * kv pairs - img_id -> blob
#     * img_id -> clip_embedding
#     * img_id -> insightface_results
#     * img_id -> thumbnail
#   * faiss_indexes
# 
# Consider:
# 
#     * https://stackoverflow.com/questions/18621513/python-insert-numpy-array-into-sqlite3-database
#     * http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
# 
# Useful methods:
# 
#     * iei.process_image(url, metadata)
#         * gets the image_id from the metadata table
#         * if it didn't exist, create it.
#         * check if all of the clip, thm, and face pieces already existed.
#         *
#         * If not, fetch the image itself
#         * get or create clip embedding 
#         * get or create thumbnail
#         * get or create insightface embedding
# 
#     * iei.rebuild_faiss_indexes()
#     * iei.rebuild_clip_indexes()
#     * 
#     * iei.get_thm(img_id)
#         
#     

# In[320]:
if check_imports := False:
    try:
        import torchvision, open_clip, transformers, autofaiss, insightface, onnxruntime
        import insightface
    except:
        print("you might want to")
        print("pip install torchvision open_clip_torch transformers autofaiss insightface onnxruntime")


# get_ipython().run_line_magic('pip', 'install torchvision open_clip_torch transformers autofaiss insightface onnxruntime >& /tmp/pip.out')


# In[321]:


# my_index = faiss.read_index("knn.index")

# query_vector = np.float32(np.random.rand(1, 100))
# k = 5
# distances, indices = my_index.search(query_vector, k)

# print(f"Top {k} elements in the dataset for max inner product search:")
# for i, (dist, indice) in enumerate(zip(distances[0], indices[0])):
#   print(f"{i+1}: Vector number {indice:4} with distance {dist}")

from PIL import Image,ImageOps
from contextlib import closing
from typing import Generator

import autofaiss
import base64
import dataclasses
import datetime
import email
import email.utils
import faiss
import functools
import glob
import hashlib
import io
import json
import numpy as np
import open_clip
import os
import pickle
import pyarrow
import re
import requests
import sqlite3
import time
import torch
import zlib
import typing


# Python3.9 compatibility
from typing import Optional, Union
# end of Python3.9 compatibility

# Avoid the error
# OSError: image file is truncated (45 bytes not processed)
# from some buggy jpeg encoders
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True


# In[322]:

@dataclasses.dataclass
class ImgData():
    img_id   :Union[int, None]    # int|None   # when we don't need python3.9 anymore
    sha224   :str
    width    :int
    height   :int
    bytesize :int
    dttm     :datetime.datetime
    mimetype :str
    
@dataclasses.dataclass
class ImgMetadata():
    meta_id  :Union[int, None]    # int|None   # when we don't need python3.9 anymore
    img_uri  :str
    src_uri  :str
    title    :str
    subtitle :str
    metadata :str
    dttm     :datetime.datetime
    img_id   :int


# In[323]:
from typing import Union, List
NumericType = Union[float, int]
NestedNumericList = list[Union[NumericType, list[NumericType]]]

class VectorHelper:

    @staticmethod
    def cast_to_float32_array(data: Union[np.ndarray, torch.Tensor, NestedNumericList]) -> np.ndarray:
        """                    
            # Example inputs
            tensor = torch.tensor([[1, 2], [3, 4]])
            array = np.array([[5, 6], [7, 8]])
            nested_list:NestedNumericList = [[9, 10], [11, 12]]

            # Casting to float32 arrays
            vh = VectorHelper()
            result_tensor = vh.cast_to_float32_array(tensor)
            result_array = vh.cast_to_float32_array(array)
            result_list = vh.cast_to_float32_array(nested_list)

            print(result_tensor.dtype)  # Output: float32
            print(result_array.dtype)   # Output: float32
            print(result_list.dtype)    # Output: float32
        """
        if isinstance(data,torch.Tensor):
            return data.numpy().astype(np.float32)
        if isinstance(data,list):
            return np.array(data).astype(np.float32)
        if isinstance(data,np.ndarray):
            return data.astype(np.float32)
        raise ValueError("Invalid data type. Expected PyTorch tensor, NumPy array, or nested Python list of numbers.")

    @staticmethod
    def int8_phase_vec(v):
        rv = VectorHelper.cast_to_float32_array(v)
        nrv = rv / np.sqrt(rv @ rv.T)
        maxabs = max(max(nrv),-min(nrv))
        n2 = (nrv * 127 / maxabs).astype(np.int32)
        return n2

    @staticmethod
    def normalize(v):
        n = np.linalg.norm(v,axis=-1,keepdims=True) + np.finfo(v.dtype).eps
        return v/n
    
    @staticmethod
    def recenter_vectors(embs:np.ndarray):
        unit_vecs  = VectorHelper.normalize(embs)
        median_vec = np.median(unit_vecs,axis=0)
        recentered = unit_vecs - median_vec
        final_vecs = VectorHelper.normalize(recentered)
        return final_vecs
    
    @staticmethod
    def slerp(a:np.ndarray, b:np.ndarray, t: float) -> np.ndarray:
        """
        https://en.wikipedia.org/wiki/Slerp
        """
        au = a/np.linalg.norm(a)
        bu = b/np.linalg.norm(b)
        adotb = np.dot(au,bu)
        omega = np.arccos(adotb)
        print(f"in slerp, vectors and b were {180/3.1416*omega}° apart")
        somega = np.sin(omega)
        if somega == 0:
            return (au * (1-t) + bu * t)
        s = (np.sin((1-t)*omega) * au + np.sin(t*omega)*bu) / somega
        return s



#os.environ['CUDA_VISIBLE_DEVICES'] = '0'
#os.environ['CUDA_VISIBLE_DEVICES'] = ''
import torchvision.transforms.transforms
class OpenClipWrapper:
    def __init__(self,model_name='ViT-B-32-quickgelu',pretrained='laion400m_e32',device='cpu'):
        """
            Try open_clip.list_pretrained() to see the list of models.
            This cheap GPU can only handle batches of ~10 images with laion400m_e32
            but it seems quite fast.
            * On CPU - 10 embeddings = 698 ms 
            * On GPU - 10 embeddings =  13 ms 
        """
        self.model_name = model_name
        self.pretrained = pretrained
        self.device = device
        m,c,p = open_clip.create_model_and_transforms(model_name, 
                                                      pretrained=pretrained,
                                                      device=device
                                                     )
        self.model, self.compose, self.preprocess = m,c,p
        self.tokenize = open_clip.get_tokenizer(self.model_name)
            
    def get_pretrained_models(self):
        return open_clip.list_pretrained()
    
    def img_embeddings(self,imgs):
        with torch.no_grad(): # torch.autocast():
            #print("type of preprocess is ",type(self.preprocess))
            #torchvision.transforms.transforms.Compose
            preprocessed_list = [self.preprocess(i) for i in imgs] # type: ignore
            preprocessed = torch.stack(preprocessed_list).to(self.device) # type: ignore
            features = self.model.encode_image(preprocessed) # type: ignore
            features /= features.norm(dim=-1, keepdim=True)
            return features
    
    def txt_embeddings(self,txts):
        with torch.no_grad():# , torch.cuda.amp.autocast():# type: ignore
            tokenized = self.tokenize(txts).to(self.device)
            features = self.model.encode_text(tokenized) # type: ignore
            features /= features.norm(dim=-1, keepdim=True)
            return features

import torchvision.transforms.transforms
if include_openai_clip := True:
    import clip
    class OpenAIWrapper:

        def __init__(self,model_name="ViT-B/32",device='cpu'):
            """
            OpenAI's CLIP takes fewer parameters than LAION's openclip
            """
            self.model_name = model_name
            self.device = device
            m,p = clip.load(model_name, device=device)
            self.model, self.preprocess = m,p
                
        def get_pretrained_models(self):
            return clip.available_models()
        
        def img_embeddings(self,imgs):
            with torch.no_grad(): # torch.autocast():
                #print("type of preprocess is ",type(self.preprocess))
                #torchvision.transforms.transforms.Compose
                preprocessed_list = [self.preprocess(i) for i in imgs] # type: ignore
                preprocessed = torch.stack(preprocessed_list).to(self.device) # type: ignore
                features = self.model.encode_image(preprocessed) # type: ignore
                features /= features.norm(dim=-1, keepdim=True)
                return features
        
        def txt_embeddings(self,txts):
            with torch.no_grad():# , torch.cuda.amp.autocast():# type: ignore
                tokenized = clip.tokenize(txts).to(self.device)
                features = self.model.encode_text(tokenized) # type: ignore
                features /= features.norm(dim=-1, keepdim=True)
                return features

# In[324]:

import insightface.app
from insightface.app import FaceAnalysis
from PIL import Image
from PIL import ImageDraw
import numpy as np
import random

# 1.5 seconds without excluding landmarks; 0.4 seconds excluding them for an image with 8 faces.
class InsightFaceWrapper:
    
    def __init__(self,exclude=['landmark_3d_68', 'landmark_2d_106', 'genderage' ]):
        self.app = FaceAnalysis(ctx_id=0, providers=['CUDAExecutionProvider','CPUExecutionProvider'])
        self.app.prepare(ctx_id=0, det_size=(640,640))
        for m in exclude or []:
            del(self.app.models[m])
            
    def analyze(self,img:Image.Image, max_num=0):
        img_np = np.asarray(img.convert('RGB'))
        res = self.app.get(img_np,max_num)
        return res
    
    def highlight_faces(self,img:Image.Image, res:list[dict]):
        draw = ImageDraw.Draw(img)
        for pic in res[0:10]:
            clr = random.sample([255,random.randint(0,255),0],3)
            clr_t = typing.cast(tuple[int,int,int],clr)
            for p in pic.get('landmark_2d_106',[]):
                pts:list[float] = [c-1 for c in p] + [c+1 for c in p]
                pts_t = typing.cast(tuple[float,float,float,float],pts)
                draw.rectangle(pts_t,outline=clr_t,width=2)
            draw.rectangle(pic['bbox'],outline=clr_t,width=5)
        return img


# In[ ]:


import filelock
import collections
import collections.abc
#collections.abc.MutableMapping
class SimpleSqliteKVStore(collections.abc.MutableMapping):
    """
        A simple disk-backed KV store.

        Lighter weight than `import sqlitedict`.
        This entire index can be reconstructed from source data, so disable
        synchronous for orders of magnitude faster on spinning hard disks.
    """
    def __init__(self,imgidx_path,synchronous='OFF'):
        self.imgidx_path = imgidx_path
        self.lock = filelock.FileLock(imgidx_path + '.lock',timeout=10)
        self.db_conn = sqlite3.connect(imgidx_path)
        create_kv_sql = "CREATE TABLE IF NOT EXISTS kv (k INTEGER PRIMARY KEY, v BLOB);"
        self.db_conn.execute(create_kv_sql)
        self.db_conn.commit()
        # can be fully reconstructed from source data. No need to keep.
        pragma_sql = f"PRAGMA synchronous = {synchronous};"
        self.db_conn.execute(pragma_sql)
        self.db_conn.commit()
        
    def __getitem__(self,k):
        with self.lock:
            sql = "select v from kv where k = ?"
            for row in self.db_conn.execute(sql,[k]):
                return row[0]
        
    def __setitem__(self,k,v):
        with self.lock:
            sql = "insert into kv (k,v) values (?,?) on conflict(k) do update set v=excluded.v"
            sql = "insert into kv (k,v) values (?,?)" # good for debugging
            self.db_conn.execute(sql,[k,v])
            self.db_conn.commit()
            
    def setitems(self,ks:list,vs:list):
        with self.lock:
            sql = "insert into kv (k,v) values (?,?) on conflict(k) do update set v=excluded.v"
            sql = "insert into kv (k,v) values (?,?)" # good for debugging
            for k,v in zip(ks,vs):
                self.db_conn.execute(sql,[k,v])
            self.db_conn.commit()
            
    def __iter__(self):
        with self.lock:
            sql = "select k from kv"
            for row in self.db_conn.execute(sql):
                yield(row[0])
                
    def iter_with_values(self):
        with self.lock:
            sql = "select k,v from kv"
            for row in self.db_conn.execute(sql):
                yield(row)
                
    def __delitem__(self,k):
        with self.lock:
            sql = "delete from kv where k = ?"
            self.db_conn.execute(sql,[k])
            self.db_conn.commit()
            
    def __len__(self):
        with self.lock:
            sql = "select count(*) from kv"
            for row in self.db_conn.execute(sql):
                return(row[0])
            
    def commit(self):
        self.db_conn.commit()
            
# s = SimpleSqliteKVStore('/tmp/1')
# s.get(1,'hi')
# s[1]=b'3'
# s.get(2,'hi')
# s[4]


# In[326]:


from dataclasses import dataclass
from typing import List

class FaissHelper:

    @dataclass
    class SearchResult:
        scores: list[float]
        imgids: list[int]

    def __init__(self,prefix:str):
        self.index_path = f"{prefix}.faiss"
        self.id_path    = f"{self.index_path}.id_lookup.txt.gz"
        print("FaissHelper",self.index_path, self.id_path)
        if os.path.exists(self.index_path) and os.path.exists(self.id_path):
            self.load()

    def load(self):
        self.faiss_index = faiss.read_index(self.index_path)
        self.id_lookup = np.loadtxt(self.id_path,np.int64)
        # with open(f"{self.index_path}.id_lookup.json") as f:
        #     self.id_lookup = json.loads(f.read())
            
    def search_without_index(self,targets,ids,embs,k=10):
        results = []
        for target in targets:
            unsorted_scores = (np.stack(embs) @ target.T)#[:,0]
            result_pairs= sorted(zip(unsorted_scores,ids),key=lambda x:-x[0])[0:k]
            scores = [rp[0] for rp in result_pairs]
            imgids = [rp[1] for rp in result_pairs]
            result = FaissHelper.SearchResult(scores=scores,imgids = imgids)
            results.append(result)
        return results
    
    def search(self,target,k=10) -> list['FaissHelper.SearchResult']:
        idl = self.id_lookup
        if idl.shape == ():
            idl = idl.reshape((1))
        dsts, idxs = self.faiss_index.search(target, k)
        print("############33 type of idxs is",type(idxs))
        results = []
        for drow,irow in zip(dsts,idxs):
            scores = [float(d) for d in drow]
            imgids = [idl[i] for i in irow]
            result = FaissHelper.SearchResult(scores=scores,imgids = imgids) # type: ignore
            results.append(result)
        return results
        
    def normalize(self,v):
        n = np.linalg.norm(v,axis=-1,keepdims=True) + np.finfo(v.dtype).eps
        return v/n

    def create_index(self,ids,embs):
        embeddings    = np.stack(embs)

        ## makes "zebra -horse +fish" nicer
        ## but we really need to apply it to text embeddings too
        #embeddings    = VectorHelper.recenter_vectors(embeddings)

        index, index_infos = autofaiss.build_index(
                      embeddings=embeddings,
                      index_path=self.index_path,
                      index_infos_path=f"{self.index_path}.infos",
                      max_index_query_time_ms = 500,
                      min_nearest_neighbors_to_retrieve = 1000,
                      max_index_memory_usage = "3G",
                      current_memory_available = "4G",
                      should_be_memory_mappable = True,
                      metric_type="ip"
                     )
        img_id_np = np.array(ids,dtype=np.int32)
        np.savetxt(self.id_path, img_id_np, fmt='%d')

        print(f"image_id_path should be at {self.id_path}")
        self.load()
        return index_infos
        ####  other id lookup alternatives
        # with open(f"{self.index_path}.id_lookup.json","w") as f:
        #    f.write(json.dumps(img_id_lookup,indent=1))
        # pa_ids = pyarrow.array(img_id_lookup)
        # pat = pyarrow.table([pa_ids],names=["img_id"])
        # pyarrow.parquet.write_table(pat, f"{self.index_path}.id_lookup.parquet")
        # with open(f"{self.index_path}.id_lookup.npy", 'wb') as f:
        #     np.save(f, img_id_np)


# In[327]:


# In[328]:


# Fix incorrect mime types for NIKON cameras
# https://github.com/agschwender/pilbox/issues/34
from PIL import JpegImagePlugin
JpegImagePlugin._getmp = lambda x: None # type: ignore

import urllib.parse
class ImgHelper:

    def __init__(self,throttle_max_rate=0.0):
        self.throttle_max_rate = throttle_max_rate
        self.t0 = 0
        
    # filenames returned by glob.glob() can have non-utf-8 characters.
    # ('/tmp/test_file\udca330result.txt')
    def file_path_to_file_uri(self,filename):
        file_uri = 'file://' + urllib.parse.quote_from_bytes(os.fsencode(filename))
        return file_uri

    def file_uri_to_file_path(self,file_uri):
        parsed_uri = urllib.parse.urlparse(file_uri)
        if not parsed_uri.scheme == "file":
            raise ValueError(f"Not a file URI: {file_uri}")
        file_path_bytes = urllib.parse.unquote_to_bytes(file_uri[7:])
        file_path = os.fsdecode(file_path_bytes)
        if parsed_uri.netloc != "":
            # Handle Windows paths with network location (e.g., file://hostname/path)
            file_path = "//" + parsed_uri.netloc + file_path
        return file_path
        
    def wait_for_throttle(self):
        t1 = time.time()
        if t1 < self.throttle_max_rate + self.t0:
            print(f"throttling beacause {self.throttle_max_rate + self.t0 - t1} > 0")
            time.sleep(self.throttle_max_rate + self.t0 - t1)
        #else:
        #    print(f"not throttling beacause {self.throttle_max_rate + self.t0 - t1} < 0")
        t1 = time.time()
        self.t0 = t1
            

    def fetch_img(self,uri,headers=None) -> tuple[Image.Image,ImgData,datetime.datetime,bytes]:

        #print("will fetch:",uri)
        self.wait_for_throttle()

        if not headers and  re.match(r'^https?:',uri):
            headers = {'User-agent': 
                      "Clip Embedding Calculator/0.01 (https://github.com/ramayer/wikipedia_in_spark; ) generic-library/0.0"}
        
        if re.match(r'^https?:',uri):
            resp = requests.get(uri,headers=headers)
            mtime_h = resp.headers.get('Last-Modified')
            mtime  = email.utils.parsedate_to_datetime(mtime_h) if mtime_h else None
            img_bytes = resp.content
        elif re.match(r'^file://',uri):
            filepath = self.file_uri_to_file_path(uri)
            #print("reading ",filepath)
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(filepath),
                                                    tz=datetime.timezone.utc)
            with open(filepath,"rb") as f:
                img_bytes = f.read()
        elif os.path.exists(uri):
            filepath = uri
            print("reading ",filepath)
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(filepath),
                                                    tz=datetime.timezone.utc)
            with open(filepath,"rb") as f:
                img_bytes = f.read()
        else:
            raise ValueError(f"can't figure out how to get {uri}")
        
        if not mtime:
            mtime = datetime.datetime.now()
        bytesize = len(img_bytes)
        img      = Image.open(io.BytesIO(img_bytes))
        mimetype = img.get_format_mimetype() # type: ignore
        sha224   = base64.b85encode(hashlib.sha224(img_bytes).digest()).decode('utf-8')
        # get the size it'l be seen on the screen
        w,h      = ImageOps.exif_transpose(img).size
        img_data = ImgData(None,sha224,w,h,bytesize,mtime,mimetype)
        return (img, img_data, mtime,img_bytes)

    def convert_I_to_L(self,img:Image.Image):
        """
        See https://github.com/OCR-D/core/pull/627
        https://github.com/python-pillow/Pillow/issues/452
        https://github.com/python-pillow/Pillow/pull/3838#discussion_r292114051
        https://github.com/python-pillow/Pillow/pull/3838

        and test on

        https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Quaternionsche_Mandelbrotmenge_20190830_zbuffer.png/800px-Quaternionsche_Mandelbrotmenge_20190830_zbuffer.png

        which shows many artifacts if you don't /300.

        """
        array = np.uint8(np.array(img) / 300)
        return Image.fromarray(array)
    
    def make_thm(self,img:Image.Image,max_w=2048,max_h=2048) -> Image.Image:
        # TODO - consider if it needs: 
        #  - yes, it does need it.
        max_w        = max_w or 2048
        max_h        = max_h or 2048
        t_img        = ImageOps.exif_transpose(img)
        img_w,img_h  = t_img.size
        wscale       = max_w / img_w
        hscale       = max_h / img_h
        scale        = min([1,wscale,hscale])
        t_w          = round(img_w * scale)
        t_h          = round(img_h * scale)
        return t_img.resize((t_w,t_h), Image.Resampling.LANCZOS)
    
        #import torchvision.transforms.functional as F
        #i2 = img.convert("RGBA")
        #return ImageOps.pad(i2,(w,h),Image.Resampling.LANCZOS,color=(127,127,127,0))
    
    def make_5_tiles(self,img:Image.Image):
        """
        Useful for indexing multiple tiles for different parts of an image.
        """
        width, height = img.size
        mid_x = width // 2
        mid_y = height // 2
        q1 = img.crop((0, 0, mid_x, mid_y))
        q2 = img.crop((mid_x, 0, width, mid_y))
        q3 = img.crop((0, mid_y, mid_x, height))
        q4 = img.crop((mid_x, mid_y, width, height))
        return [img,q1,q2,q3,q4]

    def img_bytes(self,img,quality=85):
        buf = io.BytesIO()
        img.save(buf,format="WebP",quality=quality)
        return buf.getvalue()
    
    def bytes_to_data_url(self,b: bytes) -> str:
        e = base64.b64encode(b).decode('utf-8')
        return f'data:image/jpg;base64,{e}'
    
    def get_data_url(self,url: str,headers=None) -> Union[str, None]: # str|None:  # python3.9 hack
        try:
            i,d,m,b = self.fetch_img(url,headers=headers)
            #t = self.make_thm(i)
            #b = self.img_bytes(t)
            u = self.bytes_to_data_url(b)
            return u
        except Exception as e:
            print(f"{e} for {url}")
            return None
        
    def crop_by_pct(self,image:Image.Image, 
                         x_pct, y_pct, width_pct, height_pct):
       
        img_width, img_height = image.size

        x_pixel = int(x_pct * img_width / 100)
        y_pixel = int(y_pct * img_height / 100)
        width_pixel = int(width_pct * img_width / 100)
        height_pixel = int(height_pct * img_height / 100)

        cropped_image = image.crop((x_pixel, y_pixel, x_pixel + width_pixel, y_pixel + height_pixel))

        return cropped_image

        

#####################################################################################
# Query Parser
#####################################################################################


import pyparsing as pp
import functools
import numpy as np
import toml

class ParserHelper:
    """Support complex queries like
       skiing +summer -winter -(winter sports) +(summer sports) +{img:1234} +https://example.com/img.jpg
    
    
       * TODO 
          Consider if adding and subtracting vectors is really what we want here.
    
          Perhaps we should think more in terms of rotating in the direction of a different term.
          See also:
              https://www.inference.vc/high-dimensional-gaussian-distributions-are-soap-bubble/
    
              "If you want to interpolate between two random
              without leaving the soap bubble you should instead
              interpolate in in polar coordinates ... For a more
              robust spherical interpolation scheme you might want
              to opt for something like SLERP."
    
         Some syntax for "start a zerbra, and rotate 20 dgegrees
         in the direction of horse" might be interesting.
    
    """

    def __init__(self,iei:'ImageEmbeddingIndexer',use_openai_clip):
        self.use_openai_clip = use_openai_clip
        self.iei = iei

    @functools.cached_property
    def parser(self) -> pp.ParserElement:
        ppu = pp.unicode
        greek_word = pp.Word(ppu.Greek.alphas)

        # using pre-release pyparsing==3.0.0rc1 , so I don't need to change APIs later
        sign = pp.Opt(
            pp.Group(pp.one_of("+ -") + pp.Opt(pp.pyparsing_common.fnumber.copy(), 1)),
            ["+", 1],
        )
        # word  = pp.Word(pp.alphanums,exclude_chars='([{}])') # fails on hyphenated words
        # word  = pp.Word(pp.alphanums,pp.printables,exclude_chars='([{}])') # fails on unicode
        # word = pp.Word(
        #    pp.unicode.alphanums, pp.unicode.printables, exclude_chars="({})"
        # )  # slow
        ## pp.Word really doesn't like search tems like '🐱 🐈'
        ## Trying a regex instead
        word = pp.Regex(r'[^-+ ]+')
        words = pp.OneOrMore(word)
        enclosed = pp.Forward()
        quoted_string = pp.QuotedString('"')
        nested_parens = pp.nestedExpr("(", ")", content=enclosed)
        nested_braces = pp.nestedExpr("{", "}", content=enclosed)

        ## If we want to support nested embedding math, something like this would be promising
        #
        # enclosed << pp.OneOrMore(
        #     (
        #         pp.Regex(r"[^{(\[\])}]+")
        #         | nested_parens
        #         | nested_brackets
        #         | nested_braces
        #         | quoted_string
        #     )
        # )
        expr = sign + pp.original_text_for(
            (quoted_string | nested_parens | nested_braces | words)
        )
        return expr

    def parse_structured_term(self,t):
        """
           allow json or toml clauses in searches like the json expressions
              {"image_id":28754} -{"image_id":174054}
           from v1, or the toml expression
              {clip=1234}
           for v2
        """
        status = {}
        try:
           return json.loads(t)
        except json.JSONDecodeError as e1:
            status['json_error'] = e1
            pass
        try:
            return toml.loads(t)
        except toml.TomlDecodeError as e2:
            status['toml_error'] = e2
            pass
        print(status)
        return None

    def get_query_vectors(self,q):
        iei = self.iei
        parsed = self.parser.search_string(q)
        parsed.pprint()
        
        embeddings={
            'clip':[],
            'clip_scale_factors':[],
            'face':[],
            'text':[],
        }

        if self.use_openai_clip:
            clipmeth = iei.get_openai_clip_embedding
            clipwrap = iei.oiw
        else:
            clipmeth = iei.get_laion_clip_embedding
            clipwrap = iei.ocw
        
        for (operator,magnitude),term in parsed:
            print(term)
            scale_factor = magnitude * float(operator+'1')
            #print(operator,magnitude,term, " => ", scale_factor)
        
            if len(term)>2 and term[0] == '(' and term[-1] == ')': 
                term=term[1:-1]
        
            if term.startswith('{'): # v1 img
                d = self.parse_structured_term(term)
                if d and d.get('img'):
                    e = clipmeth(d['img'])
                    #e = e * scale_factor
                    embeddings['clip'].append(e)
                    embeddings['clip_scale_factors'].append(scale_factor)
                continue
        
            if fids := re.findall(r"^face:((\d+)\.?(\d*))", term):
                for _, img_id, idx in fids:
                    ia = iei.get_insightface_analysis(img_id)
                    if idx and ia:
                        row = ia[int(idx)]
                        embeddings['face'].append(row["embedding"])
                        print(f"found one {img_id}.{idx}")
                    elif ia:
                        print(f"getting {len(ia)} for {img_id}")
                        for row in ia:
                            embeddings['face'].append(row["embedding"])
                continue
                
            if cids := re.findall(r"^clip:(\d+)@(\d+),(\d+),(\d+),(\d+)", term):
                for cid,x,y,w,h in cids:
                    print(f"need the region from {x},{y},{w},{h}")
                    ua = os.getenv("IEI_USER_AGENT",None)
                    thm = None
                    if ua:
                        headers = {'User-agent': ua}
                        metadata = iei.get_metadata(int(cid))
                        if metadata:
                            print(f"fetching {metadata.img_uri}")
                            thm,_,_,_ = iei.img_helper.fetch_img(metadata.img_uri,headers=headers)
                    else:
                        print("warning, need a user agent for full sized image")
                        thm = iei.get_thm(cid)

                    if thm: 
                        print("size before cropping is",thm.size)
                        cropped = iei.img_helper.crop_by_pct(thm,int(x),int(y),int(w),int(h))
                        cropped.save('/tmp/debug_1_cropped.jpg')
                        cropped = ImageOps.pad(cropped, (512,512))
                        cropped.save('/tmp/debug_2_scaled.jpg')
                        e = clipwrap.img_embeddings([cropped])[0]
                        embeddings['clip'].append(e)
                        embeddings['clip_scale_factors'].append(scale_factor)
                    else:
                        print(f"cant find thm for {cid}")
                continue

            if cids := re.findall(r"^clip:(\d+)", term):
                for cid in cids:
                    e = clipmeth(cid)
                    #e = e * scale_factor
                    embeddings['clip'].append(e)
                    embeddings['clip_scale_factors'].append(scale_factor)
                continue

            if cids := re.findall(r"^clip:(\[.*?\])", term):
                print("oooh - got a clip embedding {cids}")
                for cid in cids:
                    e = VectorHelper.cast_to_float32_array(json.loads(cid))
                    embeddings['clip'].append(e)
                    embeddings['clip_scale_factors'].append(scale_factor)
                continue
            
            if cids := re.findall(r"^(https?:\S*)", term):
                print("oooh - got a url {cids}")
                for cid in cids:
                    img,imgdata,dttm,imgbytes = iei.img_helper.fetch_img(cid)
                    tembs = clipwrap.img_embeddings([img])
                    for e in tembs:
                        embeddings['clip'].append(e)
                        embeddings['clip_scale_factors'].append(scale_factor)
                continue
                
            tembs = clipwrap.txt_embeddings([term])
            for e in tembs:
                #e = e * scale_factor
                e = VectorHelper.cast_to_float32_array(e)
                embeddings['clip'].append(e)
                embeddings['clip_scale_factors'].append(scale_factor)

        
        clip_result = face_result = None
        for e in embeddings['clip']:
            print(type(e))
        if len(embeddings['clip'])>0:
            clip_direction = embeddings['clip'][0] * embeddings['clip_scale_factors'][0]
            denominator = 2.0
            for e,s in zip(embeddings['clip'][1:],embeddings['clip_scale_factors'][1:]):
                clip_direction = VectorHelper.slerp(clip_direction,e,s/denominator)
               # denominator += 1
            clip_result = np.stack([clip_direction])
            # stacked_clip_embeddings = np.stack(embeddings['clip'])
            # for e in stacked_clip_embeddings:
            #     print("emag ",e@e.T)
            # clip_result = functools.reduce(lambda x,y: x+y, stacked_clip_embeddings)
            # clip_result /= np.linalg.norm(clip_result)
            # clip_result = np.stack([clip_result])
    
        if len(embeddings['face'])>0:
            face_result = np.stack(embeddings['face'])
        
        return clip_result,face_result
    
            
        
    def guess_user_intent(self,q) -> np.ndarray:
        """
        deprecated, copy&pasted from v1's rclip_server that didn't support faces
        """
        raise(DeprecationWarning("guess_user_intent is deprecated"))
        parser = self.parser
        parsed = parser.search_string(q)
        embeddings = []
        for (operator,magnitude),terms in parsed:
            if len(terms)>2 and terms[0] == '(' and terms[-1] == ')': terms=terms[1:-1]
            #print(operator,magnitude,terms)
            e = self.guess_user_intent_element(terms) * float(magnitude) * float(operator+'1')
            embeddings.append(e)
        if len(embeddings) == 0:
            return None
        result = functools.reduce(lambda x,y: x+y, embeddings)
        result /= np.linalg.norm(result)
        return result

    @functools.lru_cache
    def guess_user_intent_element(self,q) -> np.ndarray:
        """
        deprecated, copy&pasted from v1's rclip_server that didn't support faces

        Keeping here to remember to add https:// query terms and to test for backward compatibility
        """
        raise DeprecationWarning("deprecated")
        if re.match(r'^https?://',q):
            img = self.download_image(q)
            return self.get_image_embedding([img])

        if not q.startswith('{'):
            return self.get_text_embedding(q)

        data = json.loads(q)

        if img_id := data.get('image_id'):
            return np.asarray([self.image_embeddings[self.imgid_to_idx[img_id]]])

        if embedding := data.get('clip_embedding'):
            return np.asarray([embedding])

        if seed := data.get('random_img'):
            return np.asarray([random.choice(self.image_embeddings)])

        if seed := data.get('random_seed'):
            random.seed(seed)
            def rand_ndim_unit_vector(dims):
                """
                   https://stackoverflow.com/questions/6283080/random-unit-vector-in-multi-dimensional-space 
                """
                vec = [random.gauss(0, 1) for i in range(dims)]
                mag = sum(x**2 for x in vec) ** .5
                return [x/mag for x in vec]
            rnd_features = rand_ndim_unit_vector(512)
            return np.asarray([rnd_features])




#####################################################################################3

# import functools

# class LazyImg():
#     def __init__(self, img_id:int, iei:ImageEmbeddingIndexer):
#         self.img_id = img_id
        
#     @functools.cached_property
#     def img_data(self) -> ImgData:
#         return self.iei.img_data(self.img_id)

#     @functools.cached_property
#     def img_metadata(self) -> ImgMetadata:
#         return self.iei.img_metadata(self.img_id)

#     @functools.cached_property
#     def image(self) -> ImgData:
#         return self.iei.get_image(self.img_id)

#     @functools.cached_property
#     def thm(self) -> ImgData:
#         return self.iei.get_thm(self.img_id)
    
#     @functools.cached_property
#     def clip(self) -> ImgData:
#         return self.iei.clip(self.img_id)

#     @functools.cached_property
#     def face(self) -> ImgData:
#         return self.iei.face(self.img_id)

class ImageEmbeddingIndexer:
    """
      https://www.sqlite.org/fasterthanfs.html
      https://stackoverflow.com/questions/2330344/in-python-with-sqlite-is-it-necessary-to-close-a-cursor
    """
    ######################################################################
    # Cached Models
    ######################################################################

    @functools.cached_property
    def ocw(self) -> OpenClipWrapper:
        print(f"creating OpenClipWrapper {self.clip_model}")
        device = self.device
        model_name,pretrained = self.clip_model
        return OpenClipWrapper(model_name, pretrained, device)

    @functools.cached_property
    def ifw(self):
        print(f"creating InsightFaceWrapper")
        return InsightFaceWrapper()
    
    @functools.cached_property
    def oiw(self) -> OpenAIWrapper:
        print(f"creating OpenAIWrapper")
        device = self.device
        return OpenAIWrapper(device=device)

    @functools.cached_property
    def parser_helper(self):
        return ParserHelper(iei=self,use_openai_clip=self.use_openai_clip)

    ######################################################################
    # Cached key value stores
    ######################################################################
    
    def get_faiss_helper(self,namespace):
        path = f"{self.imgidx_path}/{namespace}"
        return FaissHelper(path)
    
    def get_kvs(self,namespace):
        path = f"{self.imgidx_path}/{namespace}.sqlite3"
        return SimpleSqliteKVStore(path)
    
    @functools.cached_property
    def thm_kvs(self) -> SimpleSqliteKVStore:
        w,h = self.thm_size
        return self.get_kvs(f'thm_{w}x{h}')
    
    @functools.cached_property
    def clip_kvs(self) -> SimpleSqliteKVStore:
        model_name,pretrained = self.clip_model
        return self.get_kvs(f'openclip__{model_name}__{pretrained}')
    
    @functools.cached_property
    def face_kvs(self) -> SimpleSqliteKVStore:
        return self.get_kvs(f'insightface')

    @functools.cached_property
    def laion_clip_faiss_helper(self) -> FaissHelper:
        model_name,pretrained = self.clip_model
        return self.get_faiss_helper(f'openclip__{model_name}__{pretrained}')
    
    @functools.cached_property
    def face_faiss_helper(self) -> FaissHelper:
        return self.get_faiss_helper(f'insightface')
    
    @functools.cached_property
    def openai_clip5_kvs(self) -> SimpleSqliteKVStore:
        safename = self.oiw.model_name.replace('/','_')
        return self.get_kvs(f'openaiclip_5_{safename}')
    
    @functools.cached_property
    def openai_clip_faiss_helper(self) -> FaissHelper:
        safename = self.oiw.model_name.replace('/','_')
        return self.get_faiss_helper(f'openaiclip_5_{safename}')
    
    @functools.cached_property
    def current_clip_faiss_helper(self) -> FaissHelper:
        if self.use_openai_clip:
            return self.openai_clip_faiss_helper
        else:
            return self.laion_clip_faiss_helper
    #######################################
    
    def __init__(self, 
                 imgidx_path=None,
                 clip_model=('ViT-B-32-quickgelu','laion400m_e32'),
                 thm_size = (320,640),
                 device='cpu',
                 synchronous='OFF',
                 debug=True,
                 use_openai_clip=False,
                 throttle_max_rate=0.0,
                 create_if_missing=False,
                 ):
        #configure_sqlite3()
        if not imgidx_path:
            print("no path was specified - trying environment")
            imgidx_path = os.getenv("IEI_PATH","./data/image_embedding_indexes")
        print(f"constructing ImageEmbeddingIndexer at {imgidx_path}")

        if create_if_missing:
            os.makedirs(imgidx_path , exist_ok=True)
        self.imgidx_path       = imgidx_path
        self.clip_model        = clip_model
        self.device            = device
        self.thm_size          = thm_size
        self.metadata_db       = sqlite3.connect(f"{imgidx_path}/img_metadata.sqlite3")
        self.img_helper        = ImgHelper(throttle_max_rate = throttle_max_rate)
        self.debug             = debug
        self.use_openai_clip   = use_openai_clip

        pragma_sql = f"PRAGMA synchronous = {synchronous};"
        self.metadata_db.execute(pragma_sql)
        self.metadata_db.commit()
        
        # attributes of pointers to the image
        create_img_metadata_sql="""
          CREATE TABLE IF NOT EXISTS img_meta_data (
            meta_id  INTEGER  PRIMARY KEY,
            img_uri  TEXT     NOT NULL UNIQUE,
            src_uri  TEXT,
            title    TEXT,
            subtitle TEXT,
            metadata TEXT,
            dttm     DATETIME NOT NULL,
            img_id   INTEGER  
          );
        """
        create_index_sql = """
            CREATE INDEX IF NOT EXISTS img_meta_data__img_id ON img_meta_data(img_id);
        """
        
        ## TODO - bug - height,width order here doesn't match
        # attributes of the source image itself
        create_img_data_sql="""
          CREATE TABLE IF NOT EXISTS img_data (
            img_id   INTEGER PRIMARY KEY,
            sha224   TEXT    NOT NULL UNIQUE,
            height   INTEGER NOT NULL,
            width    INTEGER NOT NULL,
            bytesize INTEGER NOT NULL,
            dttm     DATETIME NOT NULL,
            mimetype TEXT
          );
        """
        
        # Consider 1-to-many thumbnails per image.
#         # Different scales / crops of the image
#         create_img_thm_sql="""
#           CREATE TABLE IF NOT EXISTS img_data (
#             thm_id   INTEGER PRIMARY KEY,
#             img_id   INTEGER,
#             x        INTEGER,
#             y        INTEGER,
#             w        INTEGER,
#             h        INTEGER,        
#             sha224   TEXT    NOT NULL UNIQUE,
#             height   INTEGER NOT NULL,
#             width    INTEGER NOT NULL,
#             mimetype TEXT
#           );
#         """

        # key-value stores for thumbnails and embedding vectors
        self.metadata_db.execute(create_img_data_sql)
        self.metadata_db.execute(create_img_metadata_sql)
        self.metadata_db.execute(create_index_sql)
        self.metadata_db.commit()
        
    
    ##################################
    ###  Img Data
    ##################################
      
    def get_img_data(self,key):
        """ key can either be an int (img_id) or a str (sha224) """
        db  = self.metadata_db
        col = isinstance(key,int) and "img_id" or "sha224"
        cols     = [f.name for f in dataclasses.fields(ImgData)]
        sql_c = ",".join(cols)
        sql = f"select {sql_c} from img_data where {col}=?"
        for row in db.execute(sql,[key]):
            return ImgData(*row)
    
    def set_img_data(self,data:ImgData):
        """  """
        db       = self.metadata_db
        cols     = [f.name for f in dataclasses.fields(data)]
        icols    = cols[1:]
        sql_c = ",".join(icols)
        sql_v = ",".join(['?' for _ in icols])
        valdict  = dataclasses.asdict(data)
        vals     = [valdict[k] for k in icols]
        sql      = f"insert into img_data ({sql_c}) values ( {sql_v} )"
        db.execute(sql,vals)
        db.commit()
            
    ##################################
    ### ImgMetadata 
    ##################################

    def get_metadata(self,key):
        """ key can either be an int (img_id) or a str (img_uri) """
        db  = self.metadata_db
        col = isinstance(key,int) and "img_id" or "img_uri"
        sql = f"select * from img_meta_data where {col}=?"
        for row in db.execute(sql,[key]):
            return ImgMetadata(*row)

    def get_all_metadata(self,key) -> Generator[ImgMetadata, None, None]:
        """ key can either be an int (img_id) or a str (img_uri) """
        db  = self.metadata_db
        sql = f"select * from img_meta_data"
        for row in db.execute(sql):
            yield ImgMetadata(*row)
        
    def set_metadata(self,data:ImgMetadata):
        """ key can either be an int (img_id) or a str (sha224) """
        db       = self.metadata_db
        cols     = [f.name for f in dataclasses.fields(data)]
        icols    = cols[1:]
        sql_c = ",".join(icols)
        sql_v = ",".join(['?' for _ in icols])
        valdict  = dataclasses.asdict(data)
        vals     = [valdict[k] for k in icols]
        sql      = f"insert into img_meta_data ({sql_c}) values ( {sql_v} )"
        db.execute(sql,vals)
        db.commit()
        
    ########################### deprecated ######################
    # def make_thm(self,img,w=224,h=224):
    #     i2 = img.convert("RGBA")
    #     return ImageOps.pad(i2,(w,h),Image.Resampling.LANCZOS,color=(127,127,127,0))    
    # def img_bytes(self,img):
    #     buf = io.BytesIO()
    #     img.save(buf,format="WebP",quality=25)
    #     return buf.getvalue()

    ##################################
    ### Thumbnails 
    ##################################

    def get_thm(self,img_id):
        thm_bytes = self.thm_kvs.get(img_id)
        if not thm_bytes: return None
        thm       = Image.open(io.BytesIO(thm_bytes))
        return thm
    
    def get_thm_bytes(self,img_id):
        return self.thm_kvs.get(img_id)
        
    def set_thm(self,img_id,img):
        w,h = self.thm_size
        thm = self.img_helper.make_thm(img,max_w=w,max_h=h)
        thm_bytes = self.img_helper.img_bytes(thm,quality=85)
        self.thm_kvs[img_id] = thm_bytes
    ##################################
    ### save them as numpy bytes of float16s
    ##################################
    
#     def torch_to_bytes(self,t):
#         return t.cpu().to(torch.float16).numpy().tobytes()
    
#     def np_to_bytes(self,n):
#         return n.astype(np.float16).tobytes()
    
#     def bytes_to_np(self,b):
#         return np.frombuffer(b,dtype=np.float16)

    def normalize(self,v):
        n = np.linalg.norm(v,axis=-1,keepdims=True) + np.finfo(v.dtype).eps
        return v/n
    
    ################
    # openai clip
    ################

    def get_openai_clip_embedding(self,img_id) -> Union[np.ndarray, None]: # np.ndarray|None: # 3.9 hack
        b = self.openai_clip5_kvs.get(img_id)
        ce = b and pickle.loads(b)
        if isinstance(ce,np.ndarray):
            # the first embedding is for the whole image
            return ce[0] 
        else:
            return None
        
    def get_all_openai_clip_embeddings(self):
        " for autofaiss "
        ids = []
        emb = []
        for k,v in self.openai_clip5_kvs.iter_with_values():
            es = pickle.loads(v)
            for e in es:
                en = self.normalize(e)
                ids.append(k)
                emb.append(en)
                if only_use_one_clip_embedding := True:
                    break;
        return (ids,emb)
    
    def set_openai_clip_embedding(self,img_id:int,img:Image.Image):
        kvs = self.openai_clip5_kvs
        if done := self.openai_clip5_kvs[img_id]:
            print(f"already had {img_id}")
            pass
        thms = self.img_helper.make_5_tiles(img)
        emb_t = self.oiw.img_embeddings(thms)
        emb_np = emb_t.cpu().to(torch.float16).numpy()
        kvs[img_id] = pickle.dumps(emb_np)

    def make_openai_clip_faiss_index(self):
        ids,embs = self.get_all_openai_clip_embeddings()
        embs = np.stack(embs)
        fh = self.openai_clip_faiss_helper
        return fh.create_index(ids,embs)
    
    ################
    # LAION openclip
    ################
    
    def get_laion_clip_embedding(self,img_id) -> Union[np.ndarray, None]: # np.ndarray|None: # 3.9 hack
        b = self.clip_kvs.get(img_id)
        ce = b and pickle.loads(b)
        if isinstance(ce,np.ndarray):
            return ce
        else:
            return None
        
    def set_laion_clip_embedding(self,img_id:int,img:Image.Image):
        kvs         = self.clip_kvs
        emb_t       = self.ocw.img_embeddings([img])[0]
        emb_np      = emb_t.cpu().to(torch.float16).numpy()
        kvs[img_id] = pickle.dumps(emb_np)
        
    def get_all_laion_clip_embeddings(self):
        " for autofaiss "
        ids = []
        emb = []
        for k,v in self.clip_kvs.iter_with_values():
            e = pickle.loads(v)
            en = self.normalize(e)
            ids.append(k)
            emb.append(en)
        return (ids,emb)
    
    def make_laion_clip_faiss_index(self):
        ids,embs = self.get_all_laion_clip_embeddings()
        embs = np.stack(embs)
        fh = self.laion_clip_faiss_helper
        return fh.create_index(ids,embs)

    ################
    # allow switching CLIP libraries more easily.
    ################

    def get_current_clip_embedding(self,img_id) -> Union[np.ndarray, None]: # np.ndarray|None: # 3.9 hack
        if self.use_openai_clip:
            return self.get_openai_clip_embedding(img_id)
        else:
            return self.get_laion_clip_embedding(img_id)
        
    def set_current_clip_embedding(self,img_id:int,img:Image.Image):
        if self.use_openai_clip:
            return self.set_openai_clip_embedding(img_id,img)
        else:
            return self.set_laion_clip_embedding(img_id,img)
        
    def get_all_current_clip_embeddings(self):
        if self.use_openai_clip:
            return self.get_all_openai_clip_embeddings()
        else:
            return self.get_all_laion_clip_embeddings()
        
    def make_current_clip_faiss_index(self):
        if self.use_openai_clip:
            return self.make_openai_clip_faiss_index()
        else:
            return self.make_laion_clip_faiss_index()
        


    ################
    # InsightFace
    ################

    def get_insightface_analysis(self,img_id):
        b = self.face_kvs.get(img_id)
        return b and pickle.loads(b)
    
    def to_float16(self,a):
        if isinstance(a,np.ndarray) and a.dtype == np.dtype('float32'):
            return a.astype(np.float16)
        else:
            return a
    
    def set_insightface_analysis(self,img_id,img):
        t_img       = ImageOps.exif_transpose(img)
        kvs         = self.face_kvs
        res         = self.ifw.analyze(t_img)
        r2          = [{k:self.to_float16(v) for k,v in r.items()} for r in res]
        kvs[img_id] = pickle.dumps(r2)
        
    def get_all_insightface_embeddings(self):
        " for autofaiss "
        ids = []
        emb = []
        for k,v in self.face_kvs.iter_with_values():
            for row in pickle.loads(v):
                e = row['embedding']
                en = self.normalize(e)
                ids.append(k)
                emb.append(en)
        return (ids,emb)

    def make_insightface_faiss_index(self):
        ids,embs = self.get_all_insightface_embeddings()
        embs = np.stack(embs)
        fh = self.face_faiss_helper
        return fh.create_index(ids,embs)

    ######################
    ## make both indexes
    ######################
    
    def make_all_faiss_indexes(self):
        print("making insightface's index")
        i1 = self.make_insightface_faiss_index()
        if self.use_openai_clip:
            print("making openai clip's index")
            i2 = self.make_openai_clip_faiss_index()
        else:
            print("making openclip's index")
            i2 = self.make_laion_clip_faiss_index()
        return (i1,i2)
        
    ######################
    ## Preprocess an image
    ######################
    
    def preprocess_img(self, 
                       img_uri, src_uri, 
                       title, subtitle, extra_metadata,
                       recheck = True,
                       headers=None
                       ):
        
        t0 = time.time()
        
        img,idata = None,None

        metadata = self.get_metadata(img_uri)
                    
        if metadata:
            #print(f"already had metadata for {img_uri} = {metadata.img_id}")
            img_id = metadata.img_id
            idata = self.get_img_data(img_id)
            if not idata:
                print("surprising error - no image data for metadata")
        
        if not idata:
            img,idata,mtime,img_bytes = self.img_helper.fetch_img(img_uri,headers=headers)
            if saved_idata := self.get_img_data(idata.sha224):
                #print(f"already had img_data for {idata.sha224} => {saved_idata.img_id}")
                idata = saved_idata
            else:
                self.set_img_data(idata)
                idata = self.get_img_data(idata.sha224)

        if not idata:
            raise Exception(f"preprocess_img expected idata for {img_uri}")
        
        img_id = idata.img_id
        
        if not img_id:
            print(f"Failed to get id for {img_uri}")
            return
            
        if not metadata:
            #print("saving metadata")
            metadata = ImgMetadata(None,
                             img_uri,
                             src_uri,
                             title,
                             subtitle,
                             extra_metadata,
                             idata.dttm,
                             img_id)
            self.set_metadata(metadata)
            metadata = self.get_metadata(img_uri) or metadata

        if idata.height <= 224 and idata.width <= 224:
            # print("probably already a thumbnail and not worth indexing")
            return (img_id,time.time()-t0,0,0,0)
        
        thm  = self.get_thm(img_id)
        clip = self.get_current_clip_embedding(img_id)
        face = self.get_insightface_analysis(img_id)
        need_image = (thm is None) or (clip is None) or (face is None)
        if not need_image:
            #print(f"{img_id} was already done")
            return (img_id,time.time()-t0,0,0,0)

        if need_image and (img is None):
            if self.debug:
                print(f"{img_id} needed image: {(thm is None)} or {(clip is None)} or {(face is None)}")
            img,_,_,_ = self.img_helper.fetch_img(metadata.img_uri,headers=headers)

        if not img:
            print(f"Error: preprocess_img expected img for {img_uri}")
            return img_id
        
        if img.mode == 'I':
            img = self.img_helper.convert_I_to_L(img)
            print("Warning: working around issues for PIL image mode 'I'")

        t1 = time.time()
        if thm is None:   self.set_thm(img_id,img)
        t2 = time.time()
        if clip is None:  self.set_current_clip_embedding(img_id,img)
        t3 = time.time()
        if face is None:  self.set_insightface_analysis(img_id,img)
        t4 = time.time()
        return (img_id,t1-t0,t2-t1,t3-t2,t4-t3)
    

    def reprocess_image(self,imgid,headers={}):
        md = self.get_metadata(imgid)
        if not md:
            return(f"can't find {imgid}")
        del(self.clip_kvs[imgid])
        del(self.thm_kvs[imgid])
        del(self.face_kvs[imgid])
        return self.preprocess_img(md.img_uri,
                        md.src_uri,
                        md.title,
                        md.subtitle,
                        md.metadata,
                        headers=headers)

#     def encode_pytorch_to_bytes(self,t):
#         return t.cpu().to(torch.float16).numpy().tobytes()
    
#     def decode_bytes_to_numpy(self,b):
#         return np.frombuffer(b,dtype=np.float16)
    
    # TODO - consider re-creating the batch processing utils

    # def precompute_openclip_embeddings(self,img_ids):
    #     kvs = self.clip_kvs
    #     thms = [self.get_thm(i) for i in img_ids]
    #     embs = self.ocw.img_embeddings(thms)
    #     edat = [self.encode_pytorch_to_bytes(e) for e in embs]
    #     kvs.setitems(img_ids,edat)

    # def find_missing_openclip_embeddings(self):
    #     emb_ids = [k for k in self.clip_kvs()]
    #     thm_ids = [k for k in self.thm_kvs()]
    #     missing = set(thm_ids) - set(emb_ids)
    #     return missing
    
    # def calculate_missing_openclip_embeddings(self):
    #     missing    = list(self.find_missing_openclip_embeddings())
    #     print(f"missing {len(missing)} embeddings")
    #     t0 = time.time()
    #     t1 = t0
    #     n  = 0
    #     counter = 0
    #     for i in range(0, len(missing), batch_size):
    #         batch = missing[i:i+batch_size]
    #         self.precompute_openclip_embeddings(batch)
    #         n += len(batch)
    #         counter += 1
    #         t2 = time.time()
    #         print(f"Computed {n} in {t2-t0:6.2f} sec ({len(batch)/(t2-t1):4.2f}/s)")
    #         t1 = t2


# In[332]:


#!rm -r data/image_embedding_indexes


# In[ ]:





# In[333]:


# In[ ]:





# In[ ]:





# In[334]:


#ii.calculate_missing_openclip_embeddings()
on_gpu ="""
missing 900 embeddings
Computed 100 in 0.3227503299713135 sec (309.8370186295027) per sec
Computed 200 in 0.587254524230957 sec (340.567831745377) per sec
Computed 300 in 0.8521981239318848 sec (352.03081487184625) per sec
Computed 400 in 1.1190969944000244 sec (357.43103770415354) per sec
Computed 500 in 1.3885352611541748 sec (360.0916836525932) per sec
Computed 600 in 1.6588504314422607 sec (361.6962618373856) per sec
Computed 700 in 1.9163048267364502 sec (365.28635227211225) per sec
Computed 800 in 2.179753065109253 sec (367.01404980472074) per sec
Computed 900 in 2.4555177688598633 sec (366.52147722713676) per sec
"""
on_cpu = """
missing 8982 embeddings
Computed 100 in 6.264883756637573 sec (15.961988104575944) per sec
Computed 200 in 12.055073976516724 sec (16.590524487000234) per sec
Computed 300 in 17.7634494304657 sec (16.88861170654595) per sec
Computed 400 in 23.49348211288452 sec (17.02599887398676) per sec
Computed 500 in 29.26191282272339 sec (17.087057945566844) per sec
"""


# In[ ]:




