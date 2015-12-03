# -*- coding: utf-8 -*-
from client import plugin
from subprocess import call

class PowerPlugin(plugin.SpeechHandlerPlugin):
    def get_phrases(self):
        return [self.gettext("POWER OFF")]

    def handle(self, text, mic):

    output = self.gettext("Power will be switched off.")
    mic.say(output)

    call(["sudo", "reboot"])

    def is_valid(self, text):
        return any(p.lower() in text.lower() for p in self.get_phrases())
