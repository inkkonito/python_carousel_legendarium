# Legendarium Carousel — Workflow Instructions

## Overview

This project uses a simple pipeline to create Instagram carousels for **The Legendarium Companion**.

The complete workflow is:

```text
raw.txt
   ↓
python3 run.py
   ↓
content_.json + image_prompt.txt
   ↓
ChatGPT / Work — image research
   ↓
images/ + content.json
   ↓
python3 add_text.py
   ↓
output/
   ↓
review
   ↓
python3 archive_iteration.py
   ↓
published/ + src_archive/
```

---

## 1. Start a New Iteration

Put the source material for the new carousel into:

```text
raw.txt
```

The working directory should contain:

```text
raw.txt
content.json
images/
output/
```

`images/` and `output/` should be empty when starting a new iteration.

Then run:

```bash
python3 run.py
```

---

## 2. Generate the Content

`run.py` first executes:

```text
generate_content_.py
```

This generates:

```text
content_.json
```

`content_.json` contains the generated carousel content.

### Important

Do **not** modify `content_.json` during the image-research step.

It is the generated content source for the iteration.

---

## 3. Generate the Image Research Prompt

`run.py` then executes:

```text
generate_image_research_prompt.py
```

This generates:

```text
image_prompt.txt
```

Copy the contents of `image_prompt.txt` and use it in ChatGPT/Work.

---

## 4. Image Research

The image-research step is performed manually using ChatGPT/Work.

Search **every carousel slide**, including the introduction and conclusion when an image is required.

### For every slide

Find exactly **one real, existing Tolkien artwork** that is relevant to the slide.

Do **not** use AI-generated artwork.

The selected artwork should:

- already exist online
- be relevant to the slide
- have a verifiable artist/author
- have a source where the attribution can be checked

### For each selected image

1. Search for the artwork.
2. Verify that it matches the slide.
3. Verify the artist/author attribution.
4. Display the selected artwork.
5. Download the image.
6. Save it in `images/`.
7. Number it according to slide order.

Example:

```text
images/
├── 0.jpg
├── 1.jpg
├── 2.jpg
├── 3.jpg
├── 4.jpg
└── 5.jpg
```

The numbering must match the slide order exactly.

```text
0.jpg → Slide 1
1.jpg → Slide 2
2.jpg → Slide 3
...
```

---

## 5. Create `content.json`

The image-research step must create:

```text
content.json
```

It should be based on:

```text
content_.json
```

`content_.json` must remain unchanged.

For every slide, update the:

```json
"credit": "..."
```

field with the **verified artist/author of the exact downloaded artwork**.

### Attribution rules

Never guess an artist or author.

The credit must correspond to the exact image being used.

If the attribution cannot be verified, continue researching or select another artwork.

---

## 6. Check the Working Files

Before running `add_text.py`, verify that:

```text
images/
├── 0.jpg
├── 1.jpg
├── 2.jpg
├── ...
└── [one image per slide]

content.json
content_.json
```

Check that:

- there is exactly one image per slide
- numbering follows slide order
- the images are real existing artworks
- the artworks are relevant to their slides
- every artist/author attribution is verified
- every credit matches its corresponding image
- `content_.json` has not been modified

---

## 7. Generate the Carousel

Run:

```bash
python3 add_text.py
```

This processes the downloaded images and generates the final carousel assets in:

```text
output/
```

### Review the carousel

Before archiving, inspect the generated carousel and check:

- text positioning
- image quality
- slide order
- credits
- spelling
- formatting
- introduction
- conclusion
- overall visual consistency

Do not archive the iteration until the carousel has been reviewed.

---

## 8. Archive the Completed Iteration

Once the carousel is approved, run:

```bash
python3 archive_iteration.py
```

The archive script separates the published assets from the source/generated assets.

### Published archive

Everything inside:

```text
images/
```

is moved to:

```text
published/YYMMDD/
```

`content.json` is copied into the same folder.

Example:

```text
published/
└── 260920/
    ├── 0.jpg
    ├── 1.jpg
    ├── 2.jpg
    ├── 3.jpg
    ├── 4.jpg
    ├── 5.jpg
    └── content.json
```

