from app.core.config import settings

threshold = settings.threshold

def chunk_document(doc_id: str, parsed: dict) -> list[dict]:
    text_content = parsed["text_contents"]
    table_content = parsed["table_contents"]
    image_content = parsed["image_contents"]
    current_group = []
    groups = []
    for idx, content in enumerate(text_content):
        current_group.append(content)
        if idx < len(text_content) - 1:
            if text_content[idx]["y_pos"] - text_content[idx+1]["y_pos"] > threshold:
                _build_text_chunks(doc_id, current_group, groups)
                current_group = []
            
    _build_text_chunks(doc_id, current_group, groups)
        

    for table in table_content:
        table_chunk = {
            "chunk_id": f"{doc_id}_p{table["page"]}_g{len(groups)}",
            "type": "table",
            "parent_chunk_id": None,
            "content": table["markdown"],
            "image_bytes": None
        }
        groups.append(table_chunk)

    for image in image_content:
        image_chunk = {
            "chunk_id": f"{doc_id}_p{image["page"]}_g{len(groups)}",
            "type": "image",
            "parent_chunk_id": None,
            "content": "",
            "image_bytes": image["bytes"]
        }
        groups.append(image_chunk)

    return groups

def _build_text_chunks(doc_id: str, group: list, groups: list) -> None:
    parent_chunk = {
        "chunk_id": f"{doc_id}_p{group[-1]['page']}_g{len(groups)}",
        "type": "text",
        "parent_chunk_id": None,
        "content": " ".join([b["text"] for b in group]),
        "image_bytes": None
    }
    groups.append(parent_chunk)

    words = parent_chunk["content"].split()
    for i in range(0, len(words), settings.child_threshold):
        groups.append({
            "chunk_id": f"{parent_chunk['chunk_id']}_c{i}",
            "parent_chunk_id": parent_chunk["chunk_id"],
            "type": "text",
            "content": " ".join(words[i:i+settings.child_threshold]),
            "image_bytes": None
        })