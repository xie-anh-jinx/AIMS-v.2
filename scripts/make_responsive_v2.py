import re

files_to_update = {
    "/root/AIMS/apps/frontend/src/app/advisor/page.tsx": {
        "aside": r'<aside className="w-\[280px\] bg-\[#111827\] flex flex-col fixed h-full z-20 border-r border-\[#1f2937\]">',
        "aside_repl": r'{mobileMenuOpen && <div className="fixed inset-0 bg-black/50 z-30 md:hidden" onClick={() => setMobileMenuOpen(false)} />}\n      <aside className={`w-[280px] bg-[#111827] flex flex-col fixed h-full z-40 border-r border-[#1f2937] transition-transform duration-300 ${mobileMenuOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"}`}>',
        "main": r'<main className="flex-1 ml-\[280px\] p-8 overflow-y-auto">',
        "main_repl": r'<main className="flex-1 md:ml-[280px] p-4 md:p-8 overflow-y-auto w-full">'
    },
    "/root/AIMS/apps/frontend/src/app/prodi/page.tsx": {
        "aside": r'<aside className="w-\[280px\] bg-\[#111827\] flex flex-col fixed h-full z-20 border-r border-\[#1f2937\]">',
        "aside_repl": r'{mobileMenuOpen && <div className="fixed inset-0 bg-black/50 z-30 md:hidden" onClick={() => setMobileMenuOpen(false)} />}\n      <aside className={`w-[280px] bg-[#111827] flex flex-col fixed h-full z-40 border-r border-[#1f2937] transition-transform duration-300 ${mobileMenuOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"}`}>',
        "main": r'<main className="flex-1 md:ml-\[260px\] p-4 md:p-8 overflow-y-auto w-full">',
        "main_repl": r'<main className="flex-1 md:ml-[280px] p-4 md:p-8 overflow-y-auto w-full">'
    },
    "/root/AIMS/apps/frontend/src/app/student/page.tsx": {
        "aside": r'<aside className="w-64 glass-sidebar p-6 flex flex-col fixed h-full z-20">',
        "aside_repl": r'{mobileMenuOpen && <div className="fixed inset-0 bg-black/50 z-30 md:hidden" onClick={() => setMobileMenuOpen(false)} />}\n      <aside className={`w-64 glass-sidebar p-6 flex flex-col fixed h-full z-40 transition-transform duration-300 ${mobileMenuOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"}`}>',
        "main": r'<main className="flex-1 ml-64 p-8 overflow-y-auto w-full">',
        "main_repl": r'<main className="flex-1 md:ml-64 p-4 md:p-8 overflow-y-auto w-full">'
    }
}

for filepath, patches in files_to_update.items():
    with open(filepath, 'r') as f:
        content = f.read()

    # Add mobileMenuOpen overlay + classes
    if patches["aside"] in content:
        content = content.replace(patches["aside"], patches["aside_repl"])
    
    # Add mobile Main container layout
    if not re.search(patches["main_repl"].replace('[', r'\[').replace(']', r'\]'), content):
        content = re.sub(patches["main"], patches["main_repl"], content)

    # Inject Hamburger button right after <div className="max-w-[1200px] mx-auto w-full">
    if "md:hidden flex items-center justify-between mb-6" not in content and "md:hidden flex items-center mb-6" not in content:
        hamb_target = r'(<div className="max-w-\[1200px\] mx-auto w-full">\s*)'
        hamb_replacement = r'\1<div className="md:hidden flex items-center mb-6"><button onClick={() => setMobileMenuOpen(true)} className="text-slate-300 hover:text-white p-2 -ml-2"><Menu size={24} /></button></div>\n          '
        content = re.sub(hamb_target, hamb_replacement, content)

    with open(filepath, 'w') as f:
        f.write(content)
        
    print(f"Patched strictly: {filepath}")
