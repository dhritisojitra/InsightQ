"""LLM service supporting both Gemini and Groq APIs dynamically with JSON mode support."""

import json
import re
import time
from functools import lru_cache

import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, TooManyRequests
from groq import Groq, RateLimitError

from app.config import get_settings
from app.utils.logger import logger


def _get_llm_provider() -> str:
    """Determine the LLM provider based on configured API keys.
    Returns 'gemini', 'groq', or raises EnvironmentError.
    """
    settings = get_settings()
    
    # Check Gemini API Key
    has_gemini = settings.gemini_api_key and not settings.gemini_api_key.startswith("your_gemini")
    
    # Check Groq API Key
    has_groq = settings.groq_api_key and not settings.groq_api_key.startswith("your_groq")
    
    if has_gemini:
        return "gemini"
    elif has_groq:
        return "groq"
    
    raise EnvironmentError(
        "Neither GEMINI_API_KEY nor GROQ_API_KEY is configured in your .env file."
    )


def _call_gemini(prompt: str, temperature: float = 0.3, use_json: bool = False) -> str:
    """Send prompt to Gemini with exponential backoff on rate limits."""
    settings = get_settings()
    genai.configure(api_key=settings.gemini_api_key)
    model_name = settings.gemini_model or "gemini-3.5-flash"
    model = genai.GenerativeModel(model_name)
    
    max_retries = 4
    for attempt in range(max_retries):
        try:
            config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=4096,
                response_mime_type="application/json" if use_json else None
            )
            response = model.generate_content(
                prompt,
                generation_config=config,
            )
            return response.text.strip()
        except (ResourceExhausted, TooManyRequests) as e:
            wait = 2 ** attempt * 5  # 5s, 10s, 20s, 40s
            if attempt < max_retries - 1:
                logger.warning(f"Gemini Rate limited (429). Retrying in {wait}s... (attempt {attempt+1}/{max_retries})")
                time.sleep(wait)
            else:
                raise RuntimeError(
                    "Gemini API rate limit reached. Please wait a minute and try again."
                ) from e
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise


def _call_groq(prompt: str, temperature: float = 0.3, use_json: bool = False) -> str:
    """Send prompt to Groq with exponential backoff on rate limits."""
    settings = get_settings()
    client = Groq(api_key=settings.groq_api_key)
    model_name = settings.groq_model or "llama-3.3-70b-versatile"
    
    max_retries = 4
    for attempt in range(max_retries):
        try:
            response_format = {"type": "json_object"} if use_json else None
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=4096,
                response_format=response_format
            )
            return response.choices[0].message.content.strip()
        except RateLimitError as e:
            wait = 2 ** attempt * 5  # 5s, 10s, 20s, 40s
            if attempt < max_retries - 1:
                logger.warning(f"Groq Rate limited. Retrying in {wait}s... (attempt {attempt+1}/{max_retries})")
                time.sleep(wait)
            else:
                raise RuntimeError(
                    "Groq API rate limit reached. Please wait a minute and try again."
                ) from e
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise


def _call_llm(prompt: str, temperature: float = 0.3, use_json: bool = False) -> str:
    """Dispatch LLM call to configured provider (Gemini or Groq)."""
    provider = _get_llm_provider()
    if provider == "gemini":
        return _call_gemini(prompt, temperature, use_json)
    else:
        return _call_groq(prompt, temperature, use_json)


def repair_json_braces(s: str) -> str:
    """Remove orphan closing braces/brackets from a JSON string."""
    result = []
    in_string = False
    escape = False
    curly_count = 0
    bracket_count = 0
    
    for char in s:
        if in_string:
            if escape:
                escape = False
            elif char == '\\':
                escape = True
            elif char == '"':
                in_string = False
            result.append(char)
        else:
            if char == '"':
                in_string = True
                result.append(char)
            elif char == '{':
                curly_count += 1
                result.append(char)
            elif char == '}':
                if curly_count > 0:
                    curly_count -= 1
                    result.append(char)
                else:
                    # Discard orphan closing curly brace
                    pass
            elif char == '[':
                bracket_count += 1
                result.append(char)
            elif char == ']':
                if bracket_count > 0:
                    bracket_count -= 1
                    result.append(char)
                else:
                    # Discard orphan closing square bracket
                    pass
            else:
                result.append(char)
                
    return "".join(result)


