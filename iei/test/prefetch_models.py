#!/bin/env python
#
# The docker build step that downloads models
# can be extremely slow.
#
# Use a tiny prefetcher near the beginning
# of the docker build chain of commands
# to minimize how often we need to repeat this.

import os
import open_clip
import torch
from insightface.app import FaceAnalysis
from PIL import Image

device = torch.cuda.is_available() and 'cuda' or 'cpu'

# download the face models
fa = FaceAnalysis(ctx_id=0, providers=['CUDAExecutionProvider',
                                       'CPUExecutionProvider'])

fa.prepare(ctx_id=0, det_size=(640,640))


clip_model_nam = os.getenv("CLIP_MODEL",'ViT-B-32-quickgelu')
clip_model_pre = os.getenv("CLIP_PRETRAINED",'laion400m_e32')
m,c,p = open_clip.create_model_and_transforms(clip_model_nam, 
                                              pretrained=clip_model_pre,
                                              device=device
                                              )
