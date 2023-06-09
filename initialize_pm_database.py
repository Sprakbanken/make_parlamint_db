import sqlite3
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("path", help="path to the database")
args = parser.parse_args()


create_speakers = """CREATE TABLE IF NOT EXISTS speakers (
                    speaker_id TEXT PRIMARY KEY,
                    sex TEXT,
                    birth TEXT,
                    forename TEXT,
                    surname TEXT);"""

create_meetings = """CREATE TABLE IF NOT EXISTS meetings (
                    meeting_id TEXT PRIMARY KEY,
                    meeting_year TEXT,
                    meeting_date TEXT,
                    meeting_filename TEXT);"""

create_turns = """CREATE TABLE IF NOT EXISTS turns (
                    turn_id TEXT PRIMARY KEY,
                    lang TEXT,
                    ana TEXT,
                    note_str TEXT,
                    time TEXT,
                    speaker_id TEXT,
                    meeting_id TEXT,
                    FOREIGN KEY(speaker_id) REFERENCES speakers(speaker_id));"""

create_segments = """CREATE TABLE IF NOT EXISTS segments (
                    seg_id TEXT PRIMARY KEY,
                    turn_id TEXT,
                    seg_text TEXT,
                     FOREIGN KEY(turn_id) REFERENCES turns(turn_id));"""


create_sentences = """CREATE TABLE IF NOT EXISTS sentences (
                    sent_id TEXT PRIMARY KEY,
                    seg_id TEXT,
                    sent_text TEXT,
                    FOREIGN KEY(seg_id) REFERENCES segments(seg_id));"""

create_tokens = """CREATE TABLE IF NOT EXISTS tokens (
                    tok_id TEXT PRIMARY KEY,
                    sent_id TEXT,
                    tok_text TEXT,
                    FOREIGN KEY(sent_id) REFERENCES sentences(sent_id));"""

create_bigrams = """CREATE TABLE IF NOT EXISTS bigrams (
                    bigram_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sent_id TEXT,
                    bigram_text TEXT,
                    FOREIGN KEY(sent_id) REFERENCES sentences(sent_id));"""

create_trigrams = """CREATE TABLE IF NOT EXISTS trigrams (
                    trigram_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sent_id TEXT,
                    trigram_text TEXT,
                    FOREIGN KEY(sent_id) REFERENCES sentences(sent_id));"""

create_audio = """CREATE TABLE IF NOT EXISTS audio (
                    audio_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT,
                    meeting_id TEXT,
                    FOREIGN KEY(meeting_id) REFERENCES meetings(meeting_id));"""

if __name__ == "__main__":
    try:
        sqliteConnection = sqlite3.connect(
            args.path
        )
        cursor = sqliteConnection.cursor()
        print("Successfully Connected to SQLite")
        cursor.execute(create_speakers)
        cursor.execute(create_meetings)
        cursor.execute(create_turns)
        cursor.execute(create_segments)
        cursor.execute(create_sentences)
        cursor.execute(create_tokens)
        cursor.execute(create_bigrams)
        cursor.execute(create_trigrams)
        cursor.execute(create_audio)
        sqliteConnection.commit()
        print("SQLite table created")

        cursor.close()
        sqliteConnection.close()

    except sqlite3.Error as error:
        print("Error while creating a sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("sqlite connection is closed")
