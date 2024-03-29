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
import autofaiss
import base64
import dataclasses
import datetime
import email
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


# In[322]:


@dataclasses.dataclass
class ImgData():
    img_id   :int
    sha224   :str
    width    :int
    height   :int
    bytesize :int
    dttm     :datetime.datetime
    mimetype :str
    
@dataclasses.dataclass
class ImgMetadata():
    meta_id  :int
    img_uri  :str
    src_uri  :str
    title    :str
    subtitle :str
    metadata :str
    dttm     :datetime.datetime
    img_id   :int


# In[323]:


os.environ['CUDA_VISIBLE_DEVICES'] = '0'
#os.environ['CUDA_VISIBLE_DEVICES'] = ''
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
            
    def get_pretrained_models():
        return open_clip.list_pretrained()
    
    def embeddings_for_images(self,imgs):
        with torch.no_grad(), torch.cuda.amp.autocast(): # type: ignore
            preprocessed = torch.stack([self.preprocess(i) for i in imgs]).to(self.device)
            features = self.model.encode_image(preprocessed) # type: ignore
            features /= features.norm(dim=-1, keepdim=True)
            return features
    
    def embeddings_for_texts(self,txts):
        with torch.no_grad(), torch.cuda.amp.autocast():# type: ignore
            tokenized = self.tokenize(txts).to(self.device)
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
            clr = tuple(random.sample([255,random.randint(0,255),0],3))
            for p in pic.get('landmark_2d_106',[]):
                pts = [c-1 for c in p] + [c+1 for c in p]
                draw.rectangle(tuple(pts),outline=clr,width=2)
            draw.rectangle(pic['bbox'],outline=clr,width=5)
        return img


# In[ ]:





# In[325]:


import filelock
import collections
import collections.abc
#collections.abc.MutableMapping
class SimpleSqliteKVStore(collections.abc.MutableMapping):
    # TODO - add file locking.
    def __init__(self,imgidx_path):
        self.imgidx_path = imgidx_path
        self.lock = filelock.FileLock(imgidx_path + '.lock',timeout=10)
        self.db_conn = sqlite3.connect(imgidx_path)
        create_kv_sql = "CREATE TABLE IF NOT EXISTS kv (k INTEGER PRIMARY KEY, v BLOB)"
        self.db_conn.execute(create_kv_sql)
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
            
    def setitems(self,ks,vs):
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


class FaissHelper:
    
    def __init__(self,prefix:str):
        self.index_path = f"{prefix}.faiss"
        self.id_path    = f"{self.index_path}.id_lookup.txt.gz"
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
            scores = (np.stack(embs) @ target.T)#[:,0]
            result = sorted(zip(scores,ids),key=lambda x:-x[0])[0:k]
            results.append(result)
        return results
    
    def search(self,target,k=10):
        idl = self.id_lookup
        dsts, idxs = self.faiss_index.search(target, k)
        results = []
        for drow,irow in zip(dsts,idxs):
            result = zip(drow,[idl[i] for i in irow])
            results.append(list(result))
        return results
        
        # return  zip(dsts[0], [idl[i] for i in idxs[0]])
        #     results.append(result)
        # return results
        
    def normalize(self,v):
        n = np.linalg.norm(v,axis=-1,keepdims=1) + np.finfo(v.dtype).eps
        return v/n

    def create_index(self,ids,embs):
        embeddings    = np.stack(embs)
        autofaiss.build_index(
                      embeddings=embeddings,
                      index_path=self.index_path,
                      index_infos_path=f"{self.index_path}.infos",
                      max_index_query_time_ms = 300,
                      min_nearest_neighbors_to_retrieve = 1000,
                      max_index_memory_usage = "3G",
                      current_memory_available = "8G",
                      should_be_memory_mappable = True,
                      metric_type="ip"
                     )
        img_id_np = np.array(ids,dtype=np.int32)
        np.savetxt(self.id_path, img_id_np, fmt='%d')
        self.load()
        return   
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


