import re

with open('apps/frontend/src/app/admin/page.tsx', 'r') as f:
    content = f.read()

# Find the tab block
start_marker = "      {/* ── Tab: Riwayat Catatan PA ─────────────────────────────────────── */}"
end_marker = "      {/* Admin Note Modal */}"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("Could not find markers")
    exit(1)

# Extract the block
block = content[start_idx:end_idx]

# Remove the block from its current location
content = content[:start_idx] + content[end_idx:]

# Find where to insert it: before `        </div>\n      </main>`
insert_marker = "        </div>\n      </main>"
insert_idx = content.find(insert_marker)

if insert_idx == -1:
    print("Could not find insert point")
    exit(1)

# Insert the block
content = content[:insert_idx] + block + content[insert_idx:]

with open('apps/frontend/src/app/admin/page.tsx', 'w') as f:
    f.write(content)

print("Successfully moved the tab!")
