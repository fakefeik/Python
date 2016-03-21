import re
import json
import html
from urllib.request import urlopen

try:
    with open('text.txt', 'r', encoding='utf8') as f:
        text_summary = f.read()
except FileNotFoundError:
    link = re.compile(r"<a.*?>.*?</a>")
    html_tag = re.compile(r"<.+?>")
    newline = re.compile(r"<br.*?>")
    board = "https://2ch.hk/po/catalog.json"
    data = json.loads(urlopen(board).read().decode('utf8'))
    threads = list(map(lambda x: x["num"], data["threads"]))
    text_summary = ''
    for t in threads:
        thread = "https://2ch.hk/po/res/{thread}.json".format(thread=t)

        data = json.loads(urlopen(thread).read().decode('utf8'))

        text = "\n".join(list(map(lambda x: x["comment"], data["threads"][0]["posts"])))
        text = re.sub(link, '', text)
        text = re.sub(newline, '. ', text)
        text = re.sub(html_tag, '', text)

        text = html.unescape(text)
        text = text.replace('>', '')

        text_summary += text + '\n'
        print(t + " done")

    with open('text.txt', 'w+', encoding='utf8') as f:
        f.write(text_summary)

dictionary = {}
for line in text_summary.split(';\n'):
    words = line.split()
    for i in range(len(words)):
        if i < len(words) - 1 and words[i][-1] not in "().?!":
            if words[i] not in dictionary:
                dictionary[words[i]] = [words[i + 1]]
            else:
                dictionary[words[i]].append(words[i + 1])

print(dictionary)

with open('sample.json', 'w+', encoding='utf8') as f:
    json.dump(dictionary, f, ensure_ascii=False)

