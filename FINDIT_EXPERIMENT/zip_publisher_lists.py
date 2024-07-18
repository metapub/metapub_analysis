import sys
import re

def read_journals_from_text(file_path):
    journals = set()
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            # Skip lines that contain Python code-like patterns
            if not re.search(r'[:=]', line):
                if line:
                    journals.add(line)
    return journals

def read_journals_from_python(file_path):
    journals = set()
    with open(file_path, 'r') as file:
        content = file.read()
        # Find all lists with more than 4 entries
        lists = re.findall(r'\[([^\]]+)\]', content)
        for lst in lists:
            items = [item.strip().strip("'\"") for item in lst.split(',') if item.strip()]
            if len(items) > 4:
                journals.update(items)
    return journals

def main(file1, file2):
    if file1.endswith('.py'):
        journals1 = read_journals_from_python(file1)
    else:
        journals1 = read_journals_from_text(file1)
    
    if file2.endswith('.py'):
        journals2 = read_journals_from_python(file2)
    else:
        journals2 = read_journals_from_text(file2)

    all_journals = journals1.union(journals2)
    sorted_journals = sorted(all_journals)

    for journal in sorted_journals:
        print(journal)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python process_journals.py <file1> <file2>")
        sys.exit(1)
    
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    
    main(file1, file2)

