from app.core.logging import get_logger

logger = get_logger(__name__)

def fuse(dense_results: list, sparse_results: list, threshold: float) -> list[dict]:
    scores = {}

    for rank, result in enumerate(dense_results):
        scores[result.id] = {"score": 1/(rank+60), "payload": result.payload}

    for rank, result in enumerate(sparse_results):
        if result.id in scores:
            scores[result.id]["score"] += 1/(rank+60)
        else:
            scores[result.id] = {"score": 1/(rank+60), "payload": result.payload}

    sorted_results = sorted(scores.values(), key=lambda x: x["score"], reverse=True)

    logger.debug("RRF fusion complete", extra={
        "total": len(sorted_results),
        "above_threshold": sum(1 for r in sorted_results if r["score"] >= threshold),
        "threshold": threshold,
        "scores": [
            {"chunk_id": r["payload"].get("chunk_id"), "score": round(r["score"], 6), "above_threshold": r["score"] >= threshold}
            for r in sorted_results
        ],
    })

    return [r["payload"] for r in sorted_results if r["score"] >= threshold]