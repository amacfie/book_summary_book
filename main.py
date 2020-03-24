import itertools
import requests

# sudo apt install pandoc
# pip3 install pyyaml mwparserfromhell pyandoc
import mwparserfromhell
import pandoc
import yaml

def get_summary_md(wikipedia_slug: str, wikipedia_section: str):
    response = requests.get(
        'https://en.wikipedia.org/w/api.php',
        params={
            'action': 'query',
            'format': 'json',
            'titles': wikipedia_slug,
            'prop': 'extracts',
            'explaintext': True,
        },
    ).json()
    text = next(iter(response['query']['pages'].values()))['extract']
    wikicode = mwparserfromhell.parse(text)
    section = wikicode.get_sections(
        levels=[2],
        matches=wikipedia_section,
        include_headings=False,
    )[0].strip()

    doc = pandoc.Document()
    doc.mediawiki = section.encode('utf-8')
    return doc.markdown.decode()

with open('books.yaml') as f:
    books = yaml.load(f)

for book in books:
    print('Processing {}'.format(book['title']))
    book['summary'] = get_summary_md(
        book['wikipedia slug'], book['wikipedia section']
    )

books.sort(key=lambda b: (b['author'].split()[-1], b['year']))

out = '''---
title: Book Summaries
author: Andrew MacFie
rights:  Creative Commons Attribution-ShareAlike 3.0
language: en-US
...

# Preface

Creative Commons Attribution-ShareAlike 3.0

Generated by <https://github.com/amacfie/book_summary_book>

1.  ToC
{:toc}


'''

for author, author_books in itertools.groupby(
    books, lambda b: b['author']
):
    out += '# {}\n\n'.format(author)
    for book in author_books:
        out += '## {} ({})\n\n'.format(book['title'], book['year'])
        out += 'Taken from '
        out += '<https://en.wikipedia.org/wiki/{}>'.format(
            book['wikipedia slug'])
        out += '\n\n'
        out += book['summary']
        out += '\n\n'

with open('index.md', 'w') as f:
    f.write(out)

