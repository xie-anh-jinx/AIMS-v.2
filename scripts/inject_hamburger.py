import re

files_to_update = [
    "/root/AIMS/apps/frontend/src/app/advisor/page.tsx",
    "/root/AIMS/apps/frontend/src/app/student/page.tsx"
]

for filepath in files_to_update:
    with open(filepath, 'r') as f:
        content = f.read()

    # Inject Hamburger button right after <div className="max-w-6xl mx-auto">
    if "md:hidden flex items-center mb-6" not in content:
        hamb_target = r'(<div className="max-w-6xl mx-auto">\s*)'
        hamb_replacement = r'\1<div className="md:hidden flex items-center mb-6"><button onClick={() => setMobileMenuOpen(true)} className="text-slate-300 hover:text-white p-2 -ml-2"><Menu size={24} /></button></div>' + '\n          '
        content = re.sub(hamb_target, hamb_replacement, content)

    with open(filepath, 'w') as f:
        f.write(content)
        
    print(f"Injected hamburger menu to: {filepath}")
