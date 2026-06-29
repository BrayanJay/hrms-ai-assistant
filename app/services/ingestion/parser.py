from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
import asyncio
import io

pipeline_options = PdfPipelineOptions()
pipeline_options.generate_picture_images = True

converter = DocumentConverter( format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)})

async def parse_document(file_path: str) -> dict:
    result = await asyncio.to_thread(converter.convert, file_path)

    text_blocks = []
    tables = []
    images = []

    for item in result.document.texts:
        text_blocks.append({"text": item.text, "page": item.prov[0].page_no, "y_pos": item.prov[0].bbox.t})
    
    for item in result.document.tables:
        tables.append({"markdown": item.export_to_markdown(doc=result.document), "page": item.prov[0].page_no, "y_pos": item.prov[0].bbox.t})
    
    for item in result.document.pictures:
        if item.image and item.image.pil_image:
            buf = io.BytesIO()
            item.image.pil_image.save(buf, format="PNG")
            image_bytes = buf.getvalue()
        else:
            image_bytes = None

        images.append({"bytes": image_bytes, "page": item.prov[0].page_no, "y_pos": item.prov[0].bbox.t})

    return {"text_contents": text_blocks, "table_contents": tables, "image_contents": images}