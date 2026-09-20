#!/usr/bin/env python3

import json
import os
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai


INPUT_FILE = Path("../txt/raw.txt")
OUTPUT_FILE = Path("../json/content.json")

# Gemini model is configured in .env.
# Example: GEMINI_MODEL=gemini-3.8-flash
MAX_ATTEMPTS_PER_MODEL = 2
RETRY_BASE_SECONDS = 2

INTRO_CREDIT = ""
BACKGROUND_COLOR = "#0C0B09"

CONCLUSION_TEXT = "Explore Tolkien’s Legendarium"
CONCLUSION_DESCRIPTION = "Search the places, peoples, and stories of Middle-earth."
CONCLUSION_CTA = "Visit the-legendarium-companion.com"

PROMPT = r"""
Transform the supplied raw QUESTION and ANSWER into the final JSON
structure for an Instagram carousel.

The output must contain exactly one top-level key: "slides".

STRUCTURE:

{
  "slides": [
    {
      "text": "QUESTION",
      "credit": "",
      "intro": {
        "header": {
          "background": true,
          "background_color": "#0C0B09"
        },
        "question": {
          "background": true,
          "background_color": "#0C0B09"
        },
        "credit": {
          "background": true,
          "background_color": "#0C0B09"
        }
      }
    },
    {
      "text": "ANSWER ENTRY",
      "credit": ""
    },
    {
      "text": "Explore Tolkien’s Legendarium",
      "description": "Search the places, peoples, and stories of Middle-earth.",
      "cta": "Visit the-legendarium-companion.com",
      "credit": "",
      "conclusion": {
        "header": {
          "background": true,
          "background_color": "#0C0B09"
        },
        "question": {
          "background": true,
          "background_color": "#0C0B09"
        },
        "credit": {
          "background": true,
          "background_color": "#0C0B09"
        }
      }
    }
  ]
}

RULES:

1. Copy the QUESTION into the first slide's "text".
2. The first slide must use an empty string "" as its credit.
3. The first slide must contain the complete "intro" object exactly as specified.
4. Split the ANSWER into logical individual entries.
5. Each logical answer entry becomes one slide.
6. Preserve the supplied answer wording and meaning as much as possible.
7. Do not add Tolkien lore, facts, sources, or claims.
8. Do not fact-check the supplied answer.
9. Use an empty string "" for the "credit" field unless a credit is explicitly supplied in the raw material.
10. Answer slides must contain only "text" and "credit".
11. Do not add "intro" to answer slides.
12. The final slide must be the conclusion slide.
13. The conclusion slide must contain exactly "text", "description", "cta", "credit", and "conclusion".
14. The conclusion text, description, and CTA must use the supplied values exactly.
15. The conclusion object must match the specified structure exactly.
16. Do not add any other keys.
17. Return only valid JSON. No Markdown fences or commentary.
"""



def read_raw_file():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"{INPUT_FILE} was not found.")

    content = INPUT_FILE.read_text(encoding="utf-8").strip()

    if not content:
        raise ValueError(f"{INPUT_FILE} is empty.")

    return content


def extract_json(text):
    text = text.strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(r"\s*```$", "", text)

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("Gemini did not return a JSON object.")

    return text[start:end + 1]


def normalize_content(data):
    """
    Normalize the final slide so fixed carousel metadata is always generated
    by Python rather than depending on Gemini to reproduce it exactly.
    """

    if not isinstance(data, dict) or "slides" not in data:
        return data

    slides = data["slides"]

    if not isinstance(slides, list) or not slides:
        return data

    # Gemini should generate the question and answer slides.
    # The conclusion is fixed application metadata, so replace any
    # Gemini-generated final slide with the canonical structure.
    conclusion_credit = ""
    if isinstance(slides[-1], dict):
        conclusion_credit = slides[-1].get("credit", "")

    slides[-1] = {
        "text": CONCLUSION_TEXT,
        "description": CONCLUSION_DESCRIPTION,
        "cta": CONCLUSION_CTA,
        "credit": conclusion_credit if isinstance(conclusion_credit, str) else "",
        "conclusion": {
            "header": {
                "background": True,
                "background_color": BACKGROUND_COLOR,
            },
            "question": {
                "background": True,
                "background_color": BACKGROUND_COLOR,
            },
            "credit": {
                "background": True,
                "background_color": BACKGROUND_COLOR,
            },
        },
    }

    return data


