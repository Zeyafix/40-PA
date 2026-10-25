import json
from pathlib import Path

import requests


BASE_DIR = Path(__file__).resolve().parent
TASKS_FILE = BASE_DIR / "data" / "tasks.json"
REPORT_FILE = BASE_DIR / "output" / "report.txt"
API_URL = "https://jsonplaceholder.typicode.com/todos?userId=1"
REQUEST_TIMEOUT = 10


def validate_tasks(tasks):
    if not isinstance(tasks, list):
        raise ValueError("Tasks must be a JSON array.")
    for task in tasks:
        if not isinstance(task, dict):
            raise ValueError("Each task must be an object.")
        if not isinstance(task.get("title"), str) or not task["title"].strip():
            raise ValueError("Each task needs a non-empty title.")
        if not isinstance(task.get("completed"), bool):
            raise ValueError("The completed field must be true or false.")
    return tasks


def load_tasks(path):
    with open(path, encoding="utf-8") as file:
        return validate_tasks(json.load(file))


def download_tasks():
    response = requests.get(API_URL, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return validate_tasks(response.json())


def build_report(tasks):
    completed = 0
    pending_titles = []
    for task in tasks:
        if task["completed"]:
            completed += 1
        else:
            pending_titles.append(task["title"])

    lines = [
        f"Tasks: {len(tasks)}",
        f"Completed: {completed}",
        f"Pending: {len(pending_titles)}",
        "",
        "Pending tasks:",
    ]
    for title in pending_titles:
        lines.append(f"- {title}")
    if not pending_titles:
        lines.append("No pending tasks.")
    return "\n".join(lines) + "\n"


def save_report(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        file.write(report)


def show_menu():
    print("\nTask report menu:")
    print("1. Report from local tasks")
    print("2. Report from online tasks")
    print("0. Exit")


def main():
    while True:
        show_menu()
        choice = input("Choose an action (0-2): ").strip()
        if choice == "0":
            print("Goodbye!")
            return
        if choice not in ("1", "2"):
            print("Unknown action. Choose 0, 1 or 2.")
            continue

        try:
            if choice == "1":
                tasks = load_tasks(TASKS_FILE)
            else:
                tasks = download_tasks()
            report = build_report(tasks)
            save_report(REPORT_FILE, report)
        except (OSError, ValueError, requests.RequestException) as error:
            print(f"Could not create report: {error}")
        else:
            print(report, end="")
            print(f"Report saved to: {REPORT_FILE}")


if __name__ == "__main__":
    main()