class ImgHelper:
        
    def fetch_img(self,uri) -> (Image,ImgData,datetime):
        if re.match(r'^https?:',uri):
            resp = requests.get(uri)
            mtime_h = resp.headers.get('Last-Modified')
            mtime  = mtime_h and email.utils.parsedate_to_datetime(mtime_h)
            img_bytes = resp.content
        else:
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(uri),
                                                    tz=datetime.timezone.utc)
            with open(uri,"rb") as f:
                img_bytes = f.read()
        bytesize = len(img_bytes)
        img      = Image.open(io.BytesIO(img_bytes))
        mimetype = img.get_format_mimetype()
        sha224   = base64.b85encode(hashlib.sha224(img_bytes).digest()).decode('utf-8')
        w,h      = img.size
        img_data = ImgData(None,sha224,w,h,bytesize,mtime,mimetype)
        return (img, img_data)

    def make_thm(self,img:Image.Image,w=256,h=256) -> Image.Image:
        i2 = img.convert("RGBA")
        return ImageOps.pad(i2,(w,h),Image.Resampling.LANCZOS,color=(127,127,127,0))
    
    def img_bytes(self,img,quality=85):
        buf = io.BytesIO()
        img.save(buf,format="WebP",quality=quality)
        return buf.getvalue()
    
    def bytes_to_data_url(self,b: bytes) -> str:
        e = base64.b64encode(b).decode('utf-8')
        return f'data:image/jpg;base64,{e}'
    
    def get_data_url(self,url: str) -> bytes:
        try:
            i,d,m = get_img(url)
            t = make_thm(i)
            b = img_bytes(t)
            u = bytes_to_data_url(b)
            return u
        except:
            return None
        


# In[329]:


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


# In[330]:


'#' * 70


