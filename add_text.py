from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageColor
import subprocess
from io import BytesIO
from pathlib import Path
import json


# ============================================================
# CONFIGURATION
# ============================================================

IMAGES_DIR = Path("images")
OUTPUT_DIR = Path("output")
CONTENT_FILE = Path("content.json")

LOGO_PATH = "logo.svg"

# Final Instagram canvas
CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1350

# Intro artwork
ARTWORK_WIDTH = 1080
ARTWORK_HEIGHT = 1350

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

# Fonts
MAIN_FONT_PATH = "fonts/CormorantGaramond.ttf"
HEADER_FONT_PATH = "fonts/Cinzel.ttf"
CREDIT_FONT_PATH = "fonts/CormorantGaramond.ttf"

# Font sizes
MAX_FONT_SIZE = 38
MIN_FONT_SIZE = 28

HEADER_FONT_SIZE = 28
CREDIT_FONT_SIZE = 18
INTRO_FONT_SIZE = 64

# Colors
TEXT_COLOR = "#F2E8D0"
HEADER_COLOR = "#F2E8D0"
ARTWORK_BACKGROUND = "#0C0B09"
PANEL_COLOR = "#0C0B09"
ACCENT_COLOR = "#C9A86A"
CREDIT_COLOR = "#F2E8D0"

# ============================================================
# NORMAL SLIDE LAYOUT
# ============================================================

# Text uses almost the entire width.
NORMAL_TEXT_SIDE_MARGIN = 45

# Minimum artwork height.
NORMAL_ARTWORK_MIN_HEIGHT = 900

PANEL_TOP_PADDING = 20
HEADER_TO_TEXT_GAP = 16
TEXT_BOTTOM_PADDING = 18

LINE_SPACING = 6

# Header
HEADER_LOGO_SIZE = 42
HEADER_GAP = 10
HEADER_TEXT = "The Legendarium Companion"

# ============================================================
# EMBEDDED ARTWORK BORDER DETECTION
# ============================================================

# The source artwork shown in the screenshot contains black
# side borders inside the actual image file.
#
# These settings detect continuous dark columns at the
# extreme left/right edges and remove them before scaling.
#
# This ONLY applies to normal slides.
#
# We deliberately use a conservative detection rule:
# a column must be overwhelmingly dark before it is considered
# an embedded border.
BORDER_DARK_THRESHOLD = 35
BORDER_DARK_RATIO = 0.96
BORDER_SCAN_MAX_RATIO = 0.35

# Minimum width that must remain after trimming.
BORDER_MIN_REMAINING_WIDTH = 300


# ============================================================
# INTRO LAYOUT
# ============================================================

INTRO_HEADER_TOP = 55

INTRO_TEXT_MAX_WIDTH = 850
INTRO_TEXT_Y_CENTER = 675
INTRO_LINE_SPACING = 12

INTRO_CREDIT_BOTTOM_MARGIN = 25

INTRO_BOX_PADDING_X = 35
INTRO_BOX_RADIUS = 10

INTRO_HEADER_BOX_PADDING_TOP = 15
INTRO_HEADER_BOX_PADDING_BOTTOM = 15

INTRO_QUESTION_BOX_PADDING_TOP = 30
INTRO_QUESTION_BOX_PADDING_BOTTOM = 30

INTRO_CREDIT_BOX_PADDING_TOP = 5
INTRO_CREDIT_BOX_PADDING_BOTTOM = 5

# Normal slide credit background
CREDIT_BACKGROUND_PADDING_X = 10
CREDIT_BACKGROUND_PADDING_Y = 5


# ============================================================
# SVG RENDERING
# ============================================================

