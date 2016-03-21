import json
import re
import urllib.request
from random import sample
from html import unescape


chars = list(map(chr, range(65, 91)))
popular_regex = re.compile(r'<a class="popular" href="(.+?)">(.+?)</a>')
popular_link = "http://urbandictionary.com/popular.php?character={char}"
base_link = "http://urbandictionary.com"
meaning_regex = re.compile(r"<div class='meaning'>\n(.+?)\n</div>")
open_tag_regex = re.compile(r'<.+?>')
close_tag_regex = re.compile(r'</.+?>')
to_delete_regex = re.compile(r'<a.+?>.+?</a>')
items_to_sample = 5


def parse_urban(refresh=False):
    try:
        with open('words.json', 'r') as f:
            definitions = json.load(f)
        if refresh:
            raise FileNotFoundError()
    except FileNotFoundError:
        definitions = {}
        links = []
        for char in chars:
            link = popular_link.format(char=char)
            data = urllib.request.urlopen(link).read().decode("utf8")
            found = map(lambda x: (x[0], unescape(x[1])), sample(re.findall(popular_regex, data), items_to_sample))
            links += found
            print("{char} done!".format(char=char))
        for link, word in links:
            data = urllib.request.urlopen(base_link + link).read().decode("utf8")
            definition = re.findall(meaning_regex, data)[0]
            definition = re.sub(to_delete_regex, '', definition)
            definition = re.sub(open_tag_regex, '', definition)
            definition = re.sub(close_tag_regex, '', definition)
            definitions[word] = unescape(definition)
            print("{word} done!".format(word=word))
        print("Done!")

        with open('words.json', 'w+') as f:
            f.write(json.dumps(definitions, ensure_ascii=False))
    return definitions
