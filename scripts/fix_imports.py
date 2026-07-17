import os

files = [
    "/root/AIMS/apps/frontend/src/app/admin/page.tsx",
    "/root/AIMS/apps/frontend/src/app/advisor/page.tsx",
    "/root/AIMS/apps/frontend/src/app/prodi/page.tsx",
    "/root/AIMS/apps/frontend/src/app/student/page.tsx"
]

for fpath in files:
    if os.path.exists(fpath):
        with open(fpath, "r") as f:
            content = f.read()
        
        # 1. Remove from next/navigation
        content = content.replace("import { Menu, useRouter }", "import { useRouter }")
        
        # 2. Add to lucide-react safely
        if "from 'lucide-react'" in content and "Menu," not in content:
            # We find the Lucide-react import which looks like:
            # import { 
            #   Users, AlertTriangle...
            # } from 'lucide-react';
            # Let's just insert it at the very first element of lucide-react import list
            content = content.replace("import {\n  Users", "import {\n  Menu, Users")
            content = content.replace("import { \n  Users", "import { \n  Menu, Users")
            content = content.replace("import { Users", "import { Menu, Users")
            # If nothing worked, fallback: insert at top
            if "Menu," not in content:
                content = content.replace("from 'lucide-react';", "from 'lucide-react';\nimport { Menu } from 'lucide-react';")

        with open(fpath, "w") as f:
            f.write(content)
        print(f"Fixed imports in: {fpath}")
