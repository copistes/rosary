#!/bin/env python3

import os
import sys
import json
import argparse
from datetime import date
#from rich import print
from rich.console import Console
import openai
from pyliturgical import calendar
import gettext
import importlib

# setup translation
locale_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "locales")
translate = gettext.translation('messages', localedir=locale_path, fallback=True)
translate.install()

def wait_for_key():
    try:
        input("")
    except KeyboardInterrupt:
        raise SystemExit


console = Console(highlight=False)

CONFIG_FILE = os.path.expanduser("~/.rosary")

DEFAULT_CONFIG = {
    "last": None,
    "offset": 0,
    "prayed": [],
    "openai": None,
    "sermons": {}
}

REFDATE = date.today()


def todaycode():
    return REFDATE.strftime("%Y%m%d")

def dayname():
    return REFDATE.strftime("%A")

def dayofweek():
    return int(REFDATE.strftime("%w"))



def INIT_pearls():
    pearl_small = [ u'\u2460', u'\u2461', u'\u2462', u'\u2463', u'\u2464', u'\u2465',
                   u'\u2466', u'\u2467', u'\u2468', u'\u2469']
    pearl_large = u'\u24FF'
    cross = u'\u271D'

    ret=[cross] + pearl_small[0:3]
    m = [pearl_large]*3 + pearl_small
    ret += 5*m

    return ret

PEARLS = INIT_pearls()


def MYSTERIES_to_rosary(mystery_list):
    INITIAL = [_("Credo")] + [_("Hail Mary")]*3
    PREMISTERY = [_("Glory to the Father"), _("Our Father")]
    TENTH = [_("Hail Mary")]*10

    ret = INITIAL

    for m in mystery_list:
        ret = ret + PREMISTERY + [m] + TENTH

    return ret


JOYFUL_MYSTERIES = MYSTERIES_to_rosary([_("The Annunciation of the Angel Gabriel to Mary"),
                                        _("The Visitation of Mary to Elizabeth"),
                                        _("The Birth of Jesus in Bethlehem of Judea"),
                                        _("The Presentation of Jesus in the Temple"),
                                        _("The Finding of Jesus in the Temple")])

LUMINOUS_MYSTERIES = MYSTERIES_to_rosary([_("Jesus' Baptism in the Jordan"),
                                          _("The Wedding at Cana"),
                                          _("The Proclamation of the Kingdom"),
                                          _("The Transfiguration"),
                                          _("The Institution of the Eucharist")])

SORROWFUL_MYSTERIES = MYSTERIES_to_rosary([_("The Agony of Jesus in the Garden of Gethsemane"),
                                           _("The Scourging of Jesus at the Pillar"),
                                           _("The Crowning of Jesus with Thorns"),
                                           _("The Carrying of the Cross"),
                                           _("The Crucifixion and Death of Jesus")])

GLORIOUS_MYSTERIES = MYSTERIES_to_rosary([_("The Resurrection of Jesus"),
                                          _("The Ascension of Jesus into Heaven"),
                                          _("The Descent of the Holy Spirit at Pentecost"),
                                          _("The Assumption of Mary into Heaven"),
                                          _("The Coronation of Our Lady in Heaven")])


DAY_TO_ROSARIES = {
    # Sunday
    0: GLORIOUS_MYSTERIES,
    # Monday
    1: JOYFUL_MYSTERIES,
    # Tuesday
    2: SORROWFUL_MYSTERIES,
    # Wednesday
    3: GLORIOUS_MYSTERIES,
    # Thursday
    4: LUMINOUS_MYSTERIES,
    # Friday
    5: SORROWFUL_MYSTERIES,
    # Saturday
    6: JOYFUL_MYSTERIES
}

DAY_TO_ROSARIES_NAME = {
    # Sunday
    0: _("Glorious Mysteries"),
    # Monday
    1: _("Joyful Mysteries"),
    # Tuesday
    2: _("Sorrowful Mysteries"),
    # Wednesday
    3: _("Glorious Mysteries"),
    # Thursday
    4: _("Luminous Mysteries"),
    # Friday
    5: _("Sorrowful Mysteries"),
    # Saturday
    6: _("Joyful Mysteries")
}


def translate_day(day):
    DAY_TRANSLATOR = {
        "Monday" : _("Monday"),
        "Tuesday" : _("Tuesday"),
        "Wednesday" : _("Wednesday"),
        "Thursday" : _("Thursday"),
        "Friday" : _("Friday"),
        "Saturday" : _("Saturday"),
        "Sunday" : _("Sunday"),
    }
    if day in DAY_TRANSLATOR:
        return DAY_TRANSLATOR[day]
    return day

