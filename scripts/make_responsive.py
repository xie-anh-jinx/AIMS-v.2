import os
import re

files_to_process = [
    "/root/AIMS/apps/frontend/src/app/admin/page.tsx",
    "/root/AIMS/apps/frontend/src/app/advisor/page.tsx",
    "/root/AIMS/apps/frontend/src/app/prodi/page.tsx",
    "/root/AIMS/apps/frontend/src/app/student/page.tsx"
]

for filepath in files_to_process:
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        continue
        
    with open(filepath, 'r') as f:
        content = f.read()

    # 1. Add Menu icon to imports if not present
    if "from 'lucide-react';" in content and "Menu," not in content:
        content = re.sub(r'import \{\s*', r'import { Menu, ', content, count=1)
        
    # 2. Add mobileMenuOpen state
    if "mobileMenuOpen" not in content:
        # Find first useState inside the main component
        content = re.sub(
            r'(const \[.*?\] = useState.*?;)', 
            r'const [mobileMenuOpen, setMobileMenuOpen] = useState(false);\n  \1', 
            content, count=1
        )
        
    # 3. Modify Layout container
    # From: <div className="flex min-h-screen font-sans bg-[#0b1121] text-slate-300">
    # (Just keeping it as is, it's fine)
    
    # 4. Modify Aside
    # From: <aside className="w-[260px] bg-[#111827] flex flex-col fixed h-full z-20 border-r border-[#1f2937]">
    aside_target = r'<aside className="w-\[260px\] bg-\[#111827\] flex flex-col fixed h-full z-20 border-r border-\[#1f2937\]">'
    aside_replacement = (
        "{mobileMenuOpen && <div className=\"fixed inset-0 bg-black/50 z-30 md:hidden\" onClick={() => setMobileMenuOpen(false)} />}\n      "
        r'<aside className={`w-[260px] bg-[#111827] flex flex-col fixed h-full z-40 border-r border-[#1f2937] transition-transform duration-300 ${mobileMenuOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"}`}>'
    )
    if "mobileMenuOpen &&" not in content:
        content = re.sub(aside_target, aside_replacement, content)
        
    # 5. Modify Main
    # From: <main className="flex-1 ml-[260px] p-8 overflow-y-auto">
    main_target = r'<main className="flex-1 ml-\[260px\] p-8 overflow-y-auto">'
    main_replacement = r'<main className="flex-1 md:ml-[260px] p-4 md:p-8 overflow-y-auto w-full">'
    content = re.sub(main_target, main_replacement, content)
    
    # 6. Add Hamburger inside main
    # Right after <div className="max-w-[1200px] mx-auto w-full">
    if "md:hidden flex items-center justify-between mb-6" not in content:
        hamb_target = r'(<div className="max-w-\[1200px\] mx-auto w-full">\s*)'
        hamb_replacement = r'\1<div className="md:hidden flex items-center mb-6"><button onClick={() => setMobileMenuOpen(true)} className="text-slate-300 hover:text-white p-2 -ml-2"><Menu size={24} /></button></div>\n          '
        content = re.sub(hamb_target, hamb_replacement, content)
        
    # 7. Grid modifications
    content = content.replace('grid-cols-2 lg:grid-cols-4', 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4')
    content = content.replace('grid-cols-1 md:grid-cols-3', 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3')
    content = content.replace('grid-cols-1 lg:grid-cols-3', 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3')
    
    # Also adjust some paddings around tables
    content = content.replace('<table className="w-full text-left text-sm', '<div className="overflow-x-auto w-full"><table className="w-full text-left text-sm min-w-[700px]')
    content = content.replace('</table>', '</table></div>')
    
    with open(filepath, 'w') as f:
        f.write(content)
        
    print(f"Processed: {filepath}")
