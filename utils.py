# utils.py
import re
import csv


def extract_candidate_info(text):
    """
    Extract structured candidate info from free text input.
    """

    info = {}

    # Email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email_match:
        info["email"] = email_match.group(0)

    # Phone (10 digit)
    phone_match = re.search(r'\b\d{10}\b', text)
    if phone_match:
        info["phone"] = phone_match.group(0)

    # Name (simple assumption: first line or capital words)
    name_match = re.search(r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)', text)
    if name_match:
        info["name"] = name_match.group(0)

    # Experience
    exp_match = re.search(r'(\d+)\s*(years|yrs)', text.lower())
    if exp_match:
        info["experience"] = exp_match.group(1)

    # Position
    if "developer" in text.lower():
        info["position"] = "Developer"
    elif "engineer" in text.lower():
        info["position"] = "Engineer"

    # Location (basic)
    lines = text.split("\n")
    if lines:
        info["location"] = lines[-1].strip()

    info["raw_details"] = text
    return info


def save_candidate_data(candidate_data, filename="candidates.csv"):
    """
    Save candidate data into CSV.
    """

    fieldnames = [
        "name", "email", "phone", "experience", "position",
        "location", "tech_stack",
        "answer_1", "answer_2", "answer_3", "answer_4", "answer_5"
    ]

    # Ensure all keys exist
    for key in fieldnames:
        if key not in candidate_data:
            candidate_data[key] = ""

    try:
        with open(filename, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            # Write header if file is empty
            if file.tell() == 0:
                writer.writeheader()

            writer.writerow(candidate_data)

    except Exception as e:
        print(f"Error saving candidate data: {e}")


def save_answer(candidate_data, question_index, answer):
    """
    Save answers sequentially.
    """
    key = f"answer_{question_index + 1}"
    candidate_data[key] = answer


def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None


def validate_phone(phone):
    return re.match(r"^\d{10}$", phone) is not None