import os
import json
import datetime
import uuid
import re
import csv
import sqlite3
import xml.etree.ElementTree as ET
from typing import List, Dict



def normalize_case(text: str) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.capitalize() for s in sentences if s]


def fix_misspelling(sentences: List[str]) -> List[str]:
    return [re.sub(r'\biz\b', 'is', s, flags=re.IGNORECASE) for s in sentences]


def extract_last_words(sentences: List[str]) -> str:
    last_words = [s.rstrip('.!?').split()[-1] for s in sentences if s]
    return " ".join(last_words).capitalize() + "."


def count_whitespaces(text: str) -> int:
    return sum(1 for c in text if c.isspace())


def process_text(text: str) -> Dict[str, str | int]:
    normalized = normalize_case(text)
    fixed = fix_misspelling(normalized)
    extra_sentence = extract_last_words(fixed)
    final_text = " ".join(fixed) + " " + extra_sentence
    whitespace_count = count_whitespaces(text)
    return {"final_text": final_text, "whitespace_count": whitespace_count}



class DatabaseHandler:
    def __init__(self, db_path="news_feed.db"):
        self.db_path = db_path
        self._initialize_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _initialize_db(self):
        with self._connect() as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT,
                    city TEXT,
                    date TEXT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS private_ads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT,
                    exp_date TEXT,
                    days_left INTEGER
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    location TEXT,
                    time TEXT,
                    event_code TEXT
                )
            """)
            conn.commit()

    def _record_exists(self, table: str, where_clause: str, params: tuple) -> bool:
        with self._connect() as conn:
            c = conn.cursor()
            query = f"SELECT 1 FROM {table} WHERE {where_clause} LIMIT 1"
            c.execute(query, params)
            return c.fetchone() is not None

    def insert_news(self, text, city, date):
        if self._record_exists("news", "text=? AND city=?", (text, city)):
            print("Duplicate news detected — not inserted.")
            return
        with self._connect() as conn:
            conn.execute("INSERT INTO news (text, city, date) VALUES (?, ?, ?)",
                         (text, city, date))
            conn.commit()

    def insert_private_ad(self, text, exp_date, days_left):
        if self._record_exists("private_ads", "text=? AND exp_date=?", (text, exp_date)):
            print("Duplicate ad detected — not inserted.")
            return
        with self._connect() as conn:
            conn.execute("INSERT INTO private_ads (text, exp_date, days_left) VALUES (?, ?, ?)",
                         (text, exp_date, days_left))
            conn.commit()

    def insert_event(self, name, location, time_str, event_code):
        if self._record_exists("events", "name=? AND time=?", (name, time_str)):
            print("Duplicate event detected — not inserted.")
            return
        with self._connect() as conn:
            conn.execute("INSERT INTO events (name, location, time, event_code) VALUES (?, ?, ?, ?)",
                         (name, location, time_str, event_code))
            conn.commit()



def write_record(file_path: str, content: str):
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(content + "\n\n")



db_handler = DatabaseHandler()  # global instance

def publish_news(text: str, city: str, file_path: str):
    text_data = process_text(text)
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    record = f"News -------------------------\n{text_data['final_text']}\n{city}, {date}"
    write_record(file_path, record)
    db_handler.insert_news(text_data["final_text"], city, date)
    print("News published!\n")


def publish_private_ad(text: str, exp_date_str: str, file_path: str):
    exp_date = datetime.datetime.strptime(exp_date_str, "%Y-%m-%d")
    days_left = (exp_date - datetime.datetime.now()).days
    text_data = process_text(text)
    record = f"Private Ad -------------------\n{text_data['final_text']}\nExpires: {exp_date_str}, {days_left} days left"
    write_record(file_path, record)
    db_handler.insert_private_ad(text_data["final_text"], exp_date_str, days_left)
    print("Private Ad published!\n")


def publish_event(name: str, location: str, time_str: str, file_path: str):
    event_time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M")
    event_code = str(uuid.uuid4())[:8]
    record = (f"Event ------------------------\n"
              f"Event: {name}\n"
              f"Location: {location}\n"
              f"Time: {event_time.strftime('%Y-%m-%d %H:%M')}\n"
              f"Event Code: {event_code}")
    write_record(file_path, record)
    db_handler.insert_event(name, location, time_str, event_code)
    print("Event published!\n")



class TextFileInput:
    def __init__(self, default_folder="inputs"):
        self.default_folder = default_folder
        os.makedirs(default_folder, exist_ok=True)

    def process_file(self, file_path=None, output_file="news_feed.txt"):
        file_path = file_path or os.path.join(self.default_folder, "records.txt")
        if not os.path.exists(file_path):
            print(f"File {file_path} not found.")
            return
        with open(file_path, "r", encoding="utf-8") as f:
            data = f.read().strip()
        publish_news(data, "Unknown City", output_file)
        os.remove(file_path)
        print("Text file processed successfully.")


class JSONFileInput:
    def __init__(self, default_folder="inputs"):
        self.default_folder = default_folder
        os.makedirs(default_folder, exist_ok=True)

    def process_file(self, file_path=None, output_file="news_feed.txt"):
        file_path = file_path or os.path.join(self.default_folder, "records.json")
        if not os.path.exists(file_path):
            print(f"File {file_path} not found.")
            return
        with open(file_path, "r", encoding="utf-8") as f:
            records = json.load(f)
        if not isinstance(records, list):
            records = [records]
        for rec in records:
            rtype = rec.get("type", "").lower()
            if rtype == "news":
                publish_news(rec["text"], rec.get("city", "Unknown"), output_file)
            elif rtype == "private_ad":
                publish_private_ad(rec["text"], rec["exp_date"], output_file)
            elif rtype == "event":
                publish_event(rec["name"], rec["location"], rec["time"], output_file)
        os.remove(file_path)
        print(f"JSON file {file_path} processed successfully.")


class XMLFileInput:
    def __init__(self, default_folder="inputs"):
        self.default_folder = default_folder
        os.makedirs(default_folder, exist_ok=True)

    def process_file(self, file_path=None, output_file="news_feed.txt"):
        file_path = file_path or os.path.join(self.default_folder, "records.xml")
        if not os.path.exists(file_path):
            print(f"File {file_path} not found.")
            return
        tree = ET.parse(file_path)
        root = tree.getroot()
        for rec in root.findall("record"):
            rtype = rec.attrib.get("type", "").lower()
            if rtype == "news":
                publish_news(rec.findtext("text", ""), rec.findtext("city", "Unknown"), output_file)
            elif rtype == "private_ad":
                publish_private_ad(rec.findtext("text", ""), rec.findtext("exp_date", ""), output_file)
            elif rtype == "event":
                publish_event(rec.findtext("name", ""), rec.findtext("location", ""), rec.findtext("time", ""), output_file)
        os.remove(file_path)
        print(f"XML file {file_path} processed successfully.")



def update_csvs(feed_path="news_feed.txt"):
    if not os.path.exists(feed_path):
        return
    with open(feed_path, "r", encoding="utf-8") as f:
        text = f.read()
    words = re.findall(r'\b\w+\b', text.lower())
    word_counts = {}
    for w in words:
        word_counts[w] = word_counts.get(w, 0) + 1
    with open("word_count.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["word", "count"])
        writer.writerows(word_counts.items())
    letters = [c for c in text if c.isalpha()]
    letter_data = {}
    for c in letters:
        lower = c.lower()
        if lower not in letter_data:
            letter_data[lower] = {"count_all": 0, "count_upper": 0}
        letter_data[lower]["count_all"] += 1
        if c.isupper():
            letter_data[lower]["count_upper"] += 1
    with open("letter_count.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["letter", "count_all", "count_uppercase", "percentage"])
        total = sum(v["count_all"] for v in letter_data.values())
        for letter, v in sorted(letter_data.items()):
            perc = round((v["count_all"] / total) * 100, 2)
            writer.writerow([letter, v["count_all"], v["count_upper"], perc])
    print("CSV files updated.\n")



def main():
    file_path = "news_feed.txt"
    txt_handler = TextFileInput()
    json_handler = JSONFileInput()
    xml_handler = XMLFileInput()

    while True:
        print("Select record type to add:")
        print("1. News")
        print("2. Private Ad")
        print("3. Event")
        print("4. Load from Text file")
        print("5. Load from JSON file")
        print("6. Load from XML file")
        print("7. Exit")

        choice = input("Enter your choice (1-7): ").strip()
        if choice == "1":
            text = input("Enter news text: ")
            city = input("Enter city: ")
            publish_news(text, city, file_path)
            update_csvs(file_path)
        elif choice == "2":
            text = input("Enter ad text: ")
            exp = input("Enter expiration date (YYYY-MM-DD): ")
            publish_private_ad(text, exp, file_path)
            update_csvs(file_path)
        elif choice == "3":
            name = input("Enter event name: ")
            location = input("Enter location: ")
            time_str = input("Enter time (YYYY-MM-DD HH:MM): ")
            publish_event(name, location, time_str, file_path)
            update_csvs(file_path)
        elif choice == "4":
            txt_handler.process_file()
            update_csvs(file_path)
        elif choice == "5":
            json_handler.process_file()
            update_csvs(file_path)
        elif choice == "6":
            xml_handler.process_file()
            update_csvs(file_path)
        elif choice == "7":
            print("Exiting.")
            break
        else:
            print("Invalid choice.\n")


if __name__ == "__main__":
    main()
