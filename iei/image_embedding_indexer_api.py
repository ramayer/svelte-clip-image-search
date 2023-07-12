#!/usr/bin/env python
#
# see localhost:8000/docs
#
#   Search syntax:
#
#      zebra -mammal +fish
#      clip:1234
#      "cats and dogs" -""
#
#      face:4321.2
#      text:"hello world"
#      around:1234

import re
import os
from typing import Optional, Union
from fastapi import FastAPI
from pydantic import BaseModel

import fastapi
import image_embedding_indexer

from fastapi.responses import ORJSONResponse
from fastapi.responses import RedirectResponse


print("Starting")

iei = image_embedding_indexer.ImageEmbeddingIndexer();
app = FastAPI()
hdrs = {'Cache-Control': f'public, max-age={60*60*24*365}'}
hdrs = {'Cache-Control': f'public, max-age={60*5}'}

#####################################################################
#
#####################################################################
@app.on_event("startup")
async def initialize_large_models():
   iei.ocw
   iei.ifw


@app.get("/")
async def home():
    return {"Hello": "World"}


import orjson
import io
import time
@app.get("/thm/{img_id}")
async def thm(img_id:int, w:int|None=None,h:int|None=None):
  hdrs = {'Cache-Control': 'public, max-age=300'}
  debug_no_cache_hdrs = {
     'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0',
  }

  #time.sleep(0.1)
  if (h or w) and (thm := iei.get_thm(img_id)):
    #print("recompressing")
    buf = io.BytesIO()
    t2 = iei.img_helper.make_thm(thm,max_w=w or 1024,max_h=h or 1024)
    t2.save(buf,format="WebP",quality=50)
    return fastapi.Response(content = buf.getvalue(), headers = hdrs, media_type="image/webp")
  if b := iei.get_thm_bytes(img_id):
    return fastapi.Response(content = b, headers = hdrs, media_type="image/webp")
  size=1024
  svg = f'''<svg version="1.1" width="{size}" height="{int(size*3/4)}" xmlns="http://www.w3.org/2000/svg">
              <!--<rect width="100%" height="100%" fill="#333" /> -->
              <circle cx="50%" cy="50%" r="25%" fill="#222"/>
            </svg>'''
  return fastapi.Response(svg,media_type="image/svg+xml", headers=hdrs)
  

@app.get("/img/{img_id}")
async def img(img_id:int, size:int=400):
  req_hdrs = {'User-agent': 
          "Clip Embedding Calculator/0.01 (https://github.com/ramayer/wikipedia_in_spark; ) generic-library/0.0"}
        
  metadata = iei.get_metadata(img_id)

  if not metadata:
     raise fastapi.HTTPException(status_code=404, detail=f"no metdata for {img_id}")
  
  if re.match(r'^http',metadata.img_uri):
    print(f"redirecting to {metadata.img_uri}")
    response = fastapi.responses.RedirectResponse(url=metadata.img_uri)
    return response
  else:
    img,_,_,img_bytes = iei.img_helper.fetch_img(metadata.img_uri,headers=req_hdrs)
    if not img_bytes:
      raise fastapi.HTTPException(status_code=404, detail=f"can't load image for {img_id}")
    hdrs = {'Cache-Control': 'public, max-age=300'}
    return fastapi.Response(content = img_bytes, headers = hdrs, media_type="image/webp")


@app.get("/det/{img_id}")
async def det(img_id:int, size:int=400):
  metadata = iei.get_metadata(img_id)

  if not metadata:
     raise fastapi.HTTPException(status_code=404, detail=f"no metdata for {img_id}")
  
  if re.match(r'^http',metadata.src_uri):
    print("redirecting to {metadata.src_uri}")
    response = fastapi.responses.RedirectResponse(url=metadata.src_uri)
    return response
  else:
    img,_,_,img_bytes = iei.img_helper.fetch_img(metadata.img_uri,headers={'whatever':'0'})
    if not img_bytes:
      raise fastapi.HTTPException(status_code=404, detail=f"can't load image for {img_id}")
    hdrs = {'Cache-Control': 'public, max-age=300'}
    return fastapi.Response(content = img_bytes, headers = hdrs, media_type="image/webp")

