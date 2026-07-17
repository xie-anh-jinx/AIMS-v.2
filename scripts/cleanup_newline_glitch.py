import os

files = [
    "/root/AIMS/apps/frontend/src/app/admin/page.tsx",
    "/root/AIMS/apps/frontend/src/app/advisor/page.tsx",
    "/root/AIMS/apps/frontend/src/app/prodi/page.tsx",
    "/root/AIMS/apps/frontend/src/app/student/page.tsx"
]

for filepath in files:
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Replace the literal characters '\n' with actual newlines or spaces.
        # But wait, python's string "..." if containing \n is just two chars.
        # So we look for "\\n"
        content = content.replace("\\n      <aside", "\n      <aside")
        content = content.replace("</div>\\n          ", "</div>\n          ")
        # In case there are other permutations
        content = content.replace(" />}\\n      <aside", " />}\n      <aside")

        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Removed literal \\n from {filepath}")
