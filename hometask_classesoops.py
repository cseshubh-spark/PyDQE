import datetime
import uuid

def publish_news(file_path):
    text = input("Enter news text: ")
    city = input("Enter city: ")
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    record = f"News -------------------------\n{text}\n{city}, {date}\n\n"
    with open(file_path, "a") as f:
        f.write(record)
    print("News published!\n")

def publish_private_ad(file_path):
    text = input("Enter ad text: ")
    exp_date_str = input("Enter expiration date (YYYY-MM-DD): ")
    try:
        exp_date = datetime.datetime.strptime(exp_date_str, "%Y-%m-%d")
        days_left = (exp_date - datetime.datetime.now()).days
    except Exception:
        print("Invalid date format.")
        return
    record = f"Private Ad -------------------\n{text}\nExpires: {exp_date_str}, {days_left} days left\n\n"
    with open(file_path, "a") as f:
        f.write(record)
    print("Private ad published!\n")

def publish_event(file_path):
    event_name = input("Enter event name: ")
    location = input("Enter event location: ")
    time_str = input("Enter event time (YYYY-MM-DD HH:MM): ")
    try:
        event_time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M")
    except Exception:
        print("Invalid date/time format.")
        return
    event_code = str(uuid.uuid4())[:8]
    record = (f"Event ------------------------\n"
              f"Event: {event_name}\n"
              f"Location: {location}\n"
              f"Time: {event_time.strftime('%Y-%m-%d %H:%M')}\n"
              f"Event Code: {event_code}\n\n")
    with open(file_path, "a") as f:
        f.write(record)
    print("Event published!\n")

def main():
    file_path = "news_feed.txt"
    while True:
        print("Select record type to add:")
        print("1. News")
        print("2. Private Ad")
        print("3. Event (unique)")
        print("4. Exit")
        choice = input("Enter your choice (1-4): ")
        if choice == "1":
            publish_news(file_path)
        elif choice == "2":
            publish_private_ad(file_path)
        elif choice == "3":
            publish_event(file_path)
        elif choice == "4":
            print("Exiting.")
            break
        else:
            print("Invalid choice. Try again.\n")

if __name__ == "__main__":
    main()
