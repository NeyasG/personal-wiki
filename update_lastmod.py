import sys
import re
from datetime import datetime, timedelta, timezone # Add timedelta

# Define a threshold - only update if the existing time is older than this
UPDATE_THRESHOLD = timedelta(minutes=10)

def parse_iso_datetime(dt_str):
    """Helper to parse ISO 8601 strings, handling potential timezone formats."""
    try:
        # Handle Z for UTC
        if dt_str.endswith('Z'):
            dt_str = dt_str[:-1] + '+00:00'
        # Handle formats like +HHMM (add colon)
        elif len(dt_str) > 5 and dt_str[-3] != ':' and dt_str[-5] in ['+', '-']:
             dt_str = dt_str[:-2] + ':' + dt_str[-2:]
        return datetime.fromisoformat(dt_str)
    except ValueError:
        print(f"Warning: Could not parse existing timestamp '{dt_str}'")
        return None

def update_lastmod(filename):
    try:
        with open(filename, 'r+', encoding='utf-8') as f:
            content = f.read()
            local_now = datetime.now().astimezone()
            now_iso = local_now.strftime('%Y-%m-%dT%H:%M:%S%z')
            if len(now_iso) > 5 and now_iso[-3] != ':':
                 now_iso = now_iso[:-2] + ':' + now_iso[-2:]

            lastmod_pattern = re.compile(r'^(lastmod:\s*)(.*)$', re.MULTILINE)
            match = lastmod_pattern.search(content)

            should_update = False
            new_content = content # Default to original content

            if match:
                existing_timestamp_str = match.group(2).strip()
                existing_timestamp = parse_iso_datetime(existing_timestamp_str)

                if existing_timestamp:
                    # Compare existing time with current time
                    if (local_now - existing_timestamp) > UPDATE_THRESHOLD:
                        print(f"Existing timestamp {existing_timestamp_str} is older than threshold. Updating.")
                        should_update = True
                    else:
                        print(f"Existing timestamp {existing_timestamp_str} is recent. No update needed.")
                else:
                    # Could not parse existing timestamp, maybe invalid format? Update it.
                    print(f"Could not parse existing timestamp '{existing_timestamp_str}'. Updating.")
                    should_update = True

                if should_update:
                    new_content = lastmod_pattern.sub(rf'\g<1>{now_iso}', content) # Use group 1 to keep 'lastmod: '

            else:
                # lastmod doesn't exist, add it
                print(f"No existing lastmod found. Adding.")
                should_update = True # Flag that we need to potentially modify content
                date_pattern = re.compile(r'^date:\s*.*$', re.MULTILINE)
                date_match = date_pattern.search(content)
                if date_match:
                    insert_pos = date_match.end()
                    new_content = content[:insert_pos] + f'\nlastmod: {now_iso}' + content[insert_pos:]
                else:
                     frontmatter_start = content.find('---')
                     if frontmatter_start != -1:
                         frontmatter_end = content.find('---', frontmatter_start + 3)
                         if frontmatter_end != -1:
                              new_content = content[:frontmatter_end] + f'lastmod: {now_iso}\n' + content[frontmatter_end:]
                         # else: Cannot find closing '---', content remains unchanged, should_update stays False implicitly unless set above

            # Only write if content actually changed
            if should_update and new_content != content:
                f.seek(0)
                f.write(new_content)
                f.truncate()
                print(f"Updated lastmod in {filename}")
                return True # Indicates modification
            elif not should_update:
                 return False # No update needed based on threshold
            else:
                 # should_update was true, but new_content == content (e.g., couldn't find place to insert)
                 print(f"Update flagged but content unchanged for {filename}.")
                 return False


    except Exception as e:
        print(f"Error processing {filename}: {e}")
    return False # No modification or error

if __name__ == "__main__":
    modified = False
    if len(sys.argv) > 1:
        for filename in sys.argv[1:]:
            if filename.endswith('.md'):
                 if update_lastmod(filename):
                     modified = True
    else:
        print("No filenames provided to update_lastmod.py script.")
    # No explicit exit needed here, pre-commit handles it.