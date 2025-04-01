"""sopel-xkcdb

XKCDB quotes plugin for Sopel IRC bots

Copyright (c) 2015-2025 dgw

Licensed under the Eiffel Forum License 2.0
"""
from __future__ import annotations

from io import StringIO
import re

from lxml import html
import requests

from sopel import plugin, formatting


@plugin.command('xkcdb')
def xkcdb(bot, trigger):
    if qid := trigger.group(3):  # specific quote lookup
        r = requests.get('https://www.xkcdb.com/%s' % qid)
    else:  # random quote
        r = requests.get('https://www.xkcdb.com/random1')

    page = html.parse(StringIO(r.text)).getroot()
    try:
        quoteblock = page.cssselect('p.quoteblock')[0]
    except IndexError:
        bot.say("XKCDB quote %snot found!" % ("#%s " % qid) if qid else "")
        return

    header = quoteblock.cssselect('span.quotehead')[0]
    quote = quoteblock.cssselect('span.quote')[0]
    for br in quote.xpath('*//br'):
        br.tail = '\n' + br.tail if br.tail else '\n'

    lines = quote.text_content().split('\n')
    qid = int(header.cssselect('.idlink')[0].text_content()[1:])
    ratings = re.search(r'\(\+(?P<up>\d+)/\-(?P<down>\d+)\)', header.text_content())
    up = formatting.color('+%s' % ratings.group('up'), 'green')
    down = formatting.color('-%s' % ratings.group('down'), 'red')
    url = 'https://www.xkcdb.com/%s' % qid

    bot.say("XKCDB quote #%s (%s/%s) - %s" % (qid, up, down, url))
    if len(lines) <= 6:
        for line in lines:
            bot.say(line)
    else:
        for line in lines[:3]:
            bot.say(line)
        bot.say("[Quote truncated. Visit %s to read the rest.]" % url)
