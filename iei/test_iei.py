import image_embedding_indexer
iei=image_embedding_indexer.ImageEmbeddingIndexer(device='cuda')
print(iei)

test_imgs = [
    (
        "https://live.staticflickr.com/4568/24119958367_69117845b1_b.jpg",
        "https://www.flickr.com/photos/105675854@N04/24119958367/",
        "cat",
    ),
    (
        "https://live.staticflickr.com/3440/3212455941_e0993930b1_c.jpg",
        "https://www.flickr.com/photos/kenlee/3212455941",
        "obama"
    )
     
   # "images/imagenet-r/n01443537/art_0.jpg",
    ]

for img_uri,src_uri,title in test_imgs:
    x = iei.preprocess_img(img_uri,src_uri,title,None,"{}")
    print(img_uri,x)

iei.make_all_faiss_indexes()