#!/usr/bin/env python3

"""
Generate a ready-to-paste ChatGPT image-research prompt from content_.json.

Input:
    content_.json

Output:
    image_prompt.txt

The generated prompt asks ChatGPT to:
- search for one real existing Tolkien image per slide
- perform an image search for every slide
- return the actual image-search result/image for every slide
- prioritize the credited artist
- return the artist name alongside each image
- prioritize dark fantasy, epic, atmospheric, painterly/oil artwork
- perform no JSON output
"""

import json
import sys
from pathlib import Path


INPUT_FILE = Path("../json/content.json")
OUTPUT_FILE = Path("../txt/image_prompt.txt")


PROMPT_TEMPLATE = r"""

I need you to research REAL, EXISTING Tolkien artwork/images for the carousel below.

This is an image research task for a Tolkien lore communication project.

Use web search and image search directly in ChatGPT.

## TASK

Find ONE suitable existing artwork/image for EVERY slide in the carousel, including the intro/question slide.

For every slide:

1. Identify the primary visual subject of the slide.
2. Search for the relevant subject.
3. Use the artist named in the slide's "credit" as a preference when a credit is provided, but do NOT restrict the search to that artist.
4. Search broadly across verified Tolkien artwork and other suitable productions, prioritizing a strong match to the slide topic and a dark, epic, atmospheric, painterly/oil aesthetic.
5. If the first results are maps, diagrams, weak illustrations, or visually unsuitable, continue searching.
6. Find a real existing artwork/image online.
7. Verify that the artwork is genuinely relevant to the slide subject.
8. Verify the artist attribution for the exact image selected.
9. DISPLAY THE ACTUAL IMAGE in your response.
11. Give the artist/author name associated with that exact image.

## OUTPUT — VERY IMPORTANT

The first slide is the INTRO slide.

For the intro slide, use the question itself as the topic/name.

For answer slides, use the main character, place, event, or subject from the slide text as the topic/name.

I want ONLY:

### Slide 1 — Intro: Which kings and high rulers...
[ACTUAL IMAGE]

**Artist:** John Howe

### Slide 2 — Finwë
[ACTUAL IMAGE]

**Artist:** Nicolas Fantoni

### Slide 3 — Fëanor
[ACTUAL IMAGE]

**Artist:** Anato Finnstark

And so on for every slide.


## OUTPUT RESTRICTIONS

DO NOT return JSON.

DO NOT return artwork titles.

DO NOT return source information.

DO NOT explain why the image was selected.

DO NOT provide search queries.

DO NOT provide descriptions.

DO NOT provide additional metadata.

Do NOT add a bibliography or source list at the end.

The response should simply contain the slide number/name, the actual image,
the direct image URL, and the artist/author name.

## ARTIST / CREDIT RULE

Mention author
Do NOT invent an artist attribution.
If no suitable artwork by the requested artist can be found, use a verified relevant alternative artist and give that actual artist's name.

## VISUAL DIRECTION — STRICT REQUIREMENT

The visual style is a very important SELECTION CRITERION.

Every selected image must have a premium, dark-fantasy, epic,
traditional-painting aesthetic.

PRIORITIZE:

- dark fantasy
- epic fantasy
- oil painting / traditional painted artwork
- rich painterly brushwork
- cinematic composition
- dramatic lighting
- deep shadows
- atmospheric depth
- monumental scale
- mythological grandeur
- ancient / medieval atmosphere
- mysterious and melancholic mood
- powerful landscapes and environments
- dramatic scenes of destruction, war, downfall, or transformation
- rich textures
- highly detailed traditional fantasy illustration
- serious and majestic tone

The image should look like an EPIC DARK FANTASY OIL PAINTING
suitable for a premium Tolkien lore Instagram carousel.

When several valid artworks exist, first prioritize how strongly the image matches the slide topic,
then prefer the strongest combination of darkness + epic scale + painterly quality + cinematic atmosphere.

Do NOT select an image merely because it is technically relevant to the subject.
The visual quality and style must also match the direction above.

## STRICTLY AVOID

Do NOT use:

- maps
- geographic maps
- diagrams
- charts
- infographics
- timelines
- encyclopedic illustrations
- screenshots
- wiki graphics
- minimalist illustrations
- flat digital artwork
- cartoon artwork
- anime / manga
- comic-book artwork
- generic fantasy stock images
- photographs
- modern graphic-design artwork
- UI screenshots
- low-resolution images
- images with large text or typography
- AI-generated artwork
- generic fantasy scenes unrelated to Tolkien

A map may be factually perfect for a location, but it MUST NOT be
selected if a suitable Tolkien painting or illustrated scene exists.

## STYLE PRIORITY

When choosing between multiple valid Tolkien artworks, use this priority:

1. Relevant Tolkien artwork with a dark, epic oil-painting aesthetic
2. Relevant Tolkien artwork with a strong traditional painterly aesthetic
3. Relevant Tolkien artwork with a cinematic and atmospheric fantasy aesthetic
4. Other verified traditional Tolkien artwork

Never choose a visually weak image simply because it is easier to find.

## SUBJECT VS STYLE

The artwork MUST still be genuinely relevant to the slide.

Do not use a beautiful Tolkien painting if the subject is unrelated.

However, when several artworks are genuinely relevant, select the one
with the strongest dark, epic, painterly and cinematic visual impact.

## DESTRUCTION / LOST PLACES

For slides concerning destruction, disappearance, downfall, submersion,
or transformation, strongly prefer artwork that visually communicates
the EVENT or CONSEQUENCE rather than simply showing a map of the place.

For example:

- destroyed land → catastrophic landscape / destruction
- submerged land → dramatic sea / drowning / downfall imagery
- fallen kingdom → ruined city / destruction / catastrophe
- abandoned place → atmospheric ruins / empty landscape
- transformed realm → dramatic environmental transformation

The image should communicate the scale and atmosphere of the event while
remaining historically and lore-accurate.

## ARTIST PREFERENCE

Established Tolkien artists are welcome, but they are NOT a restriction.

Artists such as these may be preferred when they have a strong visual match:

- Ted Nasmith
- Alan Lee
- John Howe
- Donato Giancola
- Roger Garland
- Michael Kaluta
- Jef Murray
- Angus McBride
- other verified Tolkien illustrators

Also consider other verified artists, adaptations, productions, commissioned artwork,
book artwork, film-related artwork, or other legitimate existing Tolkien-related
visual productions when they provide a stronger match for the slide.

The most important criteria are:

1. The image genuinely matches the slide topic.
2. The image has a dark, epic, atmospheric, painterly/oil visual style.
3. The image has strong cinematic and artistic quality.
4. The artwork is real and already exists.
5. The artist/creator attribution can be verified.

Do NOT reject a strong image simply because the artist is not one of the
preferred names above.

The artwork must still actually depict or meaningfully represent the subject of the slide.

## FINAL VISUAL TEST

Before displaying an image, silently ask:

"Does this look like a dark, epic, atmospheric Tolkien oil painting
that could belong in a premium fantasy art book?"

If the answer is NO, continue searching.

Do NOT settle for the first technically relevant result.

Search further until you find the strongest suitable image available.

## IMAGE RULES

- Real existing artwork only.
- Do NOT generate images.
- Do NOT use AI-generated artwork.
- Do NOT use generic stock photography.
- Do NOT use unrelated fantasy artwork.
- Prefer established Tolkien artists and genuine Tolkien artwork.
- Verify that the artwork actually relates to the slide subject.
- Do not confuse the website hosting the artwork with the artist.
- Every slide must receive an image.
- Every displayed image must receive its own direct image URL.
- Every displayed image must receive its own artist attribution.

## FALLBACK

If an exact character depiction cannot be found, use a relevant contextual image:

character → scene → location → event → realm/symbol

The fallback must still be clearly relevant to the slide AND must preserve
the strict dark-fantasy, epic, painterly visual direction.

## IMPORTANT

Search EVERY slide.

Do not skip the intro slide.

Do not return a summary at the end.

Do not return JSON.


Only show the slide number/name, the image,
and the artist/author name.

DISPLAY THE IMAGE SEARCH RESULT DIRECTLY IN THE CHAT. DO NOT RETURN OR REQUEST THE IMAGE URL.
s
==================================================
CAROUSEL CONTENT
==================================================

----------------------------------------

"""


