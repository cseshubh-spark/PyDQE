import re

# Step 1: Original text
text = """
  tHis iz your homeWork, copy these Text to variable.

  You NEED TO normalize it fROM letter CASEs point oF View. also, create one MORE senTENCE witH LAST WoRDS of each existING SENtence and add it to the END OF this Paragraph.

  it iZ misspeLLing here. fix“iZ” with correct “is”, but ONLY when it Iz a mistAKE.

  last iz TO calculate nuMber OF Whitespace characteRS in this Tex. caREFULL, not only Spaces, but ALL whitespaces. I got 87.
"""

# Step 2: Normalize letter case (sentence case)
sentences = re.split(r'(?<=[.!?])\s+', text.strip())
normalized_sentences = [s.capitalize() for s in sentences]

# Step 3: Replace wrong "iz" with "is" (whole word only)
normalized_sentences = [re.sub(r'\biz\b', 'is', s, flags=re.IGNORECASE) for s in normalized_sentences]

# Step 4: Collect last words of each sentence to form new sentence
last_words = [s.rstrip('.!?').split()[-1] for s in normalized_sentences if s]
extra_sentence = " ".join(last_words).capitalize() + "."

# Step 5: Join sentences back and add extra sentence
final_text = " ".join(normalized_sentences) + " " + extra_sentence

# Step 6: Count all whitespace characters in original text
whitespace_count = sum(1 for c in text if c.isspace())

# Print results
print("Normalized + fixed text:\n")
print(final_text)
print("\nWhitespace count:", whitespace_count)
