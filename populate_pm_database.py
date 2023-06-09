from bs4 import BeautifulSoup
from pathlib import Path
from nor_punkt_patch import sent_patch
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.util import ngrams
import sqlite3
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("path", help="path to the database")
parser.add_argument("-d", "--data_dir", help="path to the ParlaMint-NO folder")
args = parser.parse_args()

def sent_seg(mystring):
    return sent_patch(sent_tokenize(mystring, language="norwegian"))


def find_time(note):
    pattern = re.compile(r"\[(\d{2}:\d{2}:\d{2})\]")
    if pattern.search(note):
        return pattern.search(note).group(1)
    else:
        return None


def find_date(filename):
    pattern = re.compile(r"(\d{4})\-(\d{2}\-\d{2})")
    return (pattern.search(filename).group(1), pattern.search(filename).group(2))


if __name__ == "__main__":
    con = sqlite3.connect(args.path)
    pm_root_folder = Path(args.data_dir)
    pm_ref_folder = pm_root_folder / "ref"

    metadata_file = pm_root_folder / "ParlaMint-NO.xml"

    with metadata_file.open(mode="r") as f:
        metasoup = BeautifulSoup(f.read(), "lxml")

    speakers = []
    for x in metasoup.find_all("person"):
        name = x.find("persname")
        record = (
            x.get("xml:id"),
            x.find("sex")["value"],
            x.find("birth")["when"],
            name.find("forename").text,
            name.find("surname").text,
        )
        speakers.append(record)

    cur = con.cursor()
    cur.executemany(
        "INSERT INTO speakers (speaker_id, sex, birth, forename, surname) VALUES (?,?,?,?,?);",
        speakers,
    )
    con.commit()

    for file in pm_ref_folder.glob("*.xml"):
        print(file.name)
        turns = []
        segments = []
        sentences = []
        tokenlist = []
        bigramlist = []
        trigramlist = []
        with file.open(mode="r") as f:
            soup = BeautifulSoup(f.read(), "lxml")
        date = find_date(file.name)
        meeting = (file.stem, date[0], date[1], file.name)
        for x in soup.find_all("u"):
            turn_id = x.get("xml:id")
            turn_note_ret = x.findPrevious("note", attrs={"type": "speaker"})
            if turn_note_ret is not None:
                turn_note = turn_note_ret.text
                time = find_time(turn_note)
            else:
                turn_note = None
                time = None
            turn = (
                turn_id,
                x.get("xml:lang"),
                x.get("ana"),
                turn_note,
                time,
                x.get("who"),
                file.name,
            )
            turns.append(turn)
            for y in x.find_all("seg"):
                seg_id = y.get("xml:id")
                seg = (seg_id, turn_id, y.text)
                segments.append(seg)
                for i, s in enumerate(sent_seg(y.text)):
                    sent_id = seg_id + "_" + str(i)
                    sent = (sent_id, seg_id, s)
                    sentences.append(sent)
                    punctpattern = re.compile(
                        r"[\!#$%&\(\)\*+,\-\./–:;<=>?@^_`{\|}~«»]"
                    )
                    tokens = word_tokenize(s, language="norwegian")
                    tokens_cleaned = [
                        x.lower() for x in tokens if not punctpattern.match(x)
                    ]
                    bigrams = [
                        (sent_id, " ".join(x)) for x in ngrams(tokens_cleaned, 2)
                    ]
                    trigrams = [
                        (sent_id, " ".join(x)) for x in ngrams(tokens_cleaned, 3)
                    ]
                    bigramlist += bigrams
                    trigramlist += trigrams
                    for i, t in enumerate(tokens):
                        token_id = sent_id + "_t" + str(i)
                        token = (token_id, sent_id, t)
                        tokenlist.append(token)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO meetings (meeting_id, meeting_year, meeting_date, meeting_filename) VALUES (?,?,?,?);",
            meeting,
        )
        cur.executemany(
            "INSERT INTO turns (turn_id, lang, ana, note_str, time, speaker_id, meeting_id) VALUES (?,?,?,?,?,?,?);",
            turns,
        )
        cur.executemany(
            "INSERT INTO segments (seg_id, turn_id, seg_text) VALUES (?,?,?);", segments
        )
        cur.executemany(
            "INSERT INTO sentences (sent_id, seg_id, sent_text) VALUES (?,?,?);",
            sentences,
        )
        cur.executemany(
            "INSERT INTO tokens (tok_id, sent_id, tok_text) VALUES (?,?,?);", tokenlist
        )
        cur.executemany(
            "INSERT INTO bigrams (sent_id, bigram_text) VALUES (?,?);", bigramlist
        )
        cur.executemany(
            "INSERT INTO trigrams (sent_id, trigram_text) VALUES (?,?);", trigramlist
        )
        con.commit()
    con.close()
