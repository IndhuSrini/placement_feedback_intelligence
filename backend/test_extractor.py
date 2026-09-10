from nlp.extractor import extract_information


text = """
TCS technical round was moderate.
They asked what is normalization in DBMS?
Also explain 1NF and 2NF.
Coding question was to reverse a linked list.
They also asked about polymorphism in Java.
"""


result = extract_information(text)

print("\nExtracted Information:\n")

for key, value in result.items():

    print(f"{key}:")
    print(value)
    print()