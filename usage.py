from dash import Dash, html, dcc
from dash_mistletoe.dash_renderer import DashRenderer
import mistletoe
from mistletoe import span_token, block_token
from typing import Union

app = Dash(__name__)

markdown_to_render = """
# Heading level 1

I just love **bold text**.

> Dorothy followed her through many of the beautiful rooms in her castle.
"""


class MyDashRenderer(DashRenderer):

    def render_heading(self, token: block_token.Heading) -> Union[html.H1, html.H2, html.H3, html.H4, html.H5, html.H6]:
        '''Render headers

        `self.render_to_plain` takes children and joins them to text
        Using the children, we can create an id for each heading.
        This allows for quickly making a table of contents that
        will auto scroll to the destination
        '''
        heading = super().render_heading(token)
        id = self.render_to_plain(token).lower().replace(' ', '')
        heading.id = id
        return heading

    def render_strong(self, token: span_token.Strong) -> html.Strong:
        '''Rendering of bold components

        `self.render_inner` is an internal function for handling child elements
        Then we return our own predefined component with a new style
        '''
        children = self.render_inner(token)
        return html.Strong(children, style={'color': 'blue '})

    def render_quote(self, token: block_token.Quote) -> html.Blockquote:
        '''Render a markdown quote

        Call the super class DashRenderer to grab the basic html.Hx() object
        Then we can customize the style
        '''
        quote = super().render_quote(token)
        quote.style = {'color': 'red'}
        return quote


app.layout = html.Div(
    dcc.Tabs(
        [
            dcc.Tab(
                mistletoe.markdown(markdown_to_render, DashRenderer),
                label='Basic Example'
            ),
            dcc.Tab(
                mistletoe.markdown(markdown_to_render, MyDashRenderer),
                label='Extended'
            )
        ]
    )
)

if __name__ == '__main__':
    app.run(debug=True)
