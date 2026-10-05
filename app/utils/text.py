import html
import re
from html.parser import HTMLParser

from app.constants.sources import REMOTE_HINTS


class _TextExtractor(HTMLParser):
    BLOCKS = {"p", "br", "li", "div", "ul", "ol", "h1", "h2", "h3", "h4", "tr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in self.BLOCKS:
            self.parts.append("\n- " if tag == "li" else "\n")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def strip_html(raw: str) -> str:
    """HTML -> readable plain text (unescapes entities, keeps list/paragraph breaks)."""
    if not raw:
        return ""
    parser = _TextExtractor()
    parser.feed(html.unescape(raw) if "&lt;" in raw else raw)
    text = "".join(parser.parts).replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n\s*\n+", "\n", text).strip()


def looks_remote(*texts: str) -> bool:
    return any(REMOTE_HINTS.search(t) for t in texts if t)
