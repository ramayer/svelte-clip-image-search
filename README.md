# Image Embedding Indexer 

A platform for indexing images using a variety of embeddings (face, clip, text embeddings of captions, fine-tuning your own embeddings to better recognize your own family, pets, cars, etc), and using those tools to manipulate an image gallery.





## Installation

For small image collections, installing with docker and no Cuda/M1 acceleration is most convenient. 

### Installing From Source

\[Todo - try to remember what I had done here\]

Note that the requirements.txt file can be quite fragile, as different indexers may depend on conflicting versions of libraries; and those version depdencies may depend on the platform (cuda vs mac-m1).  On some platforms it seems to work with faiss_cpu==1.7.3 and clip==1.0; while on others it seems to prefer faiss=1.5.3 with clip==0.2.0.     If you want to update the requirements file with something that works on your platform, you might want to start with `pipreqs . --savepath=requirements.tmp`, but note that pipreqs makes mistakes --- it fails to get open-clip-torch.   You'll probably then need to mess with changing == signs to >= for some libraries.


### Docker

    docker buildx build -f Dockerfile.iei_ui -t iei-ui:latest  .
    docker buildx build -f Dockerfile.iei_api -t iei-api:latest  .

    
    docker network create iei-network

    docker run -d \
       -v /tmp/iei_index:/data/iei_index \
       -v /tmp/pics/storage_emulated_0:/data/images:ro \
       -p 0.0.0.0:8000:8000 \
       --network iei-network --name iei-api \
       iei-api:latest

    docker run -d -p 0.0.0.0:5173:5173 \
        --network iei-network --name iei-ui \
        iei-ui bash


### To index images:

    docker run -it \
        -v /tmp/iei_index:/data/iei_index \
        -v /tmp/pics/storage_emulated_0:/data/images:ro \
        iei-api  ./index_files.py -r /data/images

# IEI API server



### To index images:

    docker run -it -v /tmp/test.iei:/data/iei_index.iei -v /tmp/pics/storage_emulated_0:/data/images:ro iei-api ./index_files.py -r /data/images



Note that this package has some internally conflicting requirements, depending on the platform you run it on.  On some platforms it seems to work with faiss_cpu==1.7.3 and clip==1.0 ; while on others it seems to prefer faiss=1.5.3 with clip==0.2.0.   



