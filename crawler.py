# Initial imports
import numpy as np
import pandas as pd
from pandas import DataFrame, Series
import re

import random
import urllib.request
import requests
from bs4 import BeautifulSoup
import warnings

warnings.filterwarnings("ignore")


def log_progress(sequence, every=None, size=None, name="Items"):
    from ipywidgets import IntProgress, HTML, VBox
    from IPython.display import display

    is_iterator = False
    if size is None:
        try:
            size = len(sequence)
        except TypeError:
            is_iterator = True
    if size is not None:
        if every is None:
            if size <= 200:
                every = 1
            else:
                every = int(size / 200)  # every 0.5%
    else:
        assert every is not None, "sequence is iterator, set every"

    if is_iterator:
        progress = IntProgress(min=0, max=1, value=1)
        progress.bar_style = "info"
    else:
        progress = IntProgress(min=0, max=size, value=0)
    label = HTML()
    box = VBox(children=[label, progress])
    display(box)

    index = 0
    try:
        for index, record in enumerate(sequence, 1):
            if index == 1 or index % every == 0:
                if is_iterator:
                    label.value = "{name}: {index} / ?".format(name=name, index=index)
                else:
                    progress.value = index
                    label.value = "{name}: {index} / {size}".format(
                        name=name, index=index, size=size
                    )
            yield record
    except:
        progress.bar_style = "danger"
        raise
    else:
        progress.bar_style = "success"
        progress.value = index
        label.value = "{name}: {index}".format(name=name, index=str(index or "?"))


def _format_num(n):
    return "%02d" % n


def get_episode_soup(no, base_url):
    url = base_url + str(no) + ".shtml"
    source_code = requests.get(url)
    plain_text = source_code.text
    return plain_text


def parse_episode_info(html):
    """Return a dict with meta-info about the episode."""
    groups = re.search(r"pc: .*? season (\d+), episode (\d+)", html).groups()
    season_num = int(groups[0])
    episode_num = int(groups[1])

    title = re.search(r"Episode \d+(.*?) - (.*?)<", html).groups()[1]
    title = re.sub(r"[^\x00-\x7f]", r"", title)
    date = re.search(r"Broadcast date: (.*?)<", html).groups()[0]
    writers = re.search(r"Written [bB]y([:]|&nbsp;)? (.*?)<", html).groups()[1]
    writers = ", ".join(tuple([w.strip() for w in re.split(r",|&amp;", writers) if w]))
    director = re.search(r"Directed [bB]y (.*?)<", html).groups()[0]
    seid = "S" + str(_format_num(season_num)) + "E" + str(_format_num(episode_num))

    return {
        "season_num": season_num,
        "episode_num": episode_num,
        "title": title,
        "date": date,
        "writers": writers,
        "director": director,
        "seid": seid,
    }


def main(episode_nos, base_url, episode_info_df, script_df):
    for no in log_progress(episode_nos, every=1):
        html = get_episode_soup(no, base_url)
        html_split = re.split(r"={30}.*", html)
        header = html_split[0]
        content = html_split[1]
        episode_info = parse_episode_info(header)
        if str(no) == "179and180":
            content = html_split[2]
            episode_info["title"] = "The Finale"
            episode_info["episode_no"] = "The Finale"
        soup = BeautifulSoup(content)
        dialogues = list(
            filter(None, soup.find("body").text.replace("\t", "").split("\n"))
        )
        temp1 = DataFrame(
            [
                [
                    episode_info["season_num"],
                    episode_info["episode_num"],
                    episode_info["title"],
                    episode_info["date"],
                    episode_info["writers"],
                    episode_info["director"],
                    episode_info["seid"],
                ]
            ],
            columns=(
                "Season",
                "EpisodeNo",
                "Title",
                "AirDate",
                "Writers",
                "Director",
                "SEID",
            ),
        )
        for dialogue in dialogues:
            if len(dialogue.split(":")) <= 1:
                continue
            dialogue_split = dialogue.split(":")
            character = dialogue_split.pop(0)
            line = "".join(dialogue_split).strip()
            line = re.sub(r"[^\x00-\x7f]", r"", line)
            temp2 = DataFrame(
                [
                    [
                        episode_info["season_num"],
                        episode_info["episode_num"],
                        episode_info["seid"],
                        character,
                        line,
                    ]
                ],
                columns=("Season", "EpisodeNo", "SEID", "Character", "Dialogue"),
            )
            script_df = script_df.append(temp2, ignore_index=True)
        episode_info_df = episode_info_df.append(temp1, ignore_index=True)
    return episode_info_df, script_df


EPISODE_INFO_DF = DataFrame(
    columns=("Season", "EpisodeNo", "Title", "AirDate", "Writers", "Director", "SEID")
)
SCRIPT_DF = DataFrame(columns=("SEID", "Character", "Dialogue"))
BASE_URL = "http://www.seinology.com/scripts/script-"
EPISODE_NUMBERS = (
    list(map(_format_num, range(1, 82)))
    +
    # Double episode
    ["82and83"]
    + list(map(_format_num, range(84, 100)))
    +
    # Skip the clip show "100and101".
    list(map(_format_num, range(102, 177)))
    +
    # Skip the clip show "177and178".
    # Double episode (Finale)
    ["179and180"]
)
episode_info_df, script_df = main(EPISODE_NUMBERS, BASE_URL, EPISODE_INFO_DF, SCRIPT_DF)

episode_info_df.head()
script_df.head()

episode_info_df.to_csv("episode_info.csv", encoding="utf-8")
script_df.to_csv("scripts.csv", encoding="utf-8")
