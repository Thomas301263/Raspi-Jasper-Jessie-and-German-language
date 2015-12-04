# -*- coding: utf-8 -*-
import subprocess
from client import plugin

class PowerPlugin(plugin.SpeechHandlerPlugin):
    def get_phrases(self):
        return [self.gettext('POWER OFF')]

    def handle(self, text, mic):
            mic.say(self.gettext("Switch Power off now."))
            subprocess.call(["sh", "power"])

    def is_valid(self, text):
        return (self.gettext('POWER').upper() in text.upper())