# In[331]:


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
    def clip_faiss_helper(self) -> FaissHelper:
        model_name,pretrained = self.clip_model
        return self.get_faiss_helper(f'openclip__{model_name}__{pretrained}')
    
    @functools.cached_property
    def face_faiss_helper(self) -> FaissHelper:
        return self.get_faiss_helper(f'insightface')

    #######################################
    
    def __init__(self, 
                 imgidx_path="./data/image_embedding_indexes", 
                 clip_model=('ViT-B-32-quickgelu','laion400m_e32'),
                 thm_size = (256,256),
                 device='cpu'):
        #configure_sqlite3()
        os.makedirs(imgidx_path , exist_ok=True)
        self.imgidx_path       = imgidx_path
        self.clip_model        = clip_model
        self.device            = device
        self.thm_size          = thm_size
        self.metadata_db       = sqlite3.connect(f"{imgidx_path}/img_metadata.sqlite3")
        self.img_helper        = ImgHelper()
        
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
        sql = f"select * from img_data where {col}=?"
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
        
    def get_all_metadata(self,key):
        """ key can either be an int (img_id) or a str (img_uri) """
        db  = self.metadata_db
        col = isinstance(key,int) and "img_id" or "img_uri"
        sql = f"select * from img_meta_data where {col}=?"
        for row in db.execute(sql,[key]):
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

    def get_thm(self,img_id,w=256,h=256):
        thm_bytes = self.thm_kvs.get(img_id)
        if not thm_bytes: return None
        thm       = Image.open(io.BytesIO(thm_bytes))
        if ((w,h) == self.thm_size):
            return thm
        else:
            print("warning, resizing thumbnails not yet supported")
            return thm
        
    def set_thm(self,img_id,img):
        w,h = self.thm_size
        thm = self.img_helper.make_thm(img,w=w,h=h)
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
        n = np.linalg.norm(v,axis=-1,keepdims=1) + np.finfo(v.dtype).eps
        return v/n
    
    ################
    # openclip
    ################
    
    def get_openclip_embedding(self,img_id) -> np.ndarray:
        b = self.clip_kvs.get(img_id)
        return b and pickle.loads(b)
        
    def set_openclip_embedding(self,img_id,img):
        kvs         = self.clip_kvs
        emb_t       = self.ocw.embeddings_for_images([img])[0]
        emb_np      = emb_t.cpu().to(torch.float16).numpy()
        kvs[img_id] = pickle.dumps(emb_np)
        
    def get_all_openclip_embeddings(self):
        " for autofaiss "
        ids = []
        emb = []
        for k,v in self.clip_kvs.iter_with_values():
            e = pickle.loads(v)
            en = self.normalize(e)
            ids.append(k)
            emb.append(e)
        return (ids,emb)
    
    def make_openclip_faiss_index(self):
        ids,embs = self.get_all_openclip_embeddings()
        embs = np.stack(embs)
        fh = self.clip_faiss_helper
        fh.create_index(ids,embs)


    ################
    # InsightFace
    ################

    def get_insightface_analysis(self,img_id):
        b = self.face_kvs.get(img_id)
        return b and pickle.loads(b)
    
    def set_insightface_analysis(self,img_id,img):
        kvs         = self.face_kvs
        res         = self.ifw.analyze(img)
        to16bit     = lambda x: x.astype(np.float16) if isinstance(x,np.ndarray) else x
        r2          = [{k:to16bit(v) for k,v in r.items()} for r in res]
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
        fh.create_index(ids,embs)

    ######################
    ## make both indexes
    ######################
    
    def make_all_faiss_indexes(self):
        print("making insightface's index")
        self.make_insightface_faiss_index()
        print("making openclip's index")
        self.make_openclip_faiss_index()
        
    ######################
    ## Preprocess an image
    ######################
    
    def preprocess_img(self, 
                       img_uri, src_uri, 
                       title, subtitle, metadata,
                       recheck = True):
        
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
            img,idata = self.img_helper.fetch_img(img_uri)
            if saved_idata := self.get_img_data(idata.sha224):
                #print(f"already had img_data for {idata.sha224} => {saved_idata.img_id}")
                idata = saved_idata
            else:
                self.set_img_data(idata)
                idata = self.get_img_data(idata.sha224)
        
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
                             metadata,
                             idata.dttm,
                             idata.img_id)
            self.set_metadata(metadata)
            metadata = self.get_metadata(img_uri)

        thm  = self.get_thm(idata.img_id)
        clip = self.get_openclip_embedding(idata.img_id)
        face  = self.get_insightface_analysis(idata.img_id)
        need_image = (thm is None) or (clip is None) or (face is None)
        if need_image and (img is None):
            print(f"{idata.img_id} needed image: {(thm is None)} or {(clip is None)} or {(face is None)}")
            img,_ = self.img_helper.fetch_img(metadata.img_uri)
        t1 = time.time()
        
        if thm is None:   self.set_thm(img_id,img)
        t2 = time.time()
        if clip is None:  self.set_openclip_embedding(img_id,img)
        t3 = time.time()
        if face is None:  self.set_insightface_analysis(img_id,img)
        t4 = time.time()
        print(t1-t0,t2-t1,t3-t2,t4-t3)
        return img_id
    
#     def encode_pytorch_to_bytes(self,t):
#         return t.cpu().to(torch.float16).numpy().tobytes()
    
#     def decode_bytes_to_numpy(self,b):
#         return np.frombuffer(b,dtype=np.float16)
        
    def precompute_openclip_embeddings(self,img_ids):
        kvs = self.clip_kvs()
        thms = [self.get_thm(i) for i in img_ids]
        embs = self.ocw.embeddings_for_images(thms)
        edat = [self.encode_pytorch_to_bytes(e) for e in embs]
        kvs.setitems(img_ids,edat)

    def find_missing_openclip_embeddings(self):
        emb_ids = [k for k in self.clip_kvs()]
        thm_ids = [k for k in self.thm_kvs()]
        missing = set(thm_ids) - set(emb_ids)
        return missing
    
    def calculate_missing_openclip_embeddings(self):
        batch_size = 100
        missing    = list(self.find_missing_openclip_embeddings())
        print(f"missing {len(missing)} embeddings")
        t0 = time.time()
        t1 = t0
        n  = 0
        counter = 0
        for i in range(0, len(missing), batch_size):
            batch = missing[i:i+batch_size]
            self.precompute_openclip_embeddings(batch)
            n += len(batch)
            counter += 1
            t2 = time.time()
            print(f"Computed {n} in {t2-t0:6.2f} sec ({len(batch)/(t2-t1):4.2f}/s)")
            t1 = t2


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