def validate_content(data):
    if not isinstance(data, dict):
        raise ValueError("Gemini output is not a JSON object.")

    if set(data.keys()) != {"slides"}:
        raise ValueError("Output must contain exactly the 'slides' key.")

    slides = data["slides"]

    if not isinstance(slides, list) or len(slides) < 2:
        raise ValueError(
            "'slides' must contain at least an intro and conclusion slide."
        )

    intro = slides[0]

    if set(intro.keys()) != {"text", "credit", "intro"}:
        raise ValueError(
            "The first slide must contain exactly "
            "'text', 'credit', and 'intro'."
        )

    if not isinstance(intro["text"], str) or not intro["text"].strip():
        raise ValueError("Intro slide text cannot be empty.")

    if intro["credit"] != INTRO_CREDIT:
        raise ValueError(f"Intro credit must be '{INTRO_CREDIT}'.")

    expected_style = {
        "header": {
            "background": True,
            "background_color": BACKGROUND_COLOR,
        },
        "question": {
            "background": True,
            "background_color": BACKGROUND_COLOR,
        },
        "credit": {
            "background": True,
            "background_color": BACKGROUND_COLOR,
        },
    }

    if intro["intro"] != expected_style:
        raise ValueError("Invalid intro configuration.")

    conclusion = slides[-1]

    if set(conclusion.keys()) != {
        "text",
        "description",
        "cta",
        "credit",
        "conclusion",
    }:
        raise ValueError(
            "The final slide must contain exactly "
            "'text', 'description', 'cta', 'credit', and 'conclusion'."
        )

    if conclusion["text"] != CONCLUSION_TEXT:
        raise ValueError("Invalid conclusion text.")

    if conclusion["description"] != CONCLUSION_DESCRIPTION:
        raise ValueError("Invalid conclusion description.")

    if conclusion["cta"] != CONCLUSION_CTA:
        raise ValueError("Invalid conclusion CTA.")

    if not isinstance(conclusion["credit"], str):
        raise ValueError("Conclusion credit must be a string.")

    if conclusion["conclusion"] != expected_style:
        raise ValueError("Invalid conclusion configuration.")

    for index, slide in enumerate(slides[1:-1], start=1):
        if set(slide.keys()) != {"text", "credit"}:
            raise ValueError(
                f"Answer slide {index} must contain only "
                "'text' and 'credit'."
            )

        if not isinstance(slide["text"], str) or not slide["text"].strip():
            raise ValueError(f"Answer slide {index} has empty text.")

        if not isinstance(slide["credit"], str):
            raise ValueError(
                f"Answer slide {index} credit must be a string."
            )


