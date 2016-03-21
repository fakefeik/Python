from urllib.request import urlopen
from xml.dom import minidom
import json


def whats_up_with_rouble():
    currency_url = "http://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
    currency_xml = minidom.parseString(urlopen(currency_url).read().decode('utf8'))
    needed_currencies = {"USD", "RUB"}
    currencies = {x.attributes["currency"].value: x.attributes["rate"].value for x in currency_xml.getElementsByTagName("Cube")
                  if "currency" in x.attributes and x.attributes["currency"].value in needed_currencies}
    return json.dumps({
        "USDRUB": float(currencies["RUB"]) / float(currencies["USD"]),
        "EURRUB": float(currencies["RUB"])
    })


def dvach_news():
    news_url = "http://2ch.hk/news/catalog.json"
    news_json = json.loads(urlopen(news_url).read().decode("utf8"))
    thread = sorted(news_json["threads"], key=lambda x: (-x["timestamp"], x["likes"], -x["posts_count"]))[-1]
    return json.dumps({
        "subject": thread["subject"],
        "comment": thread["comment"]
    }, ensure_ascii=False)


def hilarious_stuff():
    hilarious_url = "https://api.vkontakte.ru/method/wall.get.json?owner_id=-49268475&count=15"
    hilarious_json = json.loads(urlopen(hilarious_url).read().decode("utf8"))
    post = sorted(hilarious_json["response"][1:], key=lambda x: x["likes"]["count"])[-1]
    return json.dumps({
        "text": post["text"]
    }, ensure_ascii=False)


def main():
    print(whats_up_with_rouble())
    print(dvach_news())
    print(hilarious_stuff())


if __name__ == "__main__":
    main()
