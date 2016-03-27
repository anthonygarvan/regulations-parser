from functools import partial

from lxml import etree


class XMLBuilder(object):
    """A small DSL for generating XML. For example,
        with XMLBuilder("ROOT") as ctx:
            ctx.P("Some Text")
            with ctx.SECT(level=4):
                ctx.P("More")

        ctx.xml_str:
        <ROOT>
            <P>Some Text</P>
            <SECT level="4">
                <P>More</P>
            </SECT>
        </ROOT>"""
    def __init__(self, *args, **kwargs):
        self.cursor = etree.Element('ROOT')
        self.child(*args, **kwargs)

    def child(self, tag, _text=None, **kwargs):
        """Add a child to our xml."""
        # For backwards compatibility. To be removed soon
        if '_xml' in kwargs:
            attrs = ['{}="{}"'.format(key, value)
                     for key, value in kwargs.items() if key != '_xml']
            attr_str = ' '.join(attrs)
            el = etree.fromstring(u'<{0} {1}>{2}</{0}>'.format(
                tag, attr_str, kwargs['_xml']))
        else:
            el = etree.Element(tag)
            for key, value in sorted(kwargs.items()):
                el.set(key, str(value))
            el.text = _text or ''
        self.cursor.append(el)
        return self

    def __getattr__(self, name):
        """Handle unknown attributes by calling `self.child`"""
        return partial(self.child, name)

    def __enter__(self):
        """Focus on the most recently added child"""
        self.cursor = self.cursor[-1]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Remove focus"""
        self.cursor = self.cursor.getparent()
        return False

    @property
    def xml(self):
        return self.cursor[-1]

    @property
    def xml_str(self):
        return etree.tostring(self.xml)