### Source archive

Everything inside:

```text
output/
```

is moved to:

```text
src_archive/YYMMDD/
```

`raw.txt` is copied into the same folder.

Example:

```text
src_archive/
└── 260920/
    ├── slide_0.png
    ├── slide_1.png
    ├── slide_2.png
    ├── ...
    └── raw.txt
```

---

## 9. Duplicate Archive Dates

The archive script never overwrites an existing dated archive.

If:

```text
published/260920/
```

or:

```text
src_archive/260920/
```

already exists, the script finds the next available suffix.

For example:

```text
260920/
260920_1/
260920_2/
260920_3/
```

The **same suffix is used for both archives** so that they remain paired:

```text
published/260920_2/
src_archive/260920_2/
```

---

## 10. Reset the Working Files

After archiving:

### Images

```text
images/
```

is empty.

### Output

```text
output/
```

is empty.

### `raw.txt`

The current `raw.txt` has been copied to:

```text
src_archive/YYMMDD[_N]/raw.txt
```

Then the root file is reset to an empty:

```text
raw.txt
```

### `content.json`

The current `content.json` has been copied to:

```text
published/YYMMDD[_N]/content.json
```

Then the root file is reset to an empty:

```text
content.json
```

The project is therefore ready for the next iteration.

---

# Complete Command Sequence

## Start a new carousel

```bash
python3 run.py
```

## Research images

Use:

```text
image_prompt.txt
```

in ChatGPT/Work.

The image-research step creates:

```text
images/
content.json
```

## Generate the carousel

```bash
python3 add_text.py
```

## Review the generated carousel

Check:

```text
output/
```

## Archive the completed iteration

```bash
python3 archive_iteration.py
```

## Start the next iteration

Put new source material into:

```text
raw.txt
```

Then run:

```bash
python3 run.py
```

---

# Project Structure

A typical project looks like:

```text
legendarium-carousel/
│
├── run.py
├── generate_content_.py
├── generate_image_research_prompt.py
├── add_text.py
├── archive_iteration.py
│
├── raw.txt
├── content.json
├── content_.json
├── image_prompt.txt
│
├── images/
├── output/
│
├── published/
└── src_archive/
```

After several iterations:

```text
published/
├── 260920/
├── 260920_1/
└── 260921/

src_archive/
├── 260920/
├── 260920_1/
└── 260921/
```

---

# Important Rules

## Artwork

Use real existing Tolkien artwork.

Do **not** use AI-generated images.

## Attribution

Never guess an artist/author.

Verify the attribution for the exact artwork used.

## Slide Order

Image numbering must always correspond to slide order:

```text
0.jpg → Slide 1
1.jpg → Slide 2
2.jpg → Slide 3
...
```

## Content Source

Keep:

```text
content_.json
```

unchanged during image research.

## Review Before Archive

Always review:

```text
output/
```

before running:

```bash
python3 archive_iteration.py
```

## Archive Safety

Existing archives are never overwritten.

The archive script automatically creates:

```text
YYMMDD
YYMMDD_1
YYMMDD_2
...
```

when necessary.

The published and source archives use the same date/suffix.

---

# Workflow at a Glance

```text
                    raw.txt
                       │
                       ▼
                 python3 run.py
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
       content_.json       image_prompt.txt
             │                   │
             │             ChatGPT / Work
             │                   │
             │          ┌────────┴────────┐
             │          ▼                 ▼
             │       images/         content.json
             │          │                 │
             └──────────┴─────────────────┘
                       │
                       ▼
              python3 add_text.py
                       │
                       ▼
                    output/
                       │
                       ▼
                    REVIEW
                       │
                       ▼
          python3 archive_iteration.py
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
        published/          src_archive/
        YYMMDD[_N]/         YYMMDD[_N]/
             │                   │
        images +             output +
        content.json         raw.txt
```

---

# End State

After a successful archive, the working environment is clean:

```text
images/        → empty
output/        → empty
raw.txt        → empty
content.json   → empty
```

The completed iteration is safely preserved in:

```text
published/YYMMDD[_N]/
src_archive/YYMMDD[_N]/
```

The project is ready to start the next carousel.