def generate_with_model(client, model, raw_content):
    full_prompt = f"""
{PROMPT}

RAW MATERIAL:

----------------------------

{raw_content}

----------------------------

Generate the final carousel JSON now.
"""

    interaction = client.interactions.create(
        model=model,
        input=full_prompt,
        store=False,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": {
                "type": "object",
                "properties": {
                    "slides": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string"},
                                "credit": {"type": "string"},
                                "description": {"type": "string"},
                                "cta": {"type": "string"},
                                "intro": {
                                    "type": "object",
                                    "properties": {
                                        "header": {
                                            "type": "object",
                                            "properties": {
                                                "background": {"type": "boolean"},
                                                "background_color": {"type": "string"}
                                            },
                                            "required": ["background", "background_color"]
                                        },
                                        "question": {
                                            "type": "object",
                                            "properties": {
                                                "background": {"type": "boolean"},
                                                "background_color": {"type": "string"}
                                            },
                                            "required": ["background", "background_color"]
                                        },
                                        "credit": {
                                            "type": "object",
                                            "properties": {
                                                "background": {"type": "boolean"},
                                                "background_color": {"type": "string"}
                                            },
                                            "required": ["background", "background_color"]
                                        }
                                    },
                                    "required": ["header", "question", "credit"]
                                },
                                "conclusion": {
                                    "type": "object",
                                    "properties": {
                                        "header": {
                                            "type": "object",
                                            "properties": {
                                                "background": {"type": "boolean"},
                                                "background_color": {"type": "string"}
                                            },
                                            "required": ["background", "background_color"]
                                        },
                                        "question": {
                                            "type": "object",
                                            "properties": {
                                                "background": {"type": "boolean"},
                                                "background_color": {"type": "string"}
                                            },
                                            "required": ["background", "background_color"]
                                        },
                                        "credit": {
                                            "type": "object",
                                            "properties": {
                                                "background": {"type": "boolean"},
                                                "background_color": {"type": "string"}
                                            },
                                            "required": ["background", "background_color"]
                                        }
                                    },
                                    "required": ["header", "question", "credit"]
                                }
                            },
                            "required": ["text", "credit"]
                        }
                    }
                },
                "required": ["slides"]
            }
        },
    )

    response_text = interaction.output_text

    if not response_text:
        raise ValueError("Gemini returned an empty response.")

    data = json.loads(extract_json(response_text))
    data = normalize_content(data)
    validate_content(data)

    return data


def is_daily_quota_error(error):
    message = str(error).lower()
    return (
        "requests per day on free tier" in message
        or "limit: 20 requests per day" in message
        or ("daily" in message and "quota" in message)
    )


def is_temporary_error(error):
    message = str(error).upper()
    return any(
        marker in message
        for marker in (
            "503",
            "UNAVAILABLE",
            "429",
            "RESOURCE_EXHAUSTED",
            "INTERNAL",
            "DEADLINE",
        )
    )


def generate_content(raw_content):
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    last_error = None

    for attempt in range(1, MAX_ATTEMPTS_PER_MODEL + 1):
        try:
            print(
                f"Trying {model} "
                f"(attempt {attempt}/{MAX_ATTEMPTS_PER_MODEL})..."
            )

            result = generate_with_model(
                client,
                model,
                raw_content,
            )

            print(f"Success with {model}.")
            return result

        except Exception as error:
            last_error = error

            print()
            print("----- GEMINI ERROR -----")
            print(f"Model: {model}")
            print(f"Attempt: {attempt}/{MAX_ATTEMPTS_PER_MODEL}")
            print(f"Exception type: {type(error).__name__}")
            print(f"Exception: {error!r}")
            print(f"Error text: {str(error)}")
            print("------------------------")
            print()

            # A daily Free Tier quota cannot be fixed by retrying.
            if is_daily_quota_error(error):
                raise RuntimeError(
                    f"Gemini daily quota reached for {model}. "
                    "Change GEMINI_MODEL in .env or wait for the quota to reset."
                ) from error

            if not is_temporary_error(error):
                raise

            if attempt < MAX_ATTEMPTS_PER_MODEL:
                wait_seconds = RETRY_BASE_SECONDS * attempt

                print(
                    f"Temporary Gemini error on {model}. "
                    f"Retrying in {wait_seconds}s..."
                )

                time.sleep(wait_seconds)
            else:
                print(
                    f"{model} is temporarily unavailable after "
                    f"{MAX_ATTEMPTS_PER_MODEL} attempts."
                )

    raise RuntimeError(
        f"Gemini model {model} was unavailable. "
        f"Last error: {last_error!r}"
    )


def main():
    load_dotenv()

    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add it to your .env file."
        )

    print("Reading raw material...")

    raw_content = read_raw_file()

    print("Sending question and answer to Gemini...")

    content = generate_content(raw_content)

    OUTPUT_FILE.write_text(
        json.dumps(
            content,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print(f"Created: {OUTPUT_FILE}")
    print(f"Slides: {len(content['slides'])}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"\nERROR: {error}", file=sys.stderr)
        sys.exit(1)