def load_content():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"{INPUT_FILE} was not found."
        )

    try:
        content = json.loads(
            INPUT_FILE.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON in {INPUT_FILE}: {error}"
        ) from error

    if not isinstance(content, dict):
        raise ValueError(
            "content_.json must contain a JSON object."
        )

    slides = content.get("slides")

    if not isinstance(slides, list) or not slides:
        raise ValueError(
            "content_.json must contain a non-empty 'slides' array."
        )

    return content


def build_prompt(content):
    carousel_json = json.dumps(
        content,
        ensure_ascii=False,
        indent=2
    )

    return (
        PROMPT_TEMPLATE
        + carousel_json
        + "\n\n"
        + "----------------------------------------\n\n"
        + "IMPORTANT: Begin the image search now.\n\n"
        + "Search EVERY slide individually.\n\n"
        + "For EVERY slide, find ONE REAL, EXISTING Tolkien artwork.\n\n"
        + "The selected artwork MUST strongly match the slide topic and should ideally "
          "satisfy the visual direction: DARK + EPIC + ATMOSPHERIC + PAINTERLY/OIL + CINEMATIC.\n\n"
        + "Do not use maps, diagrams, infographics, screenshots, generic "
          "fantasy, or visually weak artwork when a suitable relevant "
          "Tolkien-related artwork or production image can be found.\n\n"
        + "Do not stop at the first relevant result. Search further when necessary.\n\n"
        + "DISPLAY the actual image for every slide.\n\n"
        + "For every displayed image, immediately provide:\n\n"
        + "**Artist:** [verified artist of that exact image]\n\n"
        + "Every slide MUST have an image.\n"
        + "Every image MUST have its own artist attribution.\n"
    )


def main():
    content = load_content()

    prompt = build_prompt(content)

    OUTPUT_FILE.write_text(
        prompt,
        encoding="utf-8"
    )

    print(f"Created: {OUTPUT_FILE}")
    print(f"Slides included: {len(content['slides'])}")
    print()
    print(
        "Copy image_prompt.txt and paste it directly into ChatGPT."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(
            f"ERROR: {error}",
            file=sys.stderr
        )
        sys.exit(1)
