"""
xkcdb.py - Pull a random (or specific) quote from the XKCDB
Copyright 2015 dgw
"""

from sopel import module, formatting
from lxml import html
import re


@module.commands('xkcdb')
def xkcdb(bot, trigger):
    qid = trigger.group(3)
    if qid:  # specific quote lookup
        page = html.parse('http://www.xkcdb.com/%s' % qid).getroot()
    else:  # random quote
        page = html.parse('http://www.xkcdb.com/random1').getroot()
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
    ratings = re.search('\(\+(?P<up>\d+)/\-(?P<down>\d+)\)', header.text_content())
    up = formatting.color('+%s' % ratings.group('up'), 'green')
    down = formatting.color('-%s' % ratings.group('down'), 'red')
    url = 'http://www.xkcdb.com/%s' % qid

    bot.say("XKCDB quote #%s (%s/%s) - %s" % (qid, up, down, url))
    if len(lines) <= 6:
        for line in lines:
            bot.say(line)
    else:
        for line in lines[:3]:
            bot.say(line)
        bot.say("[Quote truncated. Visit %s to read the rest.]" % url)
