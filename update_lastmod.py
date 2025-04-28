import sys
import re
from datetime import datetime, timezone

def update_lastmod(filename):
    try:
        with open(filename, 'r+', encoding='utf-8') as f:
            content = f.read()
            now_iso = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')
            # Ensure the timezone format has a colon if needed, adjust strftime if necessary
            # Python's %z gives +HHMM, Hugo might prefer +HH:MM. Let's adjust.
            if len(now_iso) > 5 and now_iso[-3] != ':':
                 now_iso = now_iso[:-2] + ':' + now_iso[-2:]

            # Simple regex to find and replace lastmod - adjust if your format varies
            lastmod_pattern = re.compile(r'^lastmod:\s*.*$', re.MULTILINE)

            if lastmod_pattern.search(content):
                new_content = lastmod_pattern.sub(f'lastmod: {now_iso}', content)
            else:
                # If lastmod doesn't exist, add it (e.g., after date)
                # This part might need refinement based on your frontmatter structure
                date_pattern = re.compile(r'^date:\s*.*$', re.MULTILINE)
                match = date_pattern.search(content)
                if match:
                    insert_pos = match.end()
                    new_content = content[:insert_pos] + f'\nlastmod: {now_iso}' + content[insert_pos:]
                else: # Fallback: add near the top if date isn't found
                     frontmatter_end = content.find('---', 3) # Find second '---'
                     if frontmatter_end != -1:
                          new_content = content[:frontmatter_end] + f'lastmod: {now_iso}\n' + content[frontmatter_end:]
                     else: # Cannot find frontmatter, do nothing
                          new_content = content


            if new_content != content:
                f.seek(0)
                f.write(new_content)
                f.truncate()
                print(f"Updated lastmod in {filename}")
                return True # Indicates modification
    except Exception as e:
        print(f"Error processing {filename}: {e}")
    return False # No modification or error

if __name__ == "__main__":
    modified = False
    for filename in sys.argv[1:]:
        if filename.endswith('.md'):
             if update_lastmod(filename):
                 modified = True

    # If files were modified, they need to be re-staged
    # pre-commit handles this automatically if the script exits non-zero
    # However, explicitly exiting non-zero if modified is clearer
    if modified:
         # Exit with 1 to signal files were changed and need re-staging
         # Note: pre-commit usually handles adding modified files back automatically
         # sys.exit(1) # Might not be necessary depending on pre-commit version/config
         pass