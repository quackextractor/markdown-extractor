import os
import re
import threading
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    TkinterDnD = None


class MarkdownExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Extractor GUI")
        self.root.geometry("650x550")

        self.setup_ui()

    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        content = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Project Root Selection
        root_lbl = ctk.CTkLabel(content, text="Project Root Directory (Drag and Drop or Browse):")
        root_lbl.pack(anchor=tk.W, pady=(5, 2))

        self.root_var = tk.StringVar()
        root_frame = ctk.CTkFrame(content, fg_color="transparent")
        root_frame.pack(fill=tk.X, pady=(0, 15))

        self.root_entry = ctk.CTkEntry(root_frame, textvariable=self.root_var)
        self.root_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ctk.CTkButton(root_frame, text="Browse", width=80, command=self.browse_root).pack(side=tk.RIGHT)

        # Markdown File Selection
        md_lbl = ctk.CTkLabel(content, text="Markdown/Text File (Drag and Drop to Auto-Apply):")
        md_lbl.pack(anchor=tk.W, pady=(5, 2))

        self.md_var = tk.StringVar()
        md_frame = ctk.CTkFrame(content, fg_color="transparent")
        md_frame.pack(fill=tk.X, pady=(0, 15))

        self.md_entry = ctk.CTkEntry(md_frame, textvariable=self.md_var)
        self.md_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ctk.CTkButton(md_frame, text="Browse", width=80, command=self.browse_md).pack(side=tk.RIGHT)

        # Register Drag and Drop
        if TkinterDnD:
            self.root_entry.drop_target_register(DND_FILES)
            self.root_entry.dnd_bind('<<Drop>>', self.handle_root_drop)

            self.md_entry.drop_target_register(DND_FILES)
            self.md_entry.dnd_bind('<<Drop>>', self.handle_md_drop)

        # Controls
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill=tk.X, pady=(10, 10))

        ctk.CTkButton(btn_frame, text="Apply Changes", width=120, command=self.start_extraction).pack(side=tk.RIGHT)

        self.progress = ctk.CTkProgressBar(content, mode="indeterminate")
        self.progress.pack(fill=tk.X, pady=(10, 15))
        self.progress.set(0)

        self.log_text = ctk.CTkTextbox(content, state=tk.DISABLED, height=200)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def log_message(self, text):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def handle_root_drop(self, event):
        path = event.data.strip('{}')
        if os.path.isdir(path):
            self.root_var.set(os.path.normpath(path))
        else:
            self.log_message("Error: Dropped item is not a directory.")

    def handle_md_drop(self, event):
        path = event.data.strip('{}')
        if os.path.isfile(path):
            self.md_var.set(os.path.normpath(path))
            if self.root_var.get():
                self.start_extraction()
            else:
                self.log_message("Please set a Project Root before applying.")
        else:
            self.log_message("Error: Dropped item is not a file.")

    def browse_root(self):
        current_path = self.root_var.get()
        path = filedialog.askdirectory(initialdir=current_path if os.path.isdir(current_path) else None)
        if path:
            self.root_var.set(os.path.normpath(path))

    def browse_md(self):
        path = filedialog.askopenfilename()
        if path:
            self.md_var.set(os.path.normpath(path))

    def start_extraction(self):
        project_root = self.root_var.get()
        md_file = self.md_var.get()

        if not os.path.isdir(project_root):
            self.log_message("Error: Invalid Project Root Directory")
            return
        if not os.path.isfile(md_file):
            self.log_message("Error: Invalid Input File")
            return

        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state=tk.DISABLED)

        self.progress.start()
        threading.Thread(target=self.execute_extraction, args=(project_root, md_file), daemon=True).start()

    def execute_extraction(self, project_root, md_file):
        self.log_message("Starting file extraction...")
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            current_file = None
            in_code_block = False
            code_content = []
            files_updated = 0

            for line in lines:
                header_match = re.match(r'^###\s+`?([^`\n]+)`?', line)
                if header_match and not in_code_block:
                    current_file = header_match.group(1).strip()
                    continue

                if line.strip().startswith('```'):
                    if not in_code_block:
                        if current_file:
                            in_code_block = True
                            code_content = []
                    else:
                        in_code_block = False
                        if current_file:
                            target_path = os.path.join(project_root, current_file)
                            target_dir = os.path.dirname(target_path)

                            if target_dir:
                                os.makedirs(target_dir, exist_ok=True)

                            with open(target_path, 'w', encoding='utf-8') as out_f:
                                out_f.write("".join(code_content))

                            self.log_message(f"Updated: {current_file}")
                            files_updated += 1
                            current_file = None
                elif in_code_block:
                    code_content.append(line)

            self.log_message(f"\nExtraction completed successfully. {files_updated} files updated.")

        except Exception as e:
            self.log_message(f"Error during extraction: {e}")
        finally:
            self.progress.stop()


if __name__ == '__main__':
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    if TkinterDnD:
        root = TkinterDnD.Tk()
        is_dark = ctk.get_appearance_mode() == "Dark"
        bg_color = ctk.ThemeManager.theme["CTk"]["fg_color"][1 if is_dark else 0]
        root.configure(bg=bg_color, highlightthickness=0)

        if is_dark:
            try:
                import ctypes
                root.update()
                hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
                rendering_policy = 20
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, rendering_policy, ctypes.byref(ctypes.c_int(1)), 4
                )
            except Exception:
                pass
    else:
        root = ctk.CTk()

    app = MarkdownExtractorApp(root)
    root.mainloop()