def translate_liturgical_time(time):

    LITUGICAL_TIME_TRANSLATE_TABLE = {
    'Advent' : _('Advent'),
    'Christmas Day' : _('Christmas Day'),
    'Christmas Season' : _('Christmas Season'),
    'Epiphany' : _('Epiphany'),
    'Baptism of the Lord' : _('Baptism of the Lord'),
    'Transfiguration Sunday' : _('Transfiguration Sunday'),
    'Ash Wednesday' : _('Ash Wednesday'),
    'Lent' : _('Lent'),
    'Maunday Thursday' : _('Maunday Thursday'),
    'Good Friday' : _('Good Friday'),
    'Holy Saturday' : _('Holy Saturday'),
    'Easter Sunday' : _('Easter Sunday'),
    'Easter Season' : _('Easter Season'),
    'Pentecost' : _('Pentecost'),
    'Trinity Sunday' : _('Trinity Sunday'),
    'Christ the King' : _('Christ the King'),
    'Ordinary Time' : _('Ordinary Time'),
    }

    if time in LITUGICAL_TIME_TRANSLATE_TABLE:
        return LITUGICAL_TIME_TRANSLATE_TABLE[time]
    return time

def today_to_rosary():
    day_id = dayofweek()
    ordinary_time, time_color = calendar.lookup(REFDATE)
    if day_id == 0:
        if ordinary_time == "Lent":
            # Move to sorrowful
            day_id = 5
        elif ordinary_time == "Advent":
            # Move to joyful
            day_id = 1

    console.print(_("[white]{}[/white] of [{}]{}[/{}] studying [italic]{}[/italic]").format(translate_day(dayname()), time_color, translate_liturgical_time(ordinary_time), time_color,DAY_TO_ROSARIES_NAME[day_id]), style="bold")
    # This line is important as we move up one line to print the pearls
    print("")

    return DAY_TO_ROSARIES[day_id], DAY_TO_ROSARIES_NAME[day_id]

class rosary():

    def _generate_mystery_description(self, mystery):
        if "openai" not in self.config or self.nosermon:
            return None

        openai.api_key = self.config["openai"]

        prompt = _("You are praying intensely recitating the rosary and going through the mysteries of the holly rosary.\
You want the people to do the rosary with you to feel deeply the meaning of each mystery.\
Can you explain this mystery in a short sermon of a few sentences : '{}'").format(mystery)

        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.2,
        )

        if False:
            if "sermons" not in self.config:
                self.config["sermons"] = {}

            if not self.current_myst in self.config["sermons"]:
                self.config["sermons"][self.current_myst] = {}

            if mystery not in self.config["sermons"][self.current_myst]:
                self.config["sermons"][self.current_myst][mystery] = []

            self.config["sermons"][self.current_myst][mystery].append(
                response.choices[0].text)

        if not response:
            return None

        return response.choices[0].text.replace("\n\n", "\n") + "\n"

    def _set_state(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)

    def __init__(self, nosermon=False):
        self.config = DEFAULT_CONFIG
        if not os.path.isfile(CONFIG_FILE):
            with open(CONFIG_FILE, "w") as f:
                json.dump(DEFAULT_CONFIG, f)
        else:
            with open(CONFIG_FILE, "r") as f:
                self.config = json.load(f)

        today = todaycode()
        if self.config["last"] != today:
            self.config["last"] = today
            self.config["offset"] = 0
            self._set_state()

        self.nosermon = nosermon

        self.rosary,self.current_myst = today_to_rosary()


    def _perl_from_offset(self):
        pass


    @property
    def offset(self):
        return self.config["offset"]

    def setoffset(self, offset):
        self.config["offset"] = offset

    def reset(self):
        self.setoffset(0)
        self._set_state()

    def _check_done(self):
        if self.offset == len(self.rosary):
            wait_for_key()
            console.print("Amen.", style="bold green")
            self.config["prayed"].append(
                {"date": todaycode(), "mysteries": DAY_TO_ROSARIES_NAME[dayofweek()]})
            self.reset()
            sys.exit(0)

    def step(self):
        self._check_done()
        current = self.rosary[self.offset]

        desc = None
        if current not in [_("Hail Mary"), _("Credo"), _("Glory to the Father"), _("Our Father")]:
            with console.status(_("Generating mystery's description..."),spinner="squish"):
                desc = self._generate_mystery_description(current)

        print("\033[F{} {}".format(PEARLS[self.offset], current))
        if desc:
            console.print(desc, style="bold white italic", justify="left")

        self.setoffset(self.offset + 1)
        self._check_done()
        self._set_state()


def run():

    #
    # Argument parsing
    #

    parser = argparse.ArgumentParser(
        description=_('Rosary an app to pray during the programmer\'s day.'))

    parser.add_argument('-r', "--reset",  action='store_true',
                        help=_("Reset current rosary"))
    parser.add_argument('-n', "--nosermon",  action='store_true',
                        help=_("Disable CHAT GPT sermon"))
    parser.add_argument('-s', "--single",  action='store_true',
                        help=_("Only do a single step"))
    parser.add_argument('-p', "--print",  action='store_true',
                        help=_("Only print current rosary and liturgical time"))

    args = parser.parse_args(sys.argv[1:])

    r = rosary(nosermon=args.nosermon)

    if args.print:
        sys.exit(0)

    if args.reset:
        r.reset()
        print(_("Current rosary restarted"))
        return 0

    if args.single:
        r.step()
    else:
        while True:
            r.step()
            wait_for_key()

    return 0
