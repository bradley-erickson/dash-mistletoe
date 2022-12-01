# dash_mistletoe

An extension of [mistletoe](https://github.com/miyuchina/mistletoe) that converts markdown into dash components.

## Purpose

While other Markdown parsers exist, they lack the ability to customize items at the component level.
This creates a barrier when we want to change styles or add ids to elements.
dash_mistletoe fixes this problem by providing a baseline framework for extending Markdown using [dash](https://dash.plotly.com/).

We build an extension of mistletoe; a fast, spec-compliant, and customizable Markdown parser; for dash components.
mistletoe parses to an Abstract Syntax Tree allowing us to extend easily.

## Install

To install and use, run

```bash
pip install dash-mistletoe
```

To clone and run locally, run

```bash
git clone https://github.com/bradley-erickson/dash-mistletoe
pip install -r requirements.txt
python usage.py
```

## Usage

First, mistletoe will parse `markdown_to_render` using the `DashRenderer`.
The output will contain all contents of the markdown wrapped in a Div.

```python
from dash import html
from dash_mistletoe.dash_renderer import DashRenderer
import mistletoe

markdown_to_render = """
# Heading level 1

I like markdown
"""

component = mistletoe.markdown(markdown_to_render, DashRenderer)
component
# html.Div([html.H1('Heading level 1'), html.P('I like markdown')])
```

## Extending Components

To extend a component, we will first make a sub class of `DashRenderer` to inherit all methods.
Next, we just need overwrite the methods we want to customize.
The possible methods to overwrite can be referenced in the code.

```python
class MyDashRenderer(DashRenderer):

    def render_heading(self, token):
```

Depending on what we need done with the content, we can create the component with the super class first.
Then, we change an attribute about it.
In the heading example, I add an `id` to each heading element.
Doing this allows for automatic scroll when changing the hash of the URL.
This is great for adding a table of contents to a blog post.

```python
class MyDashRenderer(DashRenderer):

    def render_heading(self, token):
        # fetch the super class heading first i.e. an html.Hx component
        heading = super().render_heading(token)
        # render the child (token) to as text (plain)
        id = self.render_to_plain(token).lower().replace(' ', '')
        # set the id and return
        heading.id = id
        return heading
```

You can also completely ignore the super class method and return something brand new.
For example, we can return a P element with a specific className instead of Strong one.
This allows us to handle how the Strong text looks with CSS instead.

```python
class MyDashRenderer(DashRenderer):

    def render_strong(self, token):
        # render the children (token)
        children = self.render_inner(token)
        return html.P(children, className='strong-text')
```
