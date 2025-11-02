import os
import csv
import re
import datetime
import uuid
from typing import List, Dict


def normalize_case(text: str) -> List[str]:
    """Normalize text to sentence case."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.capitalize() for s in sentences if s]


def fix_misspelling(sentences: List[str]) -> List[str]:
    """Replace 'iz' with 'is' when used incorrectly."""
    return [re.sub(r'\biz\b', 'is', s, flags=re.IGNORECASE) for s in sentences]


def process_text(text: str) -> str:
    """Full normalization pipeline returning final text."""
    normalized = normalize_case(text)
    fixed = fix_misspelling(normalized)
    return " ".join(fixed)



def publish_news(file_path, text: str, city: str):
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    record = f"News -------------------------\n{text}\n{city}, {date}\n\n"
    with open(file_path, "a") as f:
        f.write(record)


def publish_private_ad(file_path, text: str, exp_date_str: str):
    try:
        exp_date = datetime.datetime.strptime(exp_date_str, "%Y-%m-%d")
        days_left = (exp_date - datetime.datetime.now()).days
    except Exception:
        print(f"Invalid date format for ad: {exp_date_str}")
        return
    record = f"Private Ad -------------------\n{text}\nExpires: {exp_date_str}, {days_left} days left\n\n"
    with open(file_path, "a") as f:
        f.write(record)


def publish_event(file_path, event_name: str, location: str, time_str: str):
    try:
        event_time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M")
    except Exception:
        print(f"Invalid date/time format for event: {time_str}")
        return
    event_code = str(uuid.uuid4())[:8]
    record = (f"Event ------------------------\n"
              f"Event: {event_name}\n"
              f"Location: {location}\n"
              f"Time: {event_time.strftime('%Y-%m-%d %H:%M')}\n"
              f"Event Code: {event_code}\n\n")
    with open(file_path, "a") as f:
        f.write(record)



class FileRecordProcessor:
    DEFAULT_INPUT_FOLDER = "./input_files"

    def __init__(self, file_path: str | None = None):
        if not os.path.exists(self.DEFAULT_INPUT_FOLDER):
            os.makedirs(self.DEFAULT_INPUT_FOLDER)
        self.file_path = file_path or os.path.join(self.DEFAULT_INPUT_FOLDER, "records.txt")
        self.output_path = "news_feed.txt"

    def _parse_records(self, raw_text: str) -> List[Dict[str, str]]:
        """Parse text file into structured records."""
        blocks = re.split(r'-{3,}', raw_text.strip())
        records = []
        for block in blocks:
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            if not lines:
                continue
            rec_dict = {}
            for line in lines:
                if ":" in line:
                    key, val = line.split(":", 1)
                    rec_dict[key.strip().upper()] = val.strip()
            if rec_dict:
                records.append(rec_dict)
        return records

    def _normalize_text_fields(self, rec: Dict[str, str]) -> Dict[str, str]:
        """Apply text normalization to text-like fields."""
        for k, v in rec.items():
            if k in {"TEXT", "CITY", "NAME", "LOCATION"}:
                rec[k] = process_text(v)
        return rec

    def process_file(self):
        """Process all records and remove input file if successful."""
        if not os.path.exists(self.file_path):
            print(f"Input file not found: {self.file_path}")
            return
        with open(self.file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        records = self._parse_records(raw_text)
        success = True

        for rec in records:
            rec = self._normalize_text_fields(rec)
            record_type = rec.get("TYPE", "").lower()
            try:
                if record_type == "news":
                    publish_news(self.output_path, rec["TEXT"], rec.get("CITY", "Unknown"))
                elif record_type == "ad":
                    publish_private_ad(self.output_path, rec["TEXT"], rec["EXPIRES"])
                elif record_type == "event":
                    publish_event(self.output_path, rec["NAME"], rec["LOCATION"], rec["TIME"])
                else:
                    print(f"Unknown record type: {record_type}")
            except Exception as e:
                print(f"Failed to process record: {e}")
                success = False

        if success:
            os.remove(self.file_path)
            print(f"Processed and removed: {self.file_path}")

        # generate statistics after successful processing
        generate_statistics(self.output_path)



def generate_statistics(file_path: str):
    """Create two CSVs:
    1. word_count.csv — word, count
    2. letter_stat.csv — letter, count_all, count_uppercase, percentage
    """

    if not os.path.exists(file_path):
        print(f"No file found: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # ---------- WORD COUNT ----------
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    word_freq = {}
    for w in words:
        word_freq[w] = word_freq.get(w, 0) + 1

    with open("word_count.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["word", "count"])
        for w, c in sorted(word_freq.items()):
            writer.writerow([w, c])

    # ---------- LETTER STATISTICS ----------
    letters = re.findall(r'[A-Za-z]', text)
    total_letters = len(letters)
    lower_text = text.lower()
    upper_text = text.upper()

    stats = []
    for ch in sorted(set(lower_text)):
        if not ch.isalpha():
            continue
        count_all = lower_text.count(ch)
        count_upper = sum(1 for c in text if c == ch.upper())
        percent = round((count_all / total_letters) * 100, 2) if total_letters else 0
        stats.append([ch, count_all, count_upper, percent])

    with open("letter_stat.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["letter", "count_all", "count_uppercase", "percentage"])
        for row in stats:
            writer.writerow(row)

    print("CSV files recreated: word_count.csv and letter_stat.csv")



def main():
    file_path = "news_feed.txt"
    while True:
        print("Select record type to add:")
        print("1. News")
        print("2. Private Ad")
        print("3. Event (unique)")
        print("4. Load from file")
        print("5. Exit")
        choice = input("Enter your choice (1-5): ")

        if choice == "1":
            text = process_text(input("Enter news text: "))
            city = process_text(input("Enter city: "))
            publish_news(file_path, text, city)
            print("News published!\n")
            generate_statistics(file_path)

        elif choice == "2":
            text = process_text(input("Enter ad text: "))
            exp_date = input("Enter expiration date (YYYY-MM-DD): ")
            publish_private_ad(file_path, text, exp_date)
            print("Private ad published!\n")
            generate_statistics(file_path)

        elif choice == "3":
            name = process_text(input("Enter event name: "))
            loc = process_text(input("Enter event location: "))
            time_str = input("Enter event time (YYYY-MM-DD HH:MM): ")
            publish_event(file_path, name, loc, time_str)
            print("Event published!\n")
            generate_statistics(file_path)

        elif choice == "4":
            inp = input("Enter file path (leave empty for default): ").strip()
            processor = FileRecordProcessor(inp or None)
            processor.process_file()

        elif choice == "5":
            print("Exiting.")
            break
        else:
            print("Invalid choice. Try again.\n")


if __name__ == "__main__":
    main()
