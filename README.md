# Tolkien Instagram Image Composer

A lightweight Python tool for creating polished 1080 × 1350 Instagram carousel slides from Tolkien artwork and structured text content.

The project is used to create visual content for **The Legendarium Companion**, a Tolkien lore search and exploration project.

## Features

- Instagram-ready 1080 × 1350 output
- Intro slide with logo, branding, question and artwork credit
- Content slides with artwork, branding, lore text and credits
- Automatic artwork resizing
- Automatic detection and removal of embedded dark side borders
- Vertical artwork cropping when required
- Custom typography
- Custom SVG logo
- Configurable colors and layout
- JSON-based slide content
- Separation between source material and published content

## Project Structure

```text
image-text-tool/
│
├── src/
│   └── 260919/
│       ├── artwork-01.jpg
│       ├── artwork-02.jpg
│       └── ...
│
├── published/
│   └── 260919/
│       ├── slide_01.jpg
│       ├── slide_02.jpg
│       ├── slide_03.jpg
│       └── content.json
│
├── fonts/
│   ├── Cinzel.ttf
│   └── CormorantGaramond.ttf
│
├── logo.svg
├── add_text.py
└── README.md
```

## Source and Published Content

The project separates original source material from generated and published content.

### `src/`

Contains the original artwork used to create the carousel.

Each publication is organized by date:

```text
src/
└── 260919/
    ├── artwork-01.jpg
    ├── artwork-02.jpg
    └── ...
```

### `published/`

Contains the final generated Instagram assets and the content used for that publication.

```text
published/
└── 260919/
    ├── slide_01.jpg
    ├── slide_02.jpg
    ├── slide_03.jpg
    └── content.json
```

This makes it possible to keep multiple publications organized while preserving the original source artwork separately from the final published assets.

The date format used is:

```text
YYMMDD
```

For example:

```text
260919
```

represents September 19, 2026.

## Requirements

- Python 3
- Pillow
- `rsvg-convert`
- Cinzel font
- Cormorant Garamond font

### Install Pillow

```bash
python3 -m pip install Pillow
```

### Install SVG rendering support

The project uses `rsvg-convert` to render the SVG logo.

On macOS:

```bash
brew install librsvg
```

Verify the installation:

```bash
which rsvg-convert
```

## Fonts

Place the following fonts in the `fonts/` directory:

```text
fonts/
├── Cinzel.ttf
└── CormorantGaramond.ttf
```

The project uses:

- **Cinzel** for branding and headers
- **Cormorant Garamond** for lore text

## Content

Slide content is defined in a `content.json` file associated with each publication.

Example:

```json
{
  "slides": [
    {
      "text": "Which kings and high rulers played the most significant roles in shaping the history of Middle-earth?",
      "credit": "John Howe",
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
      "text": "Finwë: First High King of the Ñoldor, Finwë led his people to Valinor. He was later slain by Morgoth at Formenos, reshaping the history of the Ñoldor.",
      "credit": "Nicolas Fantoni"
    }
  ]
}
```

The first slide is automatically treated as the intro slide.

All following slides are treated as content slides.

## Intro Slide

The intro slide contains three independently configurable elements:

1. Header
2. Question
3. Artwork credit

Each element can have its own background.

Example:

```json
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
```

Backgrounds can also be disabled:

```json
"header": {
  "background": false
}
```

The background boxes automatically adapt to the content width and are centered on the slide.

## Artwork Handling

For normal content slides, the script automatically:

1. Loads the artwork
2. Applies EXIF orientation
3. Converts the image to RGB
4. Detects embedded dark borders
5. Removes dark side borders
6. Scales the artwork to 1080 px wide
7. Vertically crops the artwork when necessary
8. Places the artwork above the text panel

The artwork is never horizontally distorted.

This allows artwork with different source dimensions to be consistently formatted for Instagram.

## Design

The visual design uses a simple palette:

```text
Background: #0C0B09
Text:       #F2E8D0
Gold:       #C9A86A
```

The main branding is:

```text
The Legendarium Companion
```

The logo is loaded from:

```text
logo.svg
```

## Running the Script

From the project directory:

```bash
python3 add_text.py
```

The script processes the configured source artwork and content and generates the finished slides.

Generated files are placed in the relevant `published/YYMMDD/` directory.

## Output

Published carousel assets are organized by publication date:

```text
published/
└── 260919/
    ├── slide_01.jpg
    ├── slide_02.jpg
    ├── slide_03.jpg
    └── content.json
```

Every generated slide is:

```text
1080 × 1350 px
```

The output is optimized for Instagram's 4:5 portrait format.

## Workflow

```text
Original artwork
      ↓
src/YYMMDD/
      ↓
Content + composition
      ↓
add_text.py
      ↓
published/YYMMDD/
      ↓
Instagram carousel
```

Each publication therefore keeps its own:

- Original source artwork
- Generated slides
- Content definition

## Design Principles

The compositor is designed around a few principles:

- Artwork remains the visual focus
- Text remains readable without dominating the slide
- Consistent typography across the carousel
- Consistent branding
- Minimal visual decoration
- Automatic handling of different artwork dimensions
- Instagram-ready output
- Reusable content structure
- Clear separation between source and published assets

## Credits

Artwork credits are provided through the relevant `content.json` file.

The tool does not generate the underlying artwork. It is intended to compose existing artwork with text, credits and branding.

Make sure you have the appropriate rights or permissions to use any artwork included in the project.

## License

The code in this repository can be licensed separately from the artwork, fonts and branding assets.

Artwork, logos and other third-party assets may have their own copyright and licensing terms.

Check the relevant license or usage terms before redistributing them.
