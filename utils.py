import re
from unicodedata import normalize

import jinja2


def slugify(text):
    """
    Convert unicode text to lowercase ASCII and convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    """
    text = normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub('[^\w\s-]', '', text).strip().lower()
    text = re.sub('[-\s]+', '-', text)
    return text


def jinjago(text, context):
    return jinja2.Template(text).render(context)
