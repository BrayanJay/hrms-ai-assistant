from sentence_transformers import CrossEncoder

model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

async def rerank(query: str, chunks: list[dict]) -> list[dict]:
    scores = model.predict([(query, chunk["content"]) for chunk in chunks])

    ranked = sorted(zip(scores, chunks), key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in ranked]