# represent the vector's direction as well as possible with 3-digit ints.
# it can be scaled back to a unit vector on the other side.
def to_block_fp(a):
   if isinstance(a,np.ndarray) and  a.dtype == np.dtype('float16') and a.shape[0]>100:
      return (999 * a / np.max(a)).astype(np.int16)
   else:
      return a.astype(np.float32)

@app.get("/met/{img_id}")
async def met(img_id:int, size:int=400):
  img_data = iei.get_img_data(img_id)
  metadata = iei.get_metadata(img_id)
  to32bit     = lambda x: to_block_fp(x) if isinstance(x,np.ndarray) else x
  clip_emb = to32bit(iei.get_openclip_embedding(img_id))
  face_dat = iei.get_insightface_analysis(img_id)
  face2    = [{k:to_block_fp(v) for k,v in r.items()} for r in (face_dat or [])]
  data = {
     'img_data':img_data,
     'metadata':metadata,
     'clip_emb':clip_emb,
     'face_dat':face2,
  }
  cleaner = orjson.loads(orjson.dumps(data,option=orjson.OPT_SERIALIZE_NUMPY))
  return cleaner




#####################################################################
from fastapi import FastAPI, Response
@app.get("/similar_images/{img_id}")
async def similar_images(img_id:int, response:fastapi.Response, k:Optional[int]=400)-> list[float]:
  print(f"here response headers is {response.headers}")
  response.headers.update(hdrs)
  print(f"here response headers is {response.headers}")
  query = iei.get_openclip_embedding(img_id)
  if query and query.any():
    res = iei.clip_faiss_helper.search(np.stack([query]),k or 400)
    r3 = orjson.loads(orjson.dumps(res,option=orjson.OPT_SERIALIZE_NUMPY))
    return r3
  else:
     return []

@app.get("/clip_img_emb/{img_id}")
async def clip_img_emb(img_id:int, size:Optional[int]=400)-> list[float] | None:
  res = iei.get_openclip_embedding(img_id)
  if res:
     return res.tolist()
  else:
     return None

import numpy as np
@app.get("/insightface_analysis/{img_id}")
async def instightface_analysis(img_id:int, size:Optional[int]=400):
  res = iei.get_insightface_analysis(img_id)
  if res:
    to32bit     = lambda x: x.astype(np.float32) if isinstance(x,np.ndarray) else x
    r2          = [{k:to32bit(v) for k,v in r.items()} for r in res]
    r3 = orjson.loads(orjson.dumps(r2,option=orjson.OPT_SERIALIZE_NUMPY))
    return ORJSONResponse(r3)

#####################################################################

class SearchResults(BaseModel):
    imgids: list[int]
    scores: list[int]
import random
@app.get("/search")
async def search(q: Optional[str] = None, iid: Optional[int] = None, type: Optional[str] = None):
    # Process the parameters and generate response data
    # Replace this with your actual implementation
    results = None
    print("q is ",q)
    if q and (fids := re.findall(r'^face:((\d+)\.?(\d*))',q)):
        print(f"fids is {fids}")
        embeddings = []
        for _,img_id,idx in fids:
          ia = iei.get_insightface_analysis(img_id)
          if idx and ia:
             row = ia[int(idx)]
             embeddings.append(row['embedding'])
             print(f"found one {img_id}.{idx}")
          elif ia:
             print(f"getting {len(ia)} for {img_id}")
             for row in ia:
              embeddings.append(row['embedding'])               
        if len(embeddings):
            e = np.stack(embeddings)
            fh = iei.face_faiss_helper
            results = fh.search(e,k=5000)
        else:
           print(f"can't find faces in {fids}")
           e = np.stack([np.array([random.random()-0.5 for i in range(512)])])
           fh = iei.face_faiss_helper
           results = fh.search(e,k=5000)
    elif q and (cids := re.findall(r'^clip:(\d+)',q)):
       print(f"found a clip-like expression for {cids}")
       embs = [iei.get_openclip_embedding(e) for e in cids]
       emb = np.stack(embs) # type: ignore
       fh = iei.clip_faiss_helper 
       results = fh.search(emb,k=5000)
    elif q and (cids := re.findall(r'^randface:(\d+)',q)):
       random.seed(int(cids[0]))
       print(f"looking for random face with seed {cids}")
       e = np.stack([np.array([random.random()-0.5 for i in range(512)])])
       fh = iei.face_faiss_helper
       results = fh.search(e,k=5000)
    elif q and (cids := re.findall(r'^randclip:(\d+)',q)):
       random.seed(int(cids[0]))
       print(f"looking for random clip with seed {cids}")
       e = np.stack([np.array([random.random()-0.5 for i in range(512)])])
       fh = iei.face_faiss_helper
       results = fh.search(e,k=5000)
    elif q and (cids := re.findall(r'^txt:(.*)',q)):
       sql = "select img_id from "
       db  = iei.metadata_db
       sql = f"select img_id from img_meta_data where title like '%'||?||'%' limit 50"
       print(sql)
       ids = [row[0] for row in db.execute(sql,[cids[0]])]
       results = [SearchResults(imgids= ids,scores=[1 for _ in ids] )]
    elif q:
       emb = iei.ocw.txt_embeddings([q])
       fh = iei.clip_faiss_helper 
       results = fh.search(emb,k=5000)



    already_done=set()
    good_ids=[]
    good_scores=[]

    for result in results or []:
      for imgid,score in zip(result.imgids,result.scores):
         if imgid not in already_done:
            good_ids.append(imgid)
            good_scores.append(max(int(score*1000),-999))
            already_done.add(imgid)
      
    
    return SearchResults(imgids=good_ids, 
                         scores=good_scores)    

