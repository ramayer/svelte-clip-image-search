#!/usr/bin/env python
from typing import Optional, Union
from fastapi import FastAPI
import fastapi
import image_functions

iei = image_functions.ImageEmbeddingIndexer("../data/image_embedding_indexes")

app = FastAPI()

hdrs = {'Cache-Control': f'public, max-age={60*60*24*365}'}
hdrs = {'Cache-Control': f'public, max-age={60*5}'}


#####################################################################
#
#####################################################################

@app.get("/")
def home():
    return {"Hello": "World"}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}


import orjson
import io
@app.get("/thm/{img_id}")
async def thm(img_id:int, size:Optional[int]=400):
  hdrs = {'Cache-Control': 'public, max-age=172800'}
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
  hdrs = {'Cache-Control': 'public, max-age=172800'}
  response.headers.update(hdrs)
  print(f"here response headers is {response.headers}")
  query = iei.get_openclip_embedding(img_id)
  res = iei.clip_faiss_helper.search(np.stack([query]),k or 400)
  r3 = orjson.loads(orjson.dumps(res,option=orjson.OPT_SERIALIZE_NUMPY))
  return r3

@app.get("/clip_img_emb/{img_id}")
async def clip_img_emb(img_id:int, size:Optional[int]=400)-> list[float]:
  hdrs = {'Cache-Control': 'public, max-age=172800'}
  res = iei.get_openclip_embedding(img_id)
  return res.tolist()

import numpy as np
@app.get("/insightface_analysis/{img_id}")
async def clip_img_emb(img_id:int, size:Optional[int]=400):
  hdrs = {'Cache-Control': 'public, max-age=172800'}
  res = iei.get_insightface_analysis(img_id)
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
def get_insightface_analysis(i: ImgModel):
    result = {
        'embs':[1,2,3],
    }
    return result

@app.post("/clip_img_embs")
def get_clip_img_embs(i: ImgModel) -> EmbModel:
    print(i)
    embs = [[f*1.0 for f in [1,2,3]]]
    result = EmbModel(embs = embs)
    return result

@app.post("/clip_txt_embs")
def get_clip_txt_embs(i: ImgModel):
    result = {
        'embs':[1,2,3],
    }    
    return result

#############################
from fastapi import FastAPI, Response

@app.get("/debug_html_page/{img_id}")
def debug_html_page(img_id:int, k:Optional[int]=400, t:Optional[str]='clip'):

    if t == 'clip':    
        query = [iei.get_openclip_embedding(img_id)]
        fh = iei.clip_faiss_helper 
    else:
        ia = iei.get_insightface_analysis(img_id)
        if isinstance(ia,list):
            query = [x['embedding'] for x in ia]
            fh = iei.face_faiss_helper
        else:
            print("Yipes")
            query = [iei.get_openclip_embedding(img_id)]
            fh = iei.clip_faiss_helper 

    res = fh.search(np.stack(query),k or 5)
    r3 = orjson.loads(orjson.dumps(res,option=orjson.OPT_SERIALIZE_NUMPY))
    
    results = []
    for a in r3:
      for scr,idx in a:
            h = f"""<div>
                <img loading="lazy" src='/thm/{idx}'/><br>
                {scr:.2f}
                <a href="{idx}?t=face">☺</a>
                <a href="{idx}?t=clip">📷</a>
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
     
    data = f"""<html>
    <body>Hello</body>
    <div class='box'>
    {"".join(results)}
    </div>
    {style}
    </html>
        """
    return Response(content=data, media_type="text/html")
