from unittest import TestCase, mock
from dash_mistletoe.dash_renderer import DashRenderer
from dash import html
import json
import plotly
from typing import Any


class TestRenderer(TestCase):
    def setUp(self):
        self.renderer = DashRenderer()
        self.renderer.render_inner = mock.Mock(return_value='inner')
        self.renderer.__enter__()
        self.addCleanup(self.renderer.__exit__, None, None, None)

    def assertEqual(self, first: Any, second: Any, msg: Any = ...) -> None:
        f = json.loads(json.dumps(first, cls=plotly.utils.PlotlyJSONEncoder))
        s = json.loads(json.dumps(second, cls=plotly.utils.PlotlyJSONEncoder))
        return super().assertEqual(f, s, msg)

    def _test_token(self, token_name, output, children=True,
                    without_attrs=None, **kwargs):
        render_func = self.renderer.render_map[token_name]
        children = mock.MagicMock(spec=list) if children else None
        mock_token = mock.Mock(children=children, **kwargs)
        without_attrs = without_attrs or []
        for attr in without_attrs:
            delattr(mock_token, attr)
        self.assertEqual(render_func(mock_token), output)


class TestDashRenderer(TestRenderer):
    def test_strong(self):
        self._test_token('Strong', html.Strong('inner'))

    def test_emphasis(self):
        self._test_token('Emphasis', html.Em('inner'))

    def test_inline_code(self):
        from mistletoe.span_token import tokenize_inner
        rendered = self.renderer.render(tokenize_inner('`foo`')[0])
        self.assertEqual(rendered, html.Code('foo'))
        rendered = self.renderer.render(tokenize_inner('`` \\[\\` ``')[0])
        self.assertEqual(rendered, html.Code('\\[\\`'))

    def test_strikethrough(self):
        self._test_token('Strikethrough', html.Del('inner'))

    def test_image(self):
        output = html.Img(src='src', alt='', title='title')
        self._test_token('Image', output, src='src', title='title')

    def test_link(self):
        output = html.A('inner', href='target', title='title')
        self._test_token('Link', output, target='target', title='title')

    def test_autolink(self):
        output = html.A('inner', href='link', title='title')
        self._test_token('AutoLink', output, target='link', mailto=False, title='title')

    def test_escape_sequence(self):
        self._test_token('EscapeSequence', 'inner')

    def test_raw_text(self):
        self._test_token('RawText', 'john & jane', children=False, content='john & jane')

    def test_heading(self):
        output = html.H3('inner')
        self._test_token('Heading', output, level=3)

    def test_quote(self):
        output = html.Blockquote([])
        self._test_token('Quote', output)

    def test_paragraph(self):
        self._test_token('Paragraph', html.P('inner'))

    def test_block_code(self):
        from mistletoe.block_token import tokenize
        rendered = self.renderer.render(tokenize(['```sh\n', 'foo\n', '```\n'])[0])
        output = html.Pre(html.Code('foo\n', className='language-sh'))
        self.assertEqual(rendered, output)

    def test_block_code_no_language(self):
        from mistletoe.block_token import tokenize
        rendered = self.renderer.render(tokenize(['```\n', 'foo\n', '```\n'])[0])
        output = html.Pre(html.Code('foo\n', className=''))
        self.assertEqual(rendered, output)

    def test_list(self):
        output = html.Ul([])
        self._test_token('List', output, start=None)

    def test_list_item(self):
        output = html.Li()
        self._test_token('ListItem', output)

    def test_table_with_header(self):
        func_path = 'dash_mistletoe.dash_renderer.DashRenderer.render_table_row'
        with mock.patch(func_path, autospec=True) as mock_func:
            mock_func.return_value = 'row'
            output = html.Table(
                [
                    html.Thead('row'),
                    html.Tbody('inner')
                ]
            )
            self._test_token('Table', output)

    def test_table_without_header(self):
        func_path = 'dash_mistletoe.dash_renderer.DashRenderer.render_table_row'
        with mock.patch(func_path, autospec=True) as mock_func:
            mock_func.return_value = 'row'
            output = html.Table(html.Tbody('inner'))
            self._test_token('Table', output, without_attrs=['header'])

    def test_table_row(self):
        self._test_token('TableRow', html.Tr([]))

    def test_table_cell(self):
        output = html.Td('inner')
        self._test_token('TableCell', output)

    def test_thematic_break(self):
        self._test_token('ThematicBreak', html.Hr(), children=False)

    def test_line_break(self):
        self._test_token('LineBreak', html.Br(), children=False, soft=False)

    def test_document(self):
        self._test_token('Document', html.Div([]), footnotes={})