#####################################################################

class ImgModel(BaseModel):
    imgs: list[str] | None
class EmbModel(BaseModel):
    embs: list[list[float]] | None

@app.post("/insightface_analysis")
async def get_insightface_analysis(i: ImgModel):
    result = {
        'embs':[1,2,3],
    }
    return result

@app.post("/clip_img_embs")
async def get_clip_img_embs(i: ImgModel) -> EmbModel:
    print(i)
    embs = [[f*1.0 for f in [1,2,3]]]
    result = EmbModel(embs = embs)
    return result

@app.post("/clip_txt_embs")
async def get_clip_txt_embs(i: ImgModel):
    result = {
        'embs':[1,2,3],
    }    
    return result

# TODO - figure out how to give the user a progress bar
# and do this async
@app.get("/reindex")
async def reindex():
  result = iei.make_all_faiss_indexes()
  if iei.__dict__.get('clip_faiss_helper'):
     del iei.clip_faiss_helper
  if iei.__dict__.get('face_faiss_helper'):
     del iei.face_faiss_helper
  return result

@app.get("/reload")
async def reload():
  if iei.__dict__.get('clip_faiss_helper'):
     del iei.clip_faiss_helper
  if iei.__dict__.get('face_faiss_helper'):
     del iei.face_faiss_helper
  return {'status':'ok'}

#############################
from fastapi import FastAPI, Response

@app.get("/test")
async def test(img_id:Optional[int], 
               k:Optional[int]=400,
               t:Optional[str]='clip'):
    fh = None
    q: list[list[float] | np.ndarray] | None = None
    if t == 'face':
        ia = iei.get_insightface_analysis(img_id)
        if isinstance(ia,list):
            q = [x['embedding'] for x in ia]
            fh = iei.face_faiss_helper
        else:
           print(f"can't find faces in {img_id}")
           t = 'clip'

    if t == 'clip':    
        e = iei.get_openclip_embedding(img_id)
        if e is not None and e.any(): 
            q = [e]
        fh = iei.clip_faiss_helper 

    if not fh or not q:
       return """<div>nothing found</div>"""

    res = fh.search(np.stack(q),k or 5)
    #r3 = orjson.loads(orjson.dumps(res,option=orjson.OPT_SERIALIZE_NUMPY))
    
    
    results = []
    for a in res:
      for scr,idx in zip(a.scores,a.imgids):
            h = f"""<div>
                <img loading="lazy" src='/thm/{idx}'/><br>
                {scr:.2f}
                <a href="?t=face&img_id={idx}">☺</a>
                <a href="?t=clip&img_id={idx}">📷</a>
                </div>"""
            results.append(h)

    style = """
     <style>
       .box {display:flex; flex-wrap:wrap;}
       .box img {max-width:256px}
       .box>& {flex: 1 1 160px;}
       html {background-color: #333;}
     </style>
    """
     
    data = f"""
     <html>

     <ul>
     <li><a href="similar_images/1">similar images</a>
      <div class='box'>
       {"".join(results)}
      </div>
      {style}
     </html>
    """
    return Response(content=data, media_type="text/html")
