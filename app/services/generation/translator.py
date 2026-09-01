from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_LANG_NAMES = {
    "si": "Sinhala",
    "ta": "Tamil",
}
_SUPPORTED_LANGUAGES = set(_LANG_NAMES.keys())

# Dedicated OpenAI client for translation — always hits OpenAI regardless of LLM env
_translation_client = AsyncOpenAI(
    api_key=settings.openai_api_key,
    base_url="https://api.openai.com/v1",
)

_FROM_ENGLISH_SYSTEM_PROMPT = """\
You are a professional translator specializing in HR and business documents \
for a Sri Lankan corporate environment.

Rules:
- Preserve ALL Markdown formatting exactly: **, ##, ###, ---, bullet points, tables
- Preserve all numbers, dates, and codes exactly as they appear
- Only translate natural language words — never translate Markdown symbols
- Use formal, professional language appropriate for a corporate HR system
- Apply correct HR terminology:

  Sinhala:
    Annual Leave     = වාර්ෂික නිවාඩු
    Sick Leave       = රෝග නිවාඩු
    Casual Leave     = සාමාන්‍ය නිවාඩු
    Short Leave      = කෙටි නිවාඩු
    Balance          = ශේෂය
    Available        = ලබාගත හැකි
    Used             = භාවිතා කළ
    Pending          = රැඳී ඇති
    Entitled         = හිමිකම
    Approved         = අනුමත
    Remaining        = ඉතිරි

  Tamil:
    Annual Leave     = ஆண்டு விடுப்பு
    Sick Leave       = நோய் விடுப்பு
    Casual Leave     = சாதாரண விடுப்பு
    Short Leave      = குறுகிய விடுப்பு
    Balance          = இருப்பு
    Available        = கிடைக்கக்கூடிய
    Used             = பயன்படுத்திய
    Pending          = நிலுவையில் உள்ள
    Entitled         = உரிமையுள்ள
    Approved         = அங்கீகரிக்கப்பட்ட
    Remaining        = மீதமுள்ள

Return ONLY the translated text. Do not add explanations or notes.\
"""

_TO_ENGLISH_SYSTEM_PROMPT = """\
Translate the following text to English.
Return only the translated text, nothing else.\
"""


async def to_english(text: str, source_language: str) -> str:
    if source_language not in _SUPPORTED_LANGUAGES:
        return text
    try:
        response = await _translation_client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": _TO_ENGLISH_SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            max_tokens=256,
            temperature=0.1,
        )
        translated = response.choices[0].message.content
        logger.info("translated query to English", extra={"source_lang": source_language})
        return translated
    except Exception as exc:
        logger.warning("query translation failed — using original", extra={"lang": source_language, "error": str(exc)})
        return text


async def from_english(text: str, target_language: str) -> str:
    if target_language not in _SUPPORTED_LANGUAGES:
        return text
    lang_name = _LANG_NAMES[target_language]
    try:
        response = await _translation_client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": _FROM_ENGLISH_SYSTEM_PROMPT},
                {"role": "user", "content": f"Translate the following to {lang_name}:\n\n{text}"},
            ],
            max_tokens=1024,
            temperature=0.1,
        )
        translated = response.choices[0].message.content
        logger.info("translated response from English", extra={"target_lang": target_language})
        return translated
    except Exception as exc:
        logger.warning("response translation failed — returning English", extra={"lang": target_language, "error": str(exc)})
        return text
