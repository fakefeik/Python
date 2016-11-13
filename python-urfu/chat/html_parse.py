"""
Module for working with html tags
"""


def get_correct_html(text):
    """
    Returns the html page with correct tags placement and
    removed unsupported tags
    :param text: str
    :return: str
    """
    tags = ['b', 'i', 'u', 's', 'sup', 'sub']
    return correct_closing_tags(delete_unknown_tags(correct_closing_symbols(text), tags))


def delete_unknown_tags(text, tags):
    """
    Returns the html page with removed unsupported tags
    :param text: str
    :return: str
    """
    tags_to_delete = []
    for i in range(len(text)):
        if text[i] == '<':
            tag = text[i:text[i:].find('>') + i + 1]
            if tag.replace('/', '')[1:-1] not in tags:
                tags_to_delete.append((i, text[i:].find('>') + i + 1))
    for tag in reversed(tags_to_delete):
        text = text[:tag[0]] + text[tag[1]:]
    return text


def correct_closing_symbols(text):
    open_count = 0
    closing_count = 0
    for i in range(len(text)):
        if text[i] == '<':
            open_count += 1
        elif text[i] == '>':
            closing_count += 1
    delta = open_count - closing_count
    if delta > 0:
        for i in range(delta):
            text += '>'
    return text


def correct_closing_tags(text):
    """
    Returns the html page with corrected closing tags
    :param text: str
    :return: str
    """
    open_tags = {'b': 0, 'i': 0, 'u': 0, 's': 0, 'sup': 0, 'sub': 0}
    close_tags = {'b': 0, 'i': 0, 'u': 0, 's': 0, 'sup': 0, 'sub': 0}
    for i in range(len(text)):
        if text[i] == '<':
            closing = text[i:].find('>')
            if closing != -1:
                tag = text[i:text[i:].find('>') + i + 1]
                if tag[1] == '/':
                    close_tags[tag[2:-1]] += 1
                else:
                    open_tags[tag[1:-1]] += 1
    for tag in open_tags.keys():
        delta = open_tags[tag] - close_tags[tag]
        if delta > 0:
            for i in range(delta):
                text += '</{}>'.format(tag)

    return text

def has_any_text(text):
    return len(delete_unknown_tags(text, [])) > 0
