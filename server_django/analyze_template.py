
import re
import os

def analyze_template(path):
    if not os.path.exists(path):
        print(f"Error: {path} not found")
        return

    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    stack = []
    
    # We want to match tags. Simple regex for {% tag ... %}
    # We need to capture the tag name.
    tag_re = re.compile(r'{%\s*([a-zA-Z0-9_]+)')

    print(f"Analyzing {path}...")
    for i, line in enumerate(lines):
        line_num = i + 1
        matches = tag_re.finditer(line)
        for match in matches:
            tag = match.group(1)
            
            # Skip endblock/endif/etc if they are part of a variable or string? 
            # Ideally we'd parse properly, but let's assume valid django syntax.
            
            # Tags that open a block
            if tag in ['if', 'for', 'block', 'with', 'while']:
                stack.append((tag, line_num))
                print(f"{line_num}: PUSH {tag} -> Stack: {[t[0] for t in stack]}")
            
            # Tags that close a block
            elif tag in ['endif', 'endfor', 'endblock', 'endwith', 'endwhile']:
                if not stack:
                    print(f"ERROR: Found {tag} at line {line_num} but stack is empty!")
                    return
                
                last_tag, last_line = stack[-1]
                expected_end = 'end' + last_tag
                
                if tag == expected_end:
                    stack.pop()
                    print(f"{line_num}: POP {tag} (matched {last_tag}) -> Stack: {[t[0] for t in stack]}")
                else:
                    print(f"ERROR: Mismatch at line {line_num}. Found {tag}, expected {expected_end} (opened at line {last_line})")
                    return
            
            # Tags that are intermediate (elif, else, empty) do not change stack depth but must be inside a block
            elif tag in ['elif', 'else', 'empty']:
                 if not stack:
                    print(f"ERROR: Found {tag} at line {line_num} but stack is empty!")
                 else:
                    print(f"{line_num}: SEEN {tag} (inside {stack[-1][0]})")

    if stack:
        print("\nERROR: Unclosed tags at end of file:")
        for tag, line in stack:
            print(f"  {tag} opened at line {line}")
    else:
        print("\nSUCCESS: All tags balanced.")

if __name__ == "__main__":
    analyze_template(r'c:\Users\oladi\sources\rccghgz\server_django\templates\operations\attendance_list_v5.html')
