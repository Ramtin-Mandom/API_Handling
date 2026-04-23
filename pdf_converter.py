from pathlib import Path
from typing import List, Tuple

from pypdf import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


PAGE_WIDTH, PAGE_HEIGHT = letter
LEFT_MARGIN = 54
RIGHT_MARGIN = 54
TOP_MARGIN = 54
BOTTOM_MARGIN = 54
USABLE_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN


def pdf_to_text(pdf_path: str | Path) -> str:
    """
    Extract readable text from a PDF file and return it as one string.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Input file must be a .pdf file.")

    reader = PdfReader(str(pdf_path))
    pages: List[str] = []

    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            pages.append(text.strip())

    if not pages:
        raise ValueError("No readable text was found in the PDF.")

    return "\n\n".join(pages)


def save_pdf_as_text(pdf_path: str | Path, output_txt_path: str | Path) -> Path:
    """
    Extract text from a PDF and save it to a text file.
    """
    output_txt_path = Path(output_txt_path)
    text = pdf_to_text(pdf_path)
    output_txt_path.write_text(text, encoding="utf-8")
    return output_txt_path


def text_to_pdf(text: str, output_pdf_path: str | Path) -> Path:
    """
    Convert text into a presentable PDF using simple markdown-like patterns.

    Supported patterns:
    - # Main title
    - ## Section heading
    - ### Subheading
    - - Bullet item
    - * Bullet item
    - 1. Numbered item
    - --- Horizontal separator

    Everything else is treated as paragraph text.
    """
    output_pdf_path = Path(output_pdf_path)

    c = canvas.Canvas(str(output_pdf_path), pagesize=letter)
    y = PAGE_HEIGHT - TOP_MARGIN

    for raw_line in text.splitlines():
        line_type, content = classify_line(raw_line)

        if line_type == "blank":
            y = ensure_space(c, y, 18)
            y -= 10

        elif line_type == "separator":
            y = ensure_space(c, y, 24)
            c.setLineWidth(0.7)
            c.line(LEFT_MARGIN, y, PAGE_WIDTH - RIGHT_MARGIN, y)
            y -= 16

        elif line_type == "h1":
            y = ensure_space(c, y, 34)
            y = draw_wrapped_block(
                c, content, LEFT_MARGIN, y,
                "Helvetica-Bold", 18, 22, 8
            )

        elif line_type == "h2":
            y = ensure_space(c, y, 28)
            y = draw_wrapped_block(
                c, content, LEFT_MARGIN, y,
                "Helvetica-Bold", 15, 19, 6
            )

        elif line_type == "h3":
            y = ensure_space(c, y, 24)
            y = draw_wrapped_block(
                c, content, LEFT_MARGIN, y,
                "Helvetica-Bold", 12, 16, 4
            )

        elif line_type == "bullet":
            y = ensure_space(c, y, 22)
            y = draw_wrapped_block(
                c, f"• {content}", LEFT_MARGIN + 10, y,
                "Helvetica", 11, 15, 2,
                max_width=USABLE_WIDTH - 10
            )

        elif line_type == "numbered":
            y = ensure_space(c, y, 22)
            y = draw_wrapped_block(
                c, content, LEFT_MARGIN + 10, y,
                "Helvetica", 11, 15, 2,
                max_width=USABLE_WIDTH - 10
            )

        else:
            y = ensure_space(c, y, 26)
            y = draw_wrapped_block(
                c, content, LEFT_MARGIN, y,
                "Helvetica", 11, 16, 6
            )

    c.save()
    return output_pdf_path


def txt_file_to_pdf(input_txt_path: str | Path, output_pdf_path: str | Path) -> Path:
    """
    Read a text file and convert it to a presentable PDF.
    """
    input_txt_path = Path(input_txt_path)

    if not input_txt_path.is_file():
        raise FileNotFoundError(f"Text file not found: {input_txt_path}")

    text = input_txt_path.read_text(encoding="utf-8")
    return text_to_pdf(text, output_pdf_path)


def classify_line(line: str) -> Tuple[str, str]:
    stripped = line.strip()

    if not stripped:
        return "blank", ""

    if stripped == "---":
        return "separator", ""

    if stripped.startswith("### "):
        return "h3", stripped[4:].strip()

    if stripped.startswith("## "):
        return "h2", stripped[3:].strip()

    if stripped.startswith("# "):
        return "h1", stripped[2:].strip()

    if stripped.startswith("- "):
        return "bullet", stripped[2:].strip()

    if stripped.startswith("* "):
        return "bullet", stripped[2:].strip()

    if looks_numbered_list(stripped):
        return "numbered", stripped

    return "paragraph", stripped


def looks_numbered_list(text: str) -> bool:
    parts = text.split(".", 1)
    return len(parts) == 2 and parts[0].isdigit() and parts[1].strip() != ""


def wrap_text(text: str, font_name: str, font_size: int, max_width: float) -> List[str]:
    words = text.split()
    if not words:
        return [""]

    lines: List[str] = []
    current = words[0]

    for word in words[1:]:
        candidate = f"{current} {word}"
        if stringWidth(candidate, font_name, font_size) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word

    lines.append(current)
    return lines


def draw_wrapped_block(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    font_name: str,
    font_size: int,
    line_gap: int,
    extra_space_after: int = 0,
    max_width: float = USABLE_WIDTH,
) -> float:
    lines = wrap_text(text, font_name, font_size, max_width)
    c.setFont(font_name, font_size)

    for line in lines:
        c.drawString(x, y, line)
        y -= line_gap

    y -= extra_space_after
    return y


def ensure_space(c: canvas.Canvas, y: float, needed_height: int) -> float:
    if y - needed_height <= BOTTOM_MARGIN:
        c.showPage()
        return PAGE_HEIGHT - TOP_MARGIN
    return y


if __name__ == "__main__":
    pass
