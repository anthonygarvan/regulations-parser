from regparser.layer.key_terms import (
    KeyTerms as BaseKeyTerms, keyterm_in_text)
from regparser.layer.preamble.paragraph_markers import marker_of


class KeyTerms(BaseKeyTerms):
    """The CFR KeyTerms layer does _almost_ exactly what we want."""

    @classmethod
    def keyterm_in_node(cls, node):
        """Find the keyterm in a node. Requires a paragraph marker be present
        (to limit false positives)"""
        marker = marker_of(node)
        if marker:
            tagged = (getattr(node, 'tagged_text', None) or '')
            tagged = tagged.replace(marker, '', 1).strip()
            return keyterm_in_text(tagged)
