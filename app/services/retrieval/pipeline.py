from app.core.config import settings
from app.services.retrieval.searcher import hybrid_search
from app.services.retrieval.fusion import fuse
from app.services.retrieval.assembler import assemble
from app.services.generation.rewriter import rewrite
from app.services.retrieval.reranker import rerank
from app.services.ingestion.embedder import embed_query, tokenize
from app.services.retrieval.cache import get_embedding, set_embedding
from app.services.retrieval.cache import set_retrieval, get_retrieval

async def retrieve(query: str, history: list[dict]) -> list[dict] | None:
    query = await rewrite(query, history)

    #L2 cache check
    query_vector = await get_embedding(query)
    if not query_vector:
        query_vector = await embed_query(query)
        await set_embedding(query, query_vector)

    query_tokens = tokenize(query)

    #L3 cache check
    retrieval_cache = await get_retrieval(query)

    if retrieval_cache:
        result = retrieval_cache

    else:
        dense, sparse = await hybrid_search(query_vector, query_tokens, top_k=settings.top_k_chunks)
        result = fuse(sparse_results=sparse, dense_results=dense,threshold=settings.retrieval_threshold)
    
        if not result:
            return None
        
        await set_retrieval(query, result)

    result = await rerank(query, result)
    
    return await assemble(result)