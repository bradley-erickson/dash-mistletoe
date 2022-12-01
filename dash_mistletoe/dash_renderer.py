'''
dash renderer for mistletoe
'''

from dash import html
from mistletoe.base_renderer import BaseRenderer
from mistletoe import block_token, span_token
from urllib.parse import quote
from typing import Union


class DashRenderer(BaseRenderer):
    def __init__(self, *extras):
        self._suppress_ptag_stack = [False]
        super().__init__(*extras)

    def __exit__(self, *args):
        super().__exit__(*args)

    def render_inner(self, token) -> dict:
        return [i for i in map(self.render, token.children)]

    def render_to_plain(self, token) -> str:
        if hasattr(token, 'children'):
            inner = [self.render_to_plain(child) for child in token.children]
            return ''.join(inner)
        return token.content

    def render_strong(self, token: span_token.Strong) -> html.Strong:
        return html.Strong(self.render_inner(token))

    def render_emphasis(self, token: span_token.Emphasis) -> html.Em:
        return html.Em(self.render_inner(token))

    def render_inline_code(self, token: span_token.InlineCode) -> html.Code:
        inner = token.children[0].content
        return html.Code(inner)

    def render_strikethrough(self, token: span_token.Strikethrough) -> html.Del:
        return html.Del(self.render_inner(token))

    def render_image(self, token: span_token.Image) -> html.Img:
        return html.Img(src=token.src, alt=self.render_to_plain(token), title=token.title if token.title else '')

    def render_link(self, token: span_token.Link) -> html.A:
        template = html.A(
            self.render_inner(token),
            href=self.escape_url(token.target),
            title=token.title if token.title else ''
        )
        return template

    def render_auto_link(self, token: span_token.AutoLink) -> html.A:
        template = html.A(
            self.render_inner(token),
            href=f'mailto:{token.target}' if token.mailto else self.escape_url(token.target),
            title=token.title if token.title else ''
        )
        return template

    def render_escape_sequence(self, token: span_token.EscapeSequence) -> str:
        return self.render_inner(token)

    def render_raw_text(self, token: span_token.RawText) -> str:
        return token.content

    def render_heading(self, token: block_token.Heading) -> Union[html.H1, html.H2, html.H3, html.H4, html.H5, html.H6]:
        inner = self.render_inner(token)
        if token.level == 1:
            template = html.H1
        elif token.level == 2:
            template = html.H2
        elif token.level == 3:
            template = html.H3
        elif token.level == 4:
            template = html.H4
        elif token.level == 5:
            template = html.H5
        elif token.level == 6:
            template = html.H6
        return template(inner)

    def render_quote(self, token: block_token.Quote) -> html.Blockquote:
        self._suppress_ptag_stack.append(False)
        children = [self.render(child) for child in token.children]
        self._suppress_ptag_stack.pop()
        return html.Blockquote(children)

    def render_paragraph(self, token: block_token.Paragraph) -> Union[str, html.P]:
        if self._suppress_ptag_stack[-1]:
            return self.render_inner(token)
        return html.P(self.render_inner(token))

    def render_block_code(self, token: block_token.BlockCode) -> html.Pre:
        template = html.Pre(
            html.Code(
                token.children[0].content,
                className=f'language-{token.language}' if token.language else ''
            )
        )
        return template

    def render_list(self, token: block_token.List) -> Union[html.Ol, html.Ul]:
        inner = [self.render(child) for child in token.children]
        if token.start is not None:
            template = html.Ol(inner, start=token.start if token.start != 1 else '')
        else:
            template = html.Ul(inner)
        return template

    def render_list_item(self, token: block_token.ListItem) -> html.Li:
        if len(token.children) == 0:
            return html.Li()
        inner = [self.render(child) for child in token.children]
        return html.Li(inner)

    def render_table(self, token: block_token.Table) -> html.Table:
        header = hasattr(token, 'header')
        if header:
            head_inner = self.render_table_row(token.header, is_header=True)
            head_rendered = html.Thead(head_inner)
        body_inner = self.render_inner(token)
        body_rendered = html.Tbody(body_inner)
        return html.Table([head_rendered, body_rendered] if header else body_rendered)

    def render_table_row(self, token: block_token.TableRow, is_header=False) -> html.Tr:
        inner = [self.render_table_cell(child, is_header) for child in token.children]
        return html.Tr(inner)

    def render_table_cell(self, token: block_token.TableCell, in_header=False) -> Union[html.Th, html.Td]:
        tag = html.Th if in_header else html.Td
        return tag(self.render_inner(token))

    @staticmethod
    def render_thematic_break(token: block_token.ThematicBreak) -> html.Hr():
        return html.Hr()

    @staticmethod
    def render_line_break(token: span_token.LineBreak) -> Union[str, html.Br]:
        return html.Br()

    def render_document(self, token: block_token.Document) -> html.Div:
        self.footnotes.update(token.footnotes)
        return html.Div([self.render(child) for child in token.children])

    @staticmethod
    def escape_url(raw: str) -> str:
        """
        Escape urls to prevent code injection craziness. (Hopefully.)
        """
        return quote(raw, safe='/#:()*?=%@+,&;')
