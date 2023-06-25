#!/usr/bin/env python
#
# see localhost:8000/docs


from typing import Optional, Union
from fastapi import FastAPI
import fastapi
import image_embedding_indexer

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

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}


import orjson
import io
import time
@app.get("/thm/{img_id}")
async def thm(img_id:int, size:int=400):
  hdrs = {'Cache-Control': 'public, max-age=0'}
  time.sleep(0.1)
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

from fastapi.responses import ORJSONResponse

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

from pydantic import BaseModel
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
    r3 = orjson.loads(orjson.dumps(res,option=orjson.OPT_SERIALIZE_NUMPY))
    
    results = []
    for a in r3:
      for scr,idx in a:
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
