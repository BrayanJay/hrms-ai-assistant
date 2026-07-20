import re

def build_citations(answer: str, context: list[dict]) -> list[dict]:
    citations = re.findall(r'\[(\d+)\]', answer)
    context_map = {c["citation"]: c for c in context}
    seen = set()
    result = []

    for N in citations:
        n = int(N)
        if n in seen or n not in context_map:
            continue
        seen.add(n)
        c = context_map[n]
        if c["type"] == "image":
            result.append({
                "citation": c["citation"],
                "type": c["type"],
                "image_bytes": c["image_bytes"]
            })
        else:
            result.append({
                "citation": c["citation"],
                "type": c["type"],
                "content": c["content"]
            })
    
    return result