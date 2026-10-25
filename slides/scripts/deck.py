"""Meeting slides from the deck template in files/ (its theme and layouts)."""
from pathlib import Path

from pptx import Presentation
from pptx.enum.dml import MSO_THEME_COLOR
from pptx.util import Pt

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "files/AI Alignemnt Emotions all slides.pptx"

LEFT, WIDTH = 311700, 8520600
BODY_TOP = 1152475


def set_text(shape, text, level=0, new_paragraph=False):
    tf = shape.text_frame
    p = tf.add_paragraph() if new_paragraph else tf.paragraphs[0]
    p.text, p.level = text, level
    for run in p.runs:
        run.font.color.theme_color = MSO_THEME_COLOR.DARK_1


def new_deck(template=TEMPLATE):
    prs = Presentation(template)
    slide_ids = prs.slides._sldIdLst
    for slide_id in list(slide_ids):
        prs.part.drop_rel(slide_id.rId)
        slide_ids.remove(slide_id)
    return prs


def title_slide(prs, title, date):
    s = prs.slides.add_slide(prs.slide_layouts[0])
    set_text(s.placeholders[0], title)
    set_text(s.placeholders[1], date)
    return s


def slide(prs, title, bullets, figure=None, layout="below", body_height=1050000):
    """layout="below": bullets longer than one line run under the figure; "right": figure on the right."""
    s = prs.slides.add_slide(prs.slide_layouts[2])
    set_text(s.placeholders[0], title)
    body = s.placeholders[1]
    for i, b in enumerate(bullets):
        level, text = b if isinstance(b, tuple) else (0, b)
        set_text(body, text, level, new_paragraph=i > 0)
    if figure is None:
        return s

    path = str(ROOT / figure)
    if layout == "right":
        body.left, body.top, body.width, body.height = 278775, BODY_TOP, 3985200, 3416400
        pic = s.shapes.add_picture(path, 4436675, 0, width=4395625)
        pic.top = max(773526, (prs.slide_height - pic.height) // 2)
    else:
        body.left, body.top, body.width, body.height = LEFT, BODY_TOP, WIDTH, body_height
        top = BODY_TOP + body_height + 50000
        pic = s.shapes.add_picture(path, LEFT, top)
        scale = min(WIDTH / pic.width, (prs.slide_height - top - 120000) / pic.height)
        pic.width, pic.height = int(pic.width * scale), int(pic.height * scale)
        pic.left = (prs.slide_width - pic.width) // 2
    return s


def table_slide(prs, title, header, rows, bullets=(), body_height=600000, font_size=12):
    s = prs.slides.add_slide(prs.slide_layouts[2])
    set_text(s.placeholders[0], title)
    body = s.placeholders[1]
    if bullets:
        for i, b in enumerate(bullets):
            level, text = b if isinstance(b, tuple) else (0, b)
            set_text(body, text, level, new_paragraph=i > 0)
        body.left, body.top, body.width, body.height = LEFT, BODY_TOP, WIDTH, body_height
        top = BODY_TOP + body_height + 80000
    else:
        body._element.getparent().remove(body._element)
        top = BODY_TOP
    row_height = Pt(font_size * 2.1)
    table = s.shapes.add_table(len(rows) + 1, len(header), LEFT, top, WIDTH, row_height * (len(rows) + 1)).table
    for r, values in enumerate([header] + list(rows)):
        table.rows[r].height = row_height
        for c, value in enumerate(values):
            cell = table.cell(r, c)
            cell.text = str(value)
            for p in cell.text_frame.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(font_size)
    return s
