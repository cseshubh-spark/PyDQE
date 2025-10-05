import random
import string
import re
from typing import List, Dict


# Module 2:
def generate_random_dict(num_keys: int) -> Dict[str, int]:
    """Generate a random dictionary with given number of keys."""
    keys = random.sample(string.ascii_lowercase, num_keys)
    return {k: random.randint(0, 100) for k in keys}


def generate_list_of_dicts(min_dicts: int = 2, max_dicts: int = 10,
                           min_keys: int = 1, max_keys: int = 5) -> List[Dict[str, int]]:
    """Generate a list of random dictionaries."""
    num_dicts = random.randint(min_dicts, max_dicts)
    return [generate_random_dict(random.randint(min_keys, max_keys))
            for _ in range(num_dicts)]


def merge_dicts(dicts: List[Dict[str, int]]) -> Dict[str, int]:
    """
    Merge dictionaries:
    - If key appears in multiple dicts, keep the one with the highest value.
    - Append suffix _dictNumber for duplicate keys.
    """
    final_dict = {}
    key_owner = {}

    def update_dict(idx: int, key: str, value: int):
        nonlocal final_dict, key_owner
        if key in key_owner:
            old_key = key_owner[key]
            if value > final_dict[old_key]:
                del final_dict[old_key]
                new_key = f"{key}_{idx}"
                final_dict[new_key] = value
                key_owner[key] = new_key
        else:
            final_dict[key] = value
            key_owner[key] = key

    for idx, d in enumerate(dicts, start=1):
        [update_dict(idx, k, v) for k, v in d.items()]

    return final_dict


def run_dict():
    """Functional entrypoint for dictionary logic."""
    dicts = generate_list_of_dicts()
    print("Generated list of dictionaries:")
    print(dicts)
    print("\nFinal merged dictionary:")
    print(merge_dicts(dicts))


# Module 3:

def normalize_case(text: str) -> List[str]:
    """Normalize text to sentence case."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.capitalize() for s in sentences if s]


def fix_misspelling(sentences: List[str]) -> List[str]:
    """Replace 'iz' with 'is' when used incorrectly."""
    return [re.sub(r'\biz\b', 'is', s, flags=re.IGNORECASE) for s in sentences]


def extract_last_words(sentences: List[str]) -> str:
    """Form a sentence using the last word of each sentence."""
    last_words = [s.rstrip('.!?').split()[-1] for s in sentences if s]
    return " ".join(last_words).capitalize() + "."


def count_whitespaces(text: str) -> int:
    """Count all whitespace characters in text."""
    return sum(1 for c in text if c.isspace())


def process_text(text: str) -> Dict[str, str | int]:
    """Complete text normalization and analysis pipeline."""
    normalized = normalize_case(text)
    fixed = fix_misspelling(normalized)
    extra_sentence = extract_last_words(fixed)
    final_text = " ".join(fixed) + " " + extra_sentence
    whitespace_count = count_whitespaces(text)
    return {"final_text": final_text, "whitespace_count": whitespace_count}


def run_text():
    """Functional entrypoint for text logic."""
    text = """
      tHis iz your homeWork, copy these Text to variable.

      You NEED TO normalize it fROM letter CASEs point oF View. also, create one MORE senTENCE witH LAST WoRDS of each existING SENtence and add it to the END OF this Paragraph.

      it iZ misspeLLing here. fix“iZ” with correct “is”, but ONLY when it Iz a mistAKE.

      last iz TO calculate nuMber OF Whitespace characteRS in this Tex. caREFULL, not only Spaces, but ALL whitespaces. I got 87.
    """

    result = process_text(text)
    print("Normalized + fixed text:\n")
    print(result["final_text"])
    print("\nWhitespace count:", result["whitespace_count"])


if __name__ == "__main__":
    run_dict()
    print("\n" + "="*80 + "\n")
    run_text()
