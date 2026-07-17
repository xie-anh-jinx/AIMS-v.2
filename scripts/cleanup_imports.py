import os
import re

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
        
        # 1. Strip 'Menu' from all imports that are NOT lucide-react
        # Example: import { Menu, useState } from 'react'; -> import { useState } from 'react';
        # Example: import { Menu, useRouter } from 'next/navigation'; -> import { useRouter } from 'next/navigation';
        # Example: import { ..., Menu } from '...'
        
        def filter_import(match):
            import_str = match.group(0)
            if 'lucide-react' in import_str:
                return import_str # Don't strip from lucide-react
                
            # Strip Menu from the bracketed area
            inner = match.group(1)
            # Remove Menu carefully
            items = [x.strip() for x in inner.split(',')]
            items = [x for x in items if x != 'Menu' and x != '']
            new_inner = ", ".join(items)
            
            return import_str.replace(inner, new_inner)

        content = re.sub(r'import\s+\{([^}]+)\}\s+from\s+[\'"](?!(?:lucide-react))([^\'"]+)[\'"]', filter_import, content)
        
        # 2. Ensure Menu is IN lucide-react
        if "from 'lucide-react'" in content and "Menu" not in content[:content.find("from 'lucide-react'")]:
             content = re.sub(r'(import\s+\{)([^}]+)(\}\s+from\s+[\'"]lucide-react[\'"])', r'\1 \2, Menu \3', content)

        if "import { Menu } from 'lucide-react';" not in content and 'Menu' not in content[:content.find("from 'lucide-react'")]:
            content = content.replace("from 'lucide-react';", "from 'lucide-react';\nimport { Menu } from 'lucide-react';")
            
        with open(fpath, "w") as f:
            f.write(content)
        print(f"Fixed imports cleanly in: {fpath}")
