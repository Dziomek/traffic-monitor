import os
import csv
from collections import Counter

root_folder = "collected_30s"

label_counter = Counter()

print('Folder name: ', root_folder)
for dirpath, dirnames, filenames in os.walk(root_folder):
    for filename in filenames:
        if filename.endswith('.csv'):
            file_path = os.path.join(dirpath, filename)
            try:
                with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    header = next(reader, None)
                    for row in reader:
                        if row:
                            label = row[-1]
                            label_counter[label] += 1
            except Exception as e:
                print(f"Problem z plikiem {file_path}: {e}")

for label, count in label_counter.items():
    print(f"{label}: {count} times")