def render_svg(svg_path, width, height):
    """
    Render an SVG using rsvg-convert.
    """

    result = subprocess.run(
        [
            "rsvg-convert",
            "-w",
            str(width),
            "-h",
            str(height),
            str(svg_path),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    return Image.open(
        BytesIO(result.stdout)
    ).convert("RGBA")


# ============================================================
# EMBEDDED BORDER DETECTION
# ============================================================

def is_dark_pixel(pixel):
    """
    Return True when a pixel is sufficiently dark.

    Works with RGB tuples.
    """

    r, g, b = pixel[:3]

    return (
        r <= BORDER_DARK_THRESHOLD
        and g <= BORDER_DARK_THRESHOLD
        and b <= BORDER_DARK_THRESHOLD
    )


def column_is_embedded_border(
    image,
    x,
):
    """
    Determine whether a column is likely part of an
    embedded black/dark border.

    A border column is expected to be almost entirely dark.
    """

    pixels = image.load()

    dark_count = 0
    total_count = image.height

    for y in range(
        image.height
    ):
        if is_dark_pixel(
            pixels[x, y]
        ):
            dark_count += 1

    ratio = (
        dark_count
        / total_count
    )

    return ratio >= BORDER_DARK_RATIO


def trim_embedded_side_borders(image):
    """
    Remove large continuous dark borders embedded in the
    source artwork.

    Only the LEFT and RIGHT edges are scanned.

    Important:
    - The artwork itself is not resized here.
    - No vertical cropping is performed here.
    - Internal dark areas are preserved.
    - Only edge columns that are overwhelmingly dark
      are removed.

    This fixes source files where the artwork itself is
    surrounded by black margins, as visible in the supplied
    screenshot.
    """

    image = image.convert("RGB")

    width, height = image.size

    max_scan = int(
        width * BORDER_SCAN_MAX_RATIO
    )

    left = 0

    while (
        left < max_scan
        and column_is_embedded_border(
            image,
            left,
        )
    ):
        left += 1

    right = width - 1

    while (
        right >= width - max_scan
        and column_is_embedded_border(
            image,
            right,
        )
    ):
        right -= 1

    remaining_width = (
        right - left + 1
    )

    # Safety check:
    # never allow the detector to remove almost
    # the entire image.
    if (
        remaining_width
        < BORDER_MIN_REMAINING_WIDTH
    ):
        return image

    # Only crop if an actual side border was found.
    if left > 0 or right < width - 1:

        print(
            "  Removing embedded side borders: "
            f"left={left}px, "
            f"right={width - 1 - right}px"
        )

        return image.crop(
            (
                left,
                0,
                right + 1,
                height,
            )
        )

    return image


# ============================================================
# IMAGE PREPARATION
# ============================================================

def prepare_intro_artwork(image):
    """
    Prepare intro artwork.

    The complete artwork is fitted inside 1080x1350.
    Nothing is cropped or distorted.
    """

    image = ImageOps.exif_transpose(
        image
    ).convert("RGB")

    source_width, source_height = image.size

    scale = min(
        ARTWORK_WIDTH / source_width,
        ARTWORK_HEIGHT / source_height,
    )

    new_width = int(
        source_width * scale
    )

    new_height = int(
        source_height * scale
    )

    image = image.resize(
        (
            new_width,
            new_height,
        ),
        Image.Resampling.LANCZOS,
    )

    canvas = Image.new(
        "RGB",
        (
            ARTWORK_WIDTH,
            ARTWORK_HEIGHT,
        ),
        ARTWORK_BACKGROUND,
    )

    x = (
        ARTWORK_WIDTH - new_width
    ) // 2

    y = (
        ARTWORK_HEIGHT - new_height
    ) // 2

    canvas.paste(
        image,
        (
            x,
            y,
        ),
    )

    return canvas


def prepare_normal_artwork(
    image,
    target_height,
):
    """
    Prepare artwork for a normal slide.

    Processing order:

    1. Remove embedded black side borders from the source.
    2. Scale the actual artwork to EXACTLY 1080px wide.
    3. Preserve the original aspect ratio.
    4. If the resulting image is too tall, crop vertically.
    5. Never crop horizontally.
    6. Never distort.

    This means the actual artwork reaches both the left
    and right edges of the Instagram canvas.
    """

    image = ImageOps.exif_transpose(
        image
    ).convert("RGB")

    # ========================================================
    # REMOVE EMBEDDED SIDE BORDERS
    # ========================================================

    image = trim_embedded_side_borders(
        image
    )

    source_width, source_height = image.size

    # ========================================================
    # SCALE TO EXACTLY 1080PX WIDTH
    # ========================================================

    scale = (
        CANVAS_WIDTH
        / source_width
    )

    new_width = CANVAS_WIDTH

    new_height = int(
        source_height * scale
    )

    image = image.resize(
        (
            new_width,
            new_height,
        ),
        Image.Resampling.LANCZOS,
    )

    # ========================================================
    # CROP VERTICALLY IF NECESSARY
    # ========================================================

    if new_height > target_height:

        crop_amount = (
            new_height - target_height
        )

        crop_top = (
            crop_amount // 2
        )

        image = image.crop(
            (
                0,
                crop_top,
                CANVAS_WIDTH,
                crop_top + target_height,
            )
        )

        return image

    # ========================================================
    # IMAGE IS SHORTER THAN AVAILABLE AREA
    # ========================================================

    canvas = Image.new(
        "RGB",
        (
            CANVAS_WIDTH,
            target_height,
        ),
        ARTWORK_BACKGROUND,
    )

    y = (
        target_height - new_height
    ) // 2

    canvas.paste(
        image,
        (
            0,
            y,
        ),
    )

    return canvas


# ============================================================
# FONT HELPERS
# ============================================================

def load_font(path, size):
    return ImageFont.truetype(
        path,
        size,
    )


def get_text_bbox(draw, text, font):
    return draw.textbbox(
        (0, 0),
        text,
        font=font,
    )


def get_text_size(draw, text, font):
    bbox = get_text_bbox(
        draw,
        text,
        font,
    )

    return (
        bbox[2] - bbox[0],
        bbox[3] - bbox[1],
    )


# ============================================================
# TEXT WRAPPING
# ============================================================

def wrap_text(
    draw,
    text,
    font,
    max_width,
):
    """
    Wrap text according to max width.
    """

    words = text.split()

    if not words:
        return []

    lines = []
    current_line = ""

    for word in words:

        test_line = (
            word
            if not current_line
            else current_line + " " + word
        )

        width, _ = get_text_size(
            draw,
            test_line,
            font,
        )

        if width <= max_width:

            current_line = test_line

        else:

            if current_line:
                lines.append(
                    current_line
                )

            current_line = word

    if current_line:
        lines.append(
            current_line
        )

    return lines


# ============================================================
# DRAW BACKGROUND BOX
# ============================================================

def draw_background_box(
    canvas,
    center_x,
    top,
    content_width,
    content_height,
    background_color,
    padding_x=INTRO_BOX_PADDING_X,
    padding_top=0,
    padding_bottom=0,
):
    """
    Draw an independent background box whose width
    follows the content width.
    """

    overlay = Image.new(
        "RGBA",
        canvas.size,
        (0, 0, 0, 0),
    )

    draw = ImageDraw.Draw(
        overlay
    )

    rgb_color = ImageColor.getrgb(
        background_color
    )

    box_width = (
        content_width
        + padding_x * 2
    )

    box_left = (
        center_x
        - box_width / 2
    )

    box_right = (
        center_x
        + box_width / 2
    )

    box_top = (
        top
        - padding_top
    )

    box_bottom = (
        top
        + content_height
        + padding_bottom
    )

    draw.rounded_rectangle(
        (
            box_left,
            box_top,
            box_right,
            box_bottom,
        ),
        radius=INTRO_BOX_RADIUS,
        fill=(
            rgb_color[0],
            rgb_color[1],
            rgb_color[2],
            225,
        ),
    )

    return Image.alpha_composite(
        canvas,
        overlay,
    )


# ============================================================
# BRANDING HEADER
# ============================================================

def draw_branding_header(
    canvas,
    top_y,
):
    """
    Draw logo + brand centered as one group.

    The logo and text are vertically centered using
    the same exact center point.
    """

    draw = ImageDraw.Draw(
        canvas
    )

    logo = render_svg(
        LOGO_PATH,
        HEADER_LOGO_SIZE,
        HEADER_LOGO_SIZE,
    )

    header_font = load_font(
        HEADER_FONT_PATH,
        HEADER_FONT_SIZE,
    )

    logo_width = logo.width
    logo_height = logo.height

    text_width, _ = get_text_size(
        draw,
        HEADER_TEXT,
        header_font,
    )

    total_width = (
        logo_width
        + HEADER_GAP
        + text_width
    )

    start_x = (
        ARTWORK_WIDTH
        - total_width
    ) // 2

    logo_y = top_y

    logo_center_y = (
        logo_y
        + logo_height / 2
    )

    if canvas.mode == "RGBA":

        canvas.alpha_composite(
            logo,
            (
                start_x,
                logo_y,
            ),
        )

    else:

        canvas.paste(
            logo,
            (
                start_x,
                logo_y,
            ),
            logo,
        )

    draw = ImageDraw.Draw(
        canvas
    )

    draw.text(
        (
            start_x
            + logo_width
            + HEADER_GAP,
            logo_center_y,
        ),
        HEADER_TEXT,
        font=header_font,
        fill=HEADER_COLOR,
        anchor="lm",
    )

    return {
        "top": top_y,
        "bottom": top_y + logo_height,
        "left": start_x,
        "right": start_x + total_width,
        "width": total_width,
        "height": logo_height,
    }


# ============================================================
# CENTERED CREDIT HELPER
# ============================================================

def draw_centered_credit_box(
    canvas,
    credit,
    center_x,
    center_y,
    background_enabled,
    background_color,
    padding_x,
    padding_top,
    padding_bottom,
):
    """
    Draw credit and optional background as one
    vertically and horizontally centered component.

    The text and background share the exact same
    center point.
    """

    if not credit:
        return canvas

    font = load_font(
        CREDIT_FONT_PATH,
        CREDIT_FONT_SIZE,
    )

    draw = ImageDraw.Draw(
        canvas
    )

    bbox = draw.textbbox(
        (
            center_x,
            center_y,
        ),
        credit,
        font=font,
        anchor="mm",
    )

    text_width = (
        bbox[2] - bbox[0]
    )

    text_height = (
        bbox[3] - bbox[1]
    )

    if background_enabled:

        box_width = (
            text_width
            + padding_x * 2
        )

        box_height = (
            text_height
            + padding_top
            + padding_bottom
        )

        box_left = (
            center_x
            - box_width / 2
        )

        box_top = (
            center_y
            - box_height / 2
        )

        box_right = (
            center_x
            + box_width / 2
        )

        box_bottom = (
            center_y
            + box_height / 2
        )

        overlay = Image.new(
            "RGBA",
            canvas.size,
            (0, 0, 0, 0),
        )

        overlay_draw = ImageDraw.Draw(
            overlay
        )

        rgb_color = ImageColor.getrgb(
            background_color
        )

        overlay_draw.rounded_rectangle(
            (
                box_left,
                box_top,
                box_right,
                box_bottom,
            ),
            radius=INTRO_BOX_RADIUS,
            fill=(
                rgb_color[0],
                rgb_color[1],
                rgb_color[2],
                225,
            ),
        )

        canvas = Image.alpha_composite(
            canvas,
            overlay,
        )

    draw = ImageDraw.Draw(
        canvas
    )

    draw.text(
        (
            center_x,
            center_y,
        ),
        credit,
        font=font,
        fill=CREDIT_COLOR,
        anchor="mm",
    )

    return canvas


# ============================================================
# NORMAL SLIDE CREDIT
# ============================================================

def draw_credit(
    canvas,
    credit,
):
    """
    Draw credit centered near the bottom of the artwork.
    """

    if not credit:
        return canvas

    font = load_font(
        CREDIT_FONT_PATH,
        CREDIT_FONT_SIZE,
    )

    draw = ImageDraw.Draw(
        canvas
    )

    bbox = draw.textbbox(
        (0, 0),
        credit,
        font=font,
    )

    text_height = (
        bbox[3] - bbox[1]
    )

    credit_center_x = (
        CANVAS_WIDTH / 2
    )

    credit_center_y = (
        canvas.height
        - INTRO_CREDIT_BOTTOM_MARGIN
        - text_height / 2
    )

    return draw_centered_credit_box(
        canvas,
        credit,
        credit_center_x,
        credit_center_y,
        True,
        "#000000",
        CREDIT_BACKGROUND_PADDING_X,
        CREDIT_BACKGROUND_PADDING_Y,
        CREDIT_BACKGROUND_PADDING_Y,
    )


# ============================================================
# NORMAL SLIDE TEXT MEASUREMENT
# ============================================================

def measure_normal_layout(
    draw,
    text,
):
    """
    Calculate the text panel dimensions.

    The text uses almost the complete 1080px width.

    The remaining space is allocated to the artwork.
    """

    text_width = (
        CANVAS_WIDTH
        - 2 * NORMAL_TEXT_SIDE_MARGIN
    )

    header_font = load_font(
        HEADER_FONT_PATH,
        HEADER_FONT_SIZE,
    )

    _, header_text_height = get_text_size(
        draw,
        HEADER_TEXT,
        header_font,
    )

    header_height = max(
        HEADER_LOGO_SIZE,
        header_text_height,
    )

    gold_line_gap = 18
    gold_line_height = 1

    for font_size in range(
        MAX_FONT_SIZE,
        MIN_FONT_SIZE - 1,
        -2,
    ):

        font = load_font(
            MAIN_FONT_PATH,
            font_size,
        )

        lines = wrap_text(
            draw,
            text,
            font,
            text_width,
        )

        line_height = get_text_size(
            draw,
            "Ag",
            font,
        )[1]

        total_text_height = (
            len(lines)
            * line_height
            + max(
                0,
                len(lines) - 1,
            )
            * LINE_SPACING
        )

        panel_height = (
            PANEL_TOP_PADDING
            + header_height
            + gold_line_gap
            + gold_line_height
            + HEADER_TO_TEXT_GAP
            + total_text_height
            + TEXT_BOTTOM_PADDING
        )

        artwork_height = (
            CANVAS_HEIGHT
            - panel_height
        )

        if artwork_height >= NORMAL_ARTWORK_MIN_HEIGHT:

            return {
                "font": font,
                "lines": lines,
                "line_height": line_height,
                "text_height": total_text_height,
                "panel_height": int(panel_height),
                "artwork_height": int(artwork_height),
            }

    # Fallback
    font = load_font(
        MAIN_FONT_PATH,
        MIN_FONT_SIZE,
    )

    lines = wrap_text(
        draw,
        text,
        font,
        text_width,
    )

    line_height = get_text_size(
        draw,
        "Ag",
        font,
    )[1]

    total_text_height = (
        len(lines)
        * line_height
        + max(
            0,
            len(lines) - 1,
        )
        * LINE_SPACING
    )

    panel_height = (
        PANEL_TOP_PADDING
        + header_height
        + gold_line_gap
        + gold_line_height
        + HEADER_TO_TEXT_GAP
        + total_text_height
        + TEXT_BOTTOM_PADDING
    )

    artwork_height = (
        CANVAS_HEIGHT
        - panel_height
    )

    return {
        "font": font,
        "lines": lines,
        "line_height": line_height,
        "text_height": total_text_height,
        "panel_height": int(panel_height),
        "artwork_height": int(artwork_height),
    }


# ============================================================
# INTRO SLIDE
# ============================================================

def process_intro(
    artwork,
    output_path,
    text,
    credit,
    intro_config,
):
    """
    Intro consists of THREE independent sections:

    1. Header
    2. Question
    3. Credit

    Each section can independently have a background.
    """

    canvas = artwork.convert(
        "RGBA"
    )

    draw = ImageDraw.Draw(
        canvas
    )

    header_config = intro_config.get(
        "header",
        {},
    )

    question_config = intro_config.get(
        "question",
        {},
    )

    credit_config = intro_config.get(
        "credit",
        {},
    )

    # ========================================================
    # HEADER
    # ========================================================

    header_info = draw_branding_header(
        canvas,
        INTRO_HEADER_TOP,
    )

    if header_config.get(
        "background",
        False,
    ):

        header_color = header_config.get(
            "background_color",
            PANEL_COLOR,
        )

        canvas = draw_background_box(
            canvas,
            ARTWORK_WIDTH / 2,
            header_info["top"],
            header_info["width"],
            header_info["height"],
            header_color,
            padding_x=INTRO_BOX_PADDING_X,
            padding_top=INTRO_HEADER_BOX_PADDING_TOP,
            padding_bottom=INTRO_HEADER_BOX_PADDING_BOTTOM,
        )

        draw = ImageDraw.Draw(
            canvas
        )

        draw_branding_header(
            canvas,
            INTRO_HEADER_TOP,
        )

    # ========================================================
    # QUESTION
    # ========================================================

    intro_font = load_font(
        MAIN_FONT_PATH,
        INTRO_FONT_SIZE,
    )

    lines = wrap_text(
        draw,
        text,
        intro_font,
        INTRO_TEXT_MAX_WIDTH,
    )

    line_height = get_text_size(
        draw,
        "Ag",
        intro_font,
    )[1]

    total_text_height = (
        len(lines)
        * line_height
        + max(
            0,
            len(lines) - 1,
        )
        * INTRO_LINE_SPACING
    )

    text_top = (
        INTRO_TEXT_Y_CENTER
        - total_text_height / 2
    )

    question_content_width = 0

    for line in lines:

        line_width, _ = get_text_size(
            draw,
            line,
            intro_font,
        )

        question_content_width = max(
            question_content_width,
            line_width,
        )

    if question_config.get(
        "background",
        False,
    ):

        question_color = question_config.get(
            "background_color",
            PANEL_COLOR,
        )

        canvas = draw_background_box(
            canvas,
            ARTWORK_WIDTH / 2,
            text_top,
            question_content_width,
            total_text_height,
            question_color,
            padding_x=INTRO_BOX_PADDING_X,
            padding_top=INTRO_QUESTION_BOX_PADDING_TOP,
            padding_bottom=INTRO_QUESTION_BOX_PADDING_BOTTOM,
        )

        draw = ImageDraw.Draw(
            canvas
        )

    current_y = text_top

    for line in lines:

        line_width, _ = get_text_size(
            draw,
            line,
            intro_font,
        )

        x = (
            ARTWORK_WIDTH
            - line_width
        ) / 2

        draw.text(
            (
                x,
                current_y,
            ),
            line,
            font=intro_font,
            fill=TEXT_COLOR,
        )

        current_y += (
            line_height
            + INTRO_LINE_SPACING
        )

    # ========================================================
    # CREDIT
    # ========================================================

    if credit:

        credit_font = load_font(
            CREDIT_FONT_PATH,
            CREDIT_FONT_SIZE,
        )

        temp_draw = ImageDraw.Draw(
            canvas
        )

        bbox = temp_draw.textbbox(
            (0, 0),
            credit,
            font=credit_font,
            anchor="mm",
        )

        credit_text_height = (
            bbox[3] - bbox[1]
        )

        credit_center_x = (
            ARTWORK_WIDTH / 2
        )

        credit_center_y = (
            ARTWORK_HEIGHT
            - INTRO_CREDIT_BOTTOM_MARGIN
            - (
                credit_text_height
                + INTRO_CREDIT_BOX_PADDING_TOP
                + INTRO_CREDIT_BOX_PADDING_BOTTOM
            ) / 2
        )

        canvas = draw_centered_credit_box(
            canvas,
            credit,
            credit_center_x,
            credit_center_y,
            credit_config.get(
                "background",
                False,
            ),
            credit_config.get(
                "background_color",
                PANEL_COLOR,
            ),
            INTRO_BOX_PADDING_X,
            INTRO_CREDIT_BOX_PADDING_TOP,
            INTRO_CREDIT_BOX_PADDING_BOTTOM,
        )

    # ========================================================
    # SAVE
    # ========================================================

    final_image = canvas.convert(
        "RGB"
    )

    if final_image.size != (
        CANVAS_WIDTH,
        CANVAS_HEIGHT,
    ):
        raise ValueError(
            f"Intro slide has incorrect size: "
            f"{final_image.size}"
        )

    final_image.save(
        output_path,
        "JPEG",
        quality=95,
        optimize=True,
    )


# ============================================================
# NORMAL SLIDE
# ============================================================

def process_normal_slide(
    source_image,
    output_path,
    text,
    credit,
):
    """
    Normal slide.

    Final size:
        1080 × 1350

    Artwork:
        - embedded side borders removed
        - fills complete 1080px width
        - vertical crop only

    Text:
        uses 990px of available width.
    """

    # ========================================================
    # MEASURE TEXT PANEL
    # ========================================================

    temp_canvas = Image.new(
        "RGB",
        (
            CANVAS_WIDTH,
            CANVAS_HEIGHT,
        ),
        PANEL_COLOR,
    )

    temp_draw = ImageDraw.Draw(
        temp_canvas
    )

    layout = measure_normal_layout(
        temp_draw,
        text,
    )

    font = layout["font"]
    lines = layout["lines"]
    line_height = layout["line_height"]
    artwork_height = layout["artwork_height"]

    # ========================================================
    # PREPARE FULL-WIDTH ARTWORK
    # ========================================================

    artwork = prepare_normal_artwork(
        source_image,
        artwork_height,
    )

    # ========================================================
    # FINAL CANVAS
    # ========================================================

    final_canvas = Image.new(
        "RGB",
        (
            CANVAS_WIDTH,
            CANVAS_HEIGHT,
        ),
        PANEL_COLOR,
    )

    # ========================================================
    # ARTWORK
    # ========================================================

    final_canvas.paste(
        artwork,
        (
            0,
            0,
        ),
    )

    panel_y = artwork_height

    draw = ImageDraw.Draw(
        final_canvas
    )

    # ========================================================
    # HEADER
    # ========================================================

    header_font = load_font(
        HEADER_FONT_PATH,
        HEADER_FONT_SIZE,
    )

    logo = render_svg(
        LOGO_PATH,
        HEADER_LOGO_SIZE,
        HEADER_LOGO_SIZE,
    )

    header_text_width, header_text_height = (
        get_text_size(
            draw,
            HEADER_TEXT,
            header_font,
        )
    )

    header_width = (
        logo.width
        + HEADER_GAP
        + header_text_width
    )

    header_height = max(
        logo.height,
        header_text_height,
    )

    header_center_x = (
        CANVAS_WIDTH
        - header_width
    ) // 2

    header_top = (
        panel_y
        + PANEL_TOP_PADDING
    )

    logo_y = (
        header_top
        + (
            header_height
            - logo.height
        ) // 2
    )

    final_canvas.paste(
        logo,
        (
            header_center_x,
            logo_y,
        ),
        logo,
    )

    logo_center_y = (
        logo_y
        + logo.height / 2
    )

    draw.text(
        (
            header_center_x
            + logo.width
            + HEADER_GAP,
            logo_center_y,
        ),
        HEADER_TEXT,
        font=header_font,
        fill=HEADER_COLOR,
        anchor="lm",
    )

    # ========================================================
    # GOLD LINE
    # ========================================================

    gold_line_gap = 18
    gold_line_height = 1

    line_y = (
        header_top
        + header_height
        + gold_line_gap
    )

    line_margin = 45

    draw.rectangle(
        (
            line_margin,
            line_y,
            CANVAS_WIDTH
            - line_margin,
            line_y
            + gold_line_height,
        ),
        fill=ACCENT_COLOR,
    )

    # ========================================================
    # TEXT
    # ========================================================

    text_start_y = (
        line_y
        + gold_line_height
        + HEADER_TO_TEXT_GAP
    )

    current_y = text_start_y

    for line in lines:

        line_width, _ = get_text_size(
            draw,
            line,
            font,
        )

        x = (
            CANVAS_WIDTH
            - line_width
        ) / 2

        draw.text(
            (
                x,
                current_y,
            ),
            line,
            font=font,
            fill=TEXT_COLOR,
        )

        current_y += (
            line_height
            + LINE_SPACING
        )

    # ========================================================
    # CREDIT
    # ========================================================

    artwork_with_credit = artwork.convert(
        "RGBA"
    )

    artwork_with_credit = draw_credit(
        artwork_with_credit,
        credit,
    )

    final_canvas.paste(
        artwork_with_credit.convert(
            "RGB"
        ),
        (
            0,
            0,
        ),
    )

    # ========================================================
    # FINAL SIZE CHECK
    # ========================================================

    if final_canvas.size != (
        CANVAS_WIDTH,
        CANVAS_HEIGHT,
    ):

        raise ValueError(
            f"Normal slide has incorrect size: "
            f"{final_canvas.size}. "
            f"Expected 1080x1350."
        )

    # ========================================================
    # SAVE
    # ========================================================

    final_canvas.save(
        output_path,
        "JPEG",
        quality=95,
        optimize=True,
    )


# ============================================================
# LOAD CONTENT
# ============================================================

def load_content():

    if not CONTENT_FILE.exists():

        raise FileNotFoundError(
            f"Content file not found: "
            f"{CONTENT_FILE}"
        )

    with open(
        CONTENT_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        content = json.load(file)

    if "slides" not in content:

        raise ValueError(
            'content.json must contain a "slides" array.'
        )

    if not isinstance(
        content["slides"],
        list,
    ):

        raise ValueError(
            '"slides" must be an array.'
        )

    return content["slides"]


# ============================================================
# LOAD IMAGES
# ============================================================

def get_images():

    if not IMAGES_DIR.exists():

        raise FileNotFoundError(
            f"Images directory not found: "
            f"{IMAGES_DIR}"
        )

    images = [
        path
        for path in IMAGES_DIR.iterdir()
        if path.is_file()
        and path.suffix.lower()
        in SUPPORTED_EXTENSIONS
    ]

    def sort_key(path):

        try:

            return (
                0,
                int(path.stem),
            )

        except ValueError:

            return (
                1,
                path.name.lower(),
            )

    images.sort(
        key=sort_key
    )

    return images


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    slides = load_content()
    image_paths = get_images()

    if not image_paths:

        raise ValueError(
            "No supported images found "
            "in the images directory."
        )

    if len(image_paths) < len(slides):

        raise ValueError(
            f"Not enough images. "
            f"Found {len(image_paths)} images "
            f"but {len(slides)} slides are defined."
        )

    if len(image_paths) > len(slides):

        print(
            f"Warning: {len(image_paths)} images found "
            f"for {len(slides)} slides. "
            f"Only the first {len(slides)} images "
            f"will be processed."
        )

    for index, slide in enumerate(
        slides
    ):

        if not isinstance(
            slide,
            dict,
        ):

            raise ValueError(
                f"Slide {index} must be an object."
            )

        text = slide.get(
            "text",
            "",
        ).strip()

        credit = slide.get(
            "credit",
            "",
        ).strip()

        if not text:

            raise ValueError(
                f"Slide {index} has no text."
            )

        image_path = image_paths[index]

        print(
            f"Processing slide {index}: "
            f"{image_path.name}"
        )

        with Image.open(
            image_path
        ) as image:

            if index == 0:

                artwork = prepare_intro_artwork(
                    image
                )

            else:

                artwork = image.copy()

        output_path = (
            OUTPUT_DIR
            / f"{image_path.stem}.jpg"
        )

        # ====================================================
        # INTRO
        # ====================================================

        if index == 0:

            intro_config = slide.get(
                "intro",
                {},
            )

            if not isinstance(
                intro_config,
                dict,
            ):

                raise ValueError(
                    f'Slide {index} "intro" '
                    f"must be an object."
                )

            process_intro(
                artwork,
                output_path,
                text,
                credit,
                intro_config,
            )

        # ====================================================
        # NORMAL SLIDE
        # ====================================================

        else:

            process_normal_slide(
                artwork,
                output_path,
                text,
                credit,
            )

        print(
            f"Saved: {output_path}"
        )

    print()
    print("Done.")
