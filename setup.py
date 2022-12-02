from setuptools import setup

setup(
    name='dash_mistletoe',
    version='0.2.4',
    author='Bradley Erickson',
    author_email='bbwe24@gmail.com',
    url='https://github.com/bradley-erickson/dash-mistletoe',
    license='MIT',
    description='A wrapper of mistletoe to output Markdown as dash components',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    packages=['dash_mistletoe'],
    install_requires=[
        'mistletoe==0.9.0',
        'dash >= 2.1.0',
    ]
)
