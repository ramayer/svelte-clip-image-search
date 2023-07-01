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
from typing import Optional, Union
from fastapi import FastAPI
from pydantic import BaseModel

import fastapi
import image_embedding_indexer

from fastapi.responses import ORJSONResponse
from fastapi.responses import RedirectResponse


print("Starting")

iei = image_embedding_indexer.ImageEmbeddingIndexer("./data/image_embedding_indexes")
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
async def thm(img_id:int, size:int=400):
  hdrs = {'Cache-Control': 'public, max-age=300'}
  debug_no_cache_hdrs = {
     'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0',
    }
  #time.sleep(0.02)
  if thm := iei.get_thm(img_id):
    buf = io.BytesIO()
    thm.save(buf,format="WebP",quality=50)
    return fastapi.Response(content = buf.getvalue(), headers = hdrs, media_type="image/webp")
  else:
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
  print(clip_emb.dtype)
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

@app.get("/search")
async def search(q: Optional[str] = None, iid: Optional[int] = None, type: Optional[str] = None):
    # Process the parameters and generate response data
    # Replace this with your actual implementation
    results = None
    if q:
       emb = iei.ocw.txt_embeddings([q])
       fh = iei.clip_faiss_helper 
       results = fh.search(emb,k=5000)
    if results:
        response_data = SearchResults(imgids=results[0].imgids, 
                                      scores=[max(int(s*1000),-999) for s in results[0].scores])
        return response_data
    

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

#############################
from fastapi import FastAPI, Response

@app.get("/test")
async def test(img_id:Optional[int], 
               k:Optional[int]=400,
               t:Optional[str]='clip'):
    fh = None
    q: list[list[float] | np.ndarray] | None = None
    if t == 'face':
        print(img_id)
        ia = iei.get_insightface_analysis(img_id)
        print("here ia is ",ia)
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
