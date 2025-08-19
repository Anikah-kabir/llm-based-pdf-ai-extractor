from typing import List, Dict, Optional
import weaviate
from weaviate.classes.config import Configure, Property, DataType, VectorDistances
from weaviate.classes.init import Auth
from weaviate.exceptions import WeaviateBaseError, WeaviateStartUpError

from app.core.config import get_settings
import math
import time
import logging

settings = get_settings()
CLASS_NAME = "PDFChunks"
logger = logging.getLogger(__name__)

def get_weaviate_client(max_retries: int = 3) -> weaviate.WeaviateClient:
    for attempt in range(max_retries):
        try:
            client_kwargs = {}
            if settings.weaviate_url.startswith("embedded:"):
                client_kwargs["url"] = settings.weaviate_url
            else:
                client_kwargs["cluster_url"] = settings.weaviate_url

            if settings.weaviate_api_key:
                client_kwargs["auth_credentials"] = Auth.api_key(settings.weaviate_api_key)
            
            additional_headers = {}
            if settings.use_ollama:
                additional_headers={
                    "X-Ollama-Api-Key": "ollama",
                    "X-Ollama-Base-Url": settings.ollama_host
                }
            elif settings.openai_api_key:
                additional_headers["X-OpenAI-Api-Key"]  = settings.openai_api_key

            if additional_headers:
                client_kwargs["headers"] = additional_headers

            #client_kwargs['use_grpc']=False
            client_kwargs['skip_init_checks']=True 
            print(client_kwargs);
            if settings.weaviate_url.startswith("embedded:"):
                client = weaviate.connect_to_local() 
            else:
                client = weaviate.connect_to_weaviate_cloud(**client_kwargs)

            if client.is_ready():
                logger.info("Successfully connected to Weaviate")
                return client
        except WeaviateStartUpError as e:
            logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff

def init_schema():
    client = get_weaviate_client()

    #if client.collections.exists(CLASS_NAME):
    #    client.collections.delete(CLASS_NAME)
    try:
        if not client.collections.exists("PDFChunks"):
            if settings.use_ollama:
                client.collections.create(
                    name=CLASS_NAME,
                    vector_config=Configure.Vectors.text2vec_ollama(
                        name="chunk_vector",
                        source_properties=["chunk"],
                        api_endpoint=settings.ollama_host,
                        model=settings.ollama_model
                    ),
                    properties=[
                        Property(name="chunk", data_type=DataType.TEXT),
                        Property(name="pdf_id", data_type=DataType.TEXT),
                        Property(name="doc_type", data_type=DataType.TEXT),
                        Property(name="filename", data_type=DataType.TEXT),
                        Property(name="page_no", data_type=DataType.INT),
                    ],
                    vector_index_config=Configure.VectorIndex.hnsw(
                        distance_metric=VectorDistances.COSINE
                    )
                )
            else:
                client.collections.create(
                    name=CLASS_NAME,
                    vector_config=Configure.Vectors.text2vec_openai(
                        name="chunk_vector",
                        source_properties=["chunk"],
                        model=settings.embedding_model,
                        dimensions=1024,
                        base_url="https://api.openai.com/v1",
                        vectorize_collection_name=True
                    ),
                    properties=[
                        Property(name="chunk", data_type=DataType.TEXT),
                        Property(name="pdf_id", data_type=DataType.TEXT),
                        Property(name="doc_type", data_type=DataType.TEXT),
                        Property(name="filename", data_type=DataType.TEXT),
                        Property(name="page_no", data_type=DataType.INT),
                    ],
                    vector_index_config=Configure.VectorIndex.hnsw(
                        distance_metric=VectorDistances.COSINE
                    )
                )
    except WeaviateBaseError as e:
        print(f"Schema creation failed: {e.message}")
        raise
    finally:
        client.close()

def store_pdf_in_weaviate(pdf_id: str, filename: str, chunks: List[Dict], doc_type: str):
    client = get_weaviate_client()
    coll = client.collections.get(CLASS_NAME)
    
    batch = []
    for chunk in chunks:
        batch.append({
            "pdf_id": pdf_id,
            "filename": filename,
            "doc_type": doc_type,
            "chunk_num": chunk["chunk_num"],
            "page_no": chunk["approx_page"],
            "content": chunk["content"],
            "metadata": {
                "char_count": chunk["char_count"],
                "word_count": chunk["word_count"],
                "has_tables": chunk["has_tables"],
                "has_figures": chunk["has_figures"],
                "llm_analysis": chunk.get("llm_analysis", {}),
                "processed": chunk.get("processed", False)
            }
        })
        
        # Insert in batches of 50
        if len(batch) >= 50:
            coll.data.insert_many(batch)
            batch = []
    
    if batch:
        coll.data.insert_many(batch)
    
    client.close()

def search_chunks(query: str, filters: list[tuple[str, str]] = None, limit: int = 6):
    import weaviate
    client = get_weaviate_client()
    coll = client.collections.get(CLASS_NAME)

    where_filter = None
    if filters:
        from weaviate.classes.query import Filter
        f_objs = []
        for key, val in filters:
            f_objs.append(Filter.by_property(key).equal(val))
        if len(f_objs) > 1:
            from functools import reduce
            where_filter = reduce(lambda a, b: a & b, f_objs)
        else:
            where_filter = f_objs[0]

    res = coll.query.near_text(query=query, limit=limit, filters=where_filter)
    hits = [
        {
            "chunk": o.properties.get("chunk"),
            "pdf_id": o.properties.get("pdf_id"),
            "doc_type": o.properties.get("doc_type"),
            "filename": o.properties.get("filename"),
            "page_no": o.properties.get("page_no")
        }
        for o in res.objects
    ]
    client.close()
    return hits


