from app.core.config import settings
from app.services.retrieval.searcher import hybrid_search
from app.services.retrieval.fusion import fuse
from app.services.retrieval.assembler import assemble

async def retrieve(query: str) -> list[dict] | None:
    dense, sparse = await hybrid_search(query=query, top_k=settings.top_k_chunks)
    result = fuse(sparse_results=sparse, dense_results=dense,threshold=settings.retrieval_threshold)

    if not result:
        return None
    
    return await assemble(result)