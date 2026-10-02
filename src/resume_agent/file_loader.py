from pathlib import Path
from pypdf import PdfReader
from docx import Document


def read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return "\n".join(pages)


def read_docx(path: Path) -> str:
    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs)


def read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_resume(path: Path) -> str:
    """
    根据文件后缀自动选择读取方式。
    支持：.txt / .pdf / .docx
    """
    if not path.exists():
        raise FileNotFoundError(f"文件不存在：{path}")

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return read_pdf(path)
    elif suffix == ".docx":
        return read_docx(path)
    elif suffix == ".txt":
        return read_txt(path)
    else:
        raise ValueError(f"不支持的文件格式：{suffix}")


def find_resume(data_dir: Path) -> Path:
    """
    在 data/ 目录里自动找简历文件。
    优先级：pdf > docx > txt
    """
    for name in ["resume.pdf", "resume.docx", "resume.txt"]:
        candidate = data_dir / name
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"在 {data_dir} 里没找到 resume.pdf / resume.docx / resume.txt"
    )