"""Attendly: a simple Python attendance tracker with a graph."""

from datetime import date, datetime
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt

USERNAME = "teacher"
PASSWORD = "teach123"
DATA_FILE = Path(__file__).with_name("attendance_data.json")

STUDENTS = [
    {"id": "STU-101", "name": "Aarav Sharma"},
    {"id": "STU-102", "name": "Mira Patel"},
    {"id": "STU-103", "name": "Kabir Singh"},
    {"id": "STU-104", "name": "Ananya Rao"},
    {"id": "STU-105", "name": "Dev Mehta"},
    {"id": "STU-106", "name": "Isha Kapoor"},
    {"id": "STU-107", "name": "Rohan Das"},
    {"id": "STU-108", "name": "Sana Khan"},
    {"id": "STU-109", "name": "Vihaan Joshi"},
    {"id": "STU-110", "name": "Nisha Verma"},
]

STATUS_OPTIONS = {
    "P": "Present",
    "A": "Absent",
    "L": "Late",
    "N": "Not marked",
}

CATEGORIES = np.array(["Present", "Absent", "Late", "Not marked"])


def load_records():
    if not DATA_FILE.exists():
        return {}

    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_records(records):
    DATA_FILE.write_text(json.dumps(records, indent=2), encoding="utf-8")


def login():
    print("=== Attendly Teacher Login ===")

    for attempt in range(3):
        username = input("Username: ").strip()
        password = input("Password: ").strip()

        if username == USERNAME and password == PASSWORD:
            print("\nLogin successful.\n")
            return True

        print("Incorrect login.")

    return False


def choose_date():
    today = date.today().isoformat()
    value = input(f"Date (YYYY-MM-DD) or Enter for {today}: ").strip()

    if not value:
        return today

    try:
        return datetime.strptime(value, "%Y-%m-%d").date().isoformat()
    except ValueError:
        print("Invalid date. Using today's date.")
        return today


def mark_attendance(records):
    selected_date = choose_date()
    day = records.get(selected_date, {})

    print("Enter P=Present, A=Absent, L=Late, N=Not marked.")

    for student in STUDENTS:
        student_id = student["id"]
        current = day.get(student_id, "Not marked")

        choice = input(
            f"{student['name']} [{current}]: "
        ).strip().upper()

        if choice in STATUS_OPTIONS:
            day[student_id] = STATUS_OPTIONS[choice]
        else:
            day.setdefault(student_id, current)

    records[selected_date] = day

    try:
        save_records(records)
        print("Attendance saved.\n")
    except OSError:
        print("Could not save attendance. Check folder permissions.\n")


def attendance_summary(day):
    statuses = np.array([
        day.get(student["id"], "Not marked")
        for student in STUDENTS
    ])

    counts = np.array(
        [(statuses == category).sum() for category in CATEGORIES],
        dtype=int,
    )

    marked = int(np.sum(counts[:3]))

    if marked:
        rate = round((int(counts[0]) + int(counts[2])) * 100 / marked)
    else:
        rate = 0

    return statuses, counts, rate


def show_graph(selected_date, counts):
    x_positions = np.arange(len(CATEGORIES))
    colors = ["#2ecc71", "#e74c3c", "#f1c40f", "#95a5a6"]

    figure, axis = plt.subplots(figsize=(7, 5))
    bars = axis.bar(
        x_positions,
        counts,
        color=colors,
        edgecolor="black",
    )

    axis.set_title(f"Attendly Attendance Summary - {selected_date}")
    axis.set_ylabel("Number of students")
    axis.set_xticks(x_positions)
    axis.set_xticklabels(CATEGORIES)
    axis.set_yticks(np.arange(0, int(counts.max()) + 2, 1))
    axis.grid(axis="y", linestyle="--", alpha=0.4)
    axis.bar_label(bars, padding=3)
    figure.tight_layout()

    image_path = Path(__file__).with_name(
        f"attendance_graph_{selected_date}.png"
    )

    figure.savefig(image_path, dpi=150)
    print(f"Graph saved: {image_path.name}")

    plt.show()
    plt.close(figure)


def view_report(records):
    selected_date = choose_date()
    day = records.get(selected_date, {})
    statuses, counts, rate = attendance_summary(day)

    print(f"\n=== Attendance Report: {selected_date} ===")
    print(f"{'Student':<20} {'ID':<12} Status")
    print("-" * 48)

    for student, status in zip(STUDENTS, statuses):
        print(f"{student['name']:<20} {student['id']:<12} {status}")

    present, absent, late, not_marked = counts.tolist()

    print(f"\nTotal students : {len(STUDENTS)}")
    print(f"Present        : {present}")
    print(f"Absent         : {absent}")
    print(f"Late           : {late}")
    print(f"Not marked     : {not_marked}")
    print(f"Attendance rate: {rate}%\n")

    show_graph(selected_date, counts)


def main():
    if not login():
        print("Login failed.")
        return

    records = load_records()

    while True:
        print("=== Attendly Menu ===")
        print("1. Mark attendance")
        print("2. View report and graph")
        print("3. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            mark_attendance(records)
        elif choice == "2":
            view_report(records)
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Choose 1, 2, or 3.\n")


if __name__ == "__main__":
    main()