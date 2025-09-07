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
            
            headers = {
                "X-OpenAI-Api-Key":settings.openai_api_key
            }
            client = weaviate.connect_to_local(
                #auth_credentials=Auth.api_key(settings.weaviate_api_key),
                host="weaviate", 
                grpc_port=50051, 
                port=8080, 
                headers= headers
                ) 

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
                        source_properties=["content"],
                        api_endpoint=settings.ollama_host,
                        model=settings.ollama_model,
                        vector_index_config=Configure.VectorIndex.hnsw(
                            distance_metric=VectorDistances.COSINE
                        )
                    ),
                    properties=[
                        Property(name="pdf_id", data_type=DataType.TEXT),
                        Property(name="filename", data_type=DataType.TEXT),
                        Property(name="doc_type", data_type=DataType.TEXT),
                        Property(name="chunk_num", data_type=DataType.INT),
                        Property(name="page_no", data_type=DataType.INT),
                        Property(name="content", data_type=DataType.TEXT),
                        Property(
                            name="chunk_meta",
                            data_type=DataType.OBJECT,
                            nested_properties=[
                                Property(name="char_count", data_type=DataType.INT),
                                Property(name="word_count", data_type=DataType.INT),
                                Property(name="has_tables", data_type=DataType.BOOL),
                                Property(name="has_figures", data_type=DataType.BOOL),
                                Property(name="llm_analysis", data_type=DataType.TEXT),
                                Property(name="processed", data_type=DataType.BOOL),
                            ],
                        ),
                    ],
                )
            else:
                client.collections.create(
                    name=CLASS_NAME,
                    vector_config=Configure.Vectors.text2vec_openai(
                        name="chunk_vector",
                        source_properties=["content"],
                        model=settings.embedding_model,
                        dimensions=1536,
                        base_url="https://api.openai.com/v1",
                        vectorize_collection_name=True,
                        vector_index_config=Configure.VectorIndex.hnsw(
                            distance_metric=VectorDistances.COSINE
                        )
                    ),
                    properties=[
                        Property(name="pdf_id", data_type=DataType.TEXT),
                        Property(name="filename", data_type=DataType.TEXT),
                        Property(name="doc_type", data_type=DataType.TEXT),
                        Property(name="chunk_num", data_type=DataType.INT),
                        Property(name="page_no", data_type=DataType.INT),
                        Property(name="content", data_type=DataType.TEXT),
                        Property(
                            name="chunk_meta",
                            data_type=DataType.OBJECT,
                            nested_properties=[
                                Property(name="char_count", data_type=DataType.INT),
                                Property(name="word_count", data_type=DataType.INT),
                                Property(name="has_tables", data_type=DataType.BOOL),
                                Property(name="has_figures", data_type=DataType.BOOL),
                                Property(name="llm_analysis", data_type=DataType.TEXT),
                                Property(name="processed", data_type=DataType.BOOL),
                            ],
                        ),
                    ],
                )
    except WeaviateBaseError as e:
        print(f"Schema creation failed: {e.message}")
        raise
    finally:
        client.close()

def store_pdf_in_weaviate(pdf_id: str, filename: str, chunks: List[Dict], doc_type: str):
    client = get_weaviate_client()
    if client is None:
        return
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
            "chunk_meta": {
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
            try:
                coll.data.insert_many(batch)
                batch = []
            except Exception as e:
                logging.error(f"Batch insert failed: {e}")
                batch = []  # Reset batch
    
    if batch:
        try:
            coll.data.insert_many(batch)
        except Exception as e:
            logging.error(f"Final batch insert failed: {e}")   
    client.close()
    
def search_chunks(query: str, filters: list[tuple[str, str]] = None, limit: int = 6):
    import weaviate
    from weaviate.classes.query import Filter
    from weaviate.exceptions import WeaviateQueryError
    import logging
    
    client = get_weaviate_client()
    coll = client.collections.get(CLASS_NAME)

    where_filter = None
    if filters:
        try:
            # Build filter using AND condition for all filters
            filter_conditions = []
            for key, val in filters:
                filter_conditions.append(Filter.by_property(key).equal(val))
            
            if filter_conditions:
                # Combine all filters with AND
                where_filter = Filter.all_of(*filter_conditions)
                
        except Exception as e:
            logging.error(f"Error building Weaviate filter: {e}")
            # Fallback: use first filter only
            if filter_conditions:
                where_filter = filter_conditions[0]

    try:
        # Use HTTP instead of GRPC if GRPC is having issues
        # res = coll.query.near_text(query=query, limit=limit, filters=where_filter)
        
        # Alternative: Use hybrid search which might be more stable
        res = coll.query.hybrid(
            query=query,
            limit=limit,
            filters=where_filter,
            alpha=0.75  # Balance between keyword and vector search
        )
        
        hits = [
            {
                "content": o.properties.get("content"),
                "pdf_id": o.properties.get("pdf_id"),
                "doc_type": o.properties.get("doc_type"),
                "filename": o.properties.get("filename"),
                "page_no": o.properties.get("page_no"),
                "score": o.metadata.score if hasattr(o, 'metadata') else None
            }
            for o in res.objects
        ]
        return hits
        
    except WeaviateQueryError as e:
        logging.error(f"Weaviate query error: {e}")
        # Fallback to simple text search
        try:
            res = coll.query.bm25(
                query=query,
                limit=limit,
                filters=where_filter
            )
            hits = [
                {
                    "content": o.properties.get("content"),
                    "pdf_id": o.properties.get("pdf_id"),
                    "doc_type": o.properties.get("doc_type"),
                    "filename": o.properties.get("filename"),
                    "page_no": o.properties.get("page_no"),
                    "score": o.metadata.score if hasattr(o, 'metadata') else None
                }
                for o in res.objects
            ]
            return hits
        except Exception as fallback_error:
            logging.error(f"Fallback search also failed: {fallback_error}")
            return []
    except Exception as e:
        logging.error(f"Unexpected error in search: {e}")
        return []
    finally:
        try:
            client.close()
        except:
            pass