def _parse_json_list(raw: str) -> list:
    """Robustly parse a JSON list from raw LLM output."""
    raw = raw.strip()
    raw = re.sub(r"^```json\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"^```\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    start_idx = raw.find('[')
    end_idx = raw.rfind(']')
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        json_str = raw[start_idx:end_idx + 1]
    else:
        json_str = raw

    # Repair orphan braces/brackets
    json_str = repair_json_braces(json_str)

    # Clean trailing commas in objects or arrays
    json_str = re.sub(r",\s*([\]}])", r"\1", json_str)
    
    return json.loads(json_str)


def _parse_json_dict(raw: str) -> dict:
    """Robustly parse a JSON dictionary from raw LLM output."""
    raw = raw.strip()
    raw = re.sub(r"^```json\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"^```\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    start_idx = raw.find('{')
    end_idx = raw.rfind('}')
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        json_str = raw[start_idx:end_idx + 1]
    else:
        json_str = raw

    # Repair orphan braces/brackets
    json_str = repair_json_braces(json_str)

    # Clean trailing commas in objects or arrays
    json_str = re.sub(r",\s*([\]}])", r"\1", json_str)
    
    return json.loads(json_str)


def generate_rag_answer(question: str, context_chunks: list[dict]) -> str:
    """Generate an answer using RAG context chunks."""
    context_text = "\n\n".join(
        f"[Source: {c['filename']}, Page {c['page_number']}]\n{c['text']}"
        for c in context_chunks
    )

    prompt = f"""You are a helpful academic assistant. Use ONLY the provided context to answer the question.
If the answer cannot be found in the context, say "I couldn't find this in the uploaded document."

When citing information, reference the source page as [Page X].

CONTEXT:
{context_text}

QUESTION: {question}

ANSWER (be thorough but concise, cite page numbers inline):"""

    return _call_llm(prompt, temperature=0.2, use_json=False)


def generate_document_summary(full_text: str, filename: str) -> dict:
    """Generate a structured summary for a document."""
    words = full_text.split()
    truncated = " ".join(words[:4000]) if len(words) > 4000 else full_text

    prompt = f"""You are an academic summarizer. Analyze the following document excerpt from "{filename}" and produce:

1. A clear, comprehensive summary (3-5 paragraphs) covering the main ideas, findings, and conclusions.
2. A list of 5-8 key topics/concepts covered.

Respond ONLY with valid JSON in this exact format:
{{
  "summary": "...",
  "key_topics": ["topic1", "topic2", ...]
}}

DOCUMENT:
{truncated}"""

    raw = _call_llm(prompt, temperature=0.3, use_json=True)
    try:
        return _parse_json_dict(raw)
    except Exception as e:
        logger.error(f"Failed to parse summary JSON. Raw: {raw}. Error: {e}")
        return {"summary": raw, "key_topics": []}


def generate_suggested_questions(summary: str, filename: str) -> list[str]:
    """Generate 5 suggested questions based on a document summary."""
    prompt = f"""Based on the following summary of "{filename}", generate exactly 5 insightful questions a student might ask about this document.

Return ONLY a JSON array of 5 question strings, no other text:
["question1", "question2", "question3", "question4", "question5"]

SUMMARY:
{summary}"""

    raw = _call_llm(prompt, temperature=0.5, use_json=True)
    try:
        questions = _parse_json_list(raw)
        return [q for q in questions if isinstance(q, str)][:5]
    except Exception as e:
        logger.error(f"Failed to parse suggested questions JSON. Raw: {raw}. Error: {e}")
        return []


def generate_mcqs(context_chunks: list[dict], num_questions: int, difficulty: str) -> list[dict]:
    """Generate multiple-choice questions from retrieved chunks."""
    context_text = "\n\n".join(
        f"[Page {c['page_number']}] {c['text']}" for c in context_chunks
    )

    prompt = f"""You are an expert academic quiz creator. Based on the following content, create exactly {num_questions} multiple-choice questions at {difficulty} difficulty.

Rules:
- Each question must have exactly 4 options labeled A, B, C, D
- Indicate the correct answer
- Provide a brief explanation
- Include the source page number when relevant
- IMPORTANT: Use single quotes for all string literals inside query expressions (e.g. use 'Male' instead of "Male") to prevent JSON validation conflicts.
- IMPORTANT: Return ONLY a valid JSON array, do not include any trailing commas, comments, or extra text.

Return ONLY valid JSON as an array of objects:
[
  {{
    "question": "...",
    "options": [
      {{"label": "A", "text": "..."}},
      {{"label": "B", "text": "..."}},
      {{"label": "C", "text": "..."}},
      {{"label": "D", "text": "..."}}
    ],
    "correct_answer": "A",
    "explanation": "...",
    "source_page": 1
  }}
]

CONTENT:
{context_text}"""

    raw = _call_llm(prompt, temperature=0.4, use_json=True)
    try:
        return _parse_json_list(raw)
    except Exception as e:
        logger.error(f"Failed to parse MCQ JSON. Raw: {raw}. Error: {e}")
        raise RuntimeError(f"LLM generated invalid JSON formatting for MCQs: {e}")


def check_llm_available() -> bool:
    """Quick check that at least one LLM is configured."""
    try:
        _get_llm_provider()
        return True
    except EnvironmentError:
        return False
