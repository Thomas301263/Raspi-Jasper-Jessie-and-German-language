# -*- coding: utf-8 -*-
import urllib2
import re
import random
import bs4
from client import app_utils
from client import plugin
from semantic.numbers import NumberService

URL = 'http://news.ycombinator.com'


class HNStory:

    def __init__(self, title, URL):
        self.title = title
        self.URL = URL


def get_top_stories(maxResults=None):
    """
        Returns the top headlines from Hacker News.

        Arguments:
        maxResults -- if provided, returns a random sample of size maxResults
    """
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = urllib2.Request(URL, headers=hdr)
    page = urllib2.urlopen(req).read()
    soup = bs4.BeautifulSoup(page, 'html.parser')
    matches = soup.findAll('td', class_="title")
    matches = [m.a for m in matches if m.a and m.text != u'More']
    matches = [HNStory(m.text, m['href']) for m in matches]

    if maxResults:
        num_stories = min(maxResults, len(matches))
        return random.sample(matches, num_stories)

    return matches


class HackerNewsPlugin(plugin.SpeechHandlerPlugin):
    def get_priority(self):
        return 4

    def get_phrases(self):
        return ["HACKER", "NEWS", "YES", "NO", "FIRST", "SECOND", "THIRD"]

    def handle(self, text, mic):
        """
        Responds to user-input, typically speech text, with a sample of
        Hacker News's top headlines, sending them to the user over email
        if desired.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        """
        mic.say("Pulling up some stories.")
        stories = get_top_stories(maxResults=3)
        all_titles = '... '.join(str(idx + 1) + ") " +
                                 story.title for idx, story
                                 in enumerate(stories))

        def handle_response(text):

            def extract_ordinals(text):
                output = []
                service = NumberService()
                for w in text.split():
                    if w in service.__ordinals__:
                        output.append(service.__ordinals__[w])
                return [service.parse(w) for w in output]

            chosen_articles = extract_ordinals(text)
            send_all = not chosen_articles and app_utils.is_positive(text)

            if send_all or chosen_articles:
                mic.say("Sure, just give me a moment")

                if self.profile['prefers_email']:
                    body = "<ul>"

                def formatArticle(article):
                    tiny_url = app_utils.generate_tiny_URL(article.URL)

                    if self.profile['prefers_email']:
                        return "<li><a href=\'%s\'>%s</a></li>" % (
                            tiny_url, article.title)
                    else:
                        return article.title + " -- " + tiny_url

                for idx, article in enumerate(stories):
                    if send_all or (idx + 1) in chosen_articles:
                        article_link = formatArticle(article)

                        if self.profile['prefers_email']:
                            body += article_link
                        else:
                            if not app_utils.email_user(self.profile,
                                                        SUBJECT="",
                                                        BODY=article_link):
                                mic.say("I'm having trouble sending you " +
                                        "these articles. Please make sure " +
                                        "that your phone number and carrier " +
                                        "are correct on the dashboard.")
                                return

                # if prefers email, we send once, at the end
                if self.profile['prefers_email']:
                    body += "</ul>"
                    if not app_utils.email_user(self.profile,
                                                SUBJECT="From the Front " +
                                                        "Page of Hacker News",
                                                BODY=body):
                        mic.say("I'm having trouble sending you these " +
                                "articles. Please make sure that your " +
                                "phone number and carrier are correct " +
                                "on the dashboard.")
                        return

                mic.say("All done.")

            else:
                mic.say("OK I will not send any articles")

        if not self.profile['prefers_email'] and self.profile['phone_number']:
            mic.say("Here are some front-page articles. " +
                    all_titles + ". Would you like me to send you these? " +
                    "If so, which?")
            handle_response(mic.active_listen()[0])
        else:
            mic.say("Here are some front-page articles. " + all_titles)

    def is_valid(self, text):
        """
        Returns True if the input is related to Hacker News.

        Arguments:
        text -- user-input, typically transcribed speech
        """
        return bool(re.search(r'\b(hack(er)?|HN)\b', text, re.IGNORECASE))
