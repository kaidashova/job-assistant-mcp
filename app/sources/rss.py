import html
import xml.etree.ElementTree as ET

from app.utils.dates import parse_rfc822
from app.utils.text import strip_html


def parse_items(xml_text: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    items = []
    for item in root.iter("item"):
        items.append(
            {
                "title": html.unescape((item.findtext("title") or "").strip()),
                "link": (item.findtext("link") or "").strip(),
                "description": strip_html(item.findtext("description") or ""),
                "published": parse_rfc822(item.findtext("pubDate")),
                "categories": [c.text.strip() for c in item.findall("category") if c.text],
            }
        )
    return items
