import os
import re
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    TkinterDnD = None


def process_text(content):
    """
    Cleans citation tags, fixes formatting issues caused by them,
    and automatically repairs common markdown structural errors
    while preserving code indentation.
    """
    cite_pat = r'\n[ \t]*(\[(?:cite_start|cite_end|cite:|source:)[^\]]*\])'
    content = re.sub(cite_pat, r' \1', content)
    content = re.sub(cite_pat, r' \1', content)

    pattern = r'\[(?:cite_start|cite_end|cite:[^\]]*|source:[^\]]*)\]'
    content = re.sub(pattern, '', content)

    content = re.sub(r'\*\s*\n\s*\*\*', '* **', content)
    content = re.sub(r'(?<=:)\s*\*\s*\*\*', '\n  * **', content)
    content = re.sub(r'\n{3,}', '\n\n', content)

    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)

    return content.rstrip()


def open_folder_in_explorer(path):
    """Opens the specified path in the default OS file manager."""
    if not path or not os.path.isdir(path):
        return

    path = os.path.normpath(path)
    try:
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        print(f"Failed to open folder: {e}")


class MarkdownExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Extractor GUI")
        self.root.geometry("700x700")

        self.setup_ui()

    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        content = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Project Root Selection
        root_lbl = ctk.CTkLabel(content, text="1. Project Root Directory (Drag & Drop or Browse):", font=("", 12, "bold"))
        root_lbl.pack(anchor=tk.W, pady=(0, 2))

        self.root_var = tk.StringVar()
        root_frame = ctk.CTkFrame(content, fg_color="transparent")
        root_frame.pack(fill=tk.X, pady=(0, 15))

        self.root_entry = ctk.CTkEntry(root_frame, textvariable=self.root_var)
        self.root_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ctk.CTkButton(root_frame, text="Browse", width=70, command=self.browse_root).pack(side=tk.LEFT, padx=(0, 5))
        ctk.CTkButton(root_frame, text="Open Folder", width=90, fg_color="#455A64", hover_color="#37474F", command=self.open_root_folder).pack(side=tk.LEFT)

        # File Input Selection
        md_lbl = ctk.CTkLabel(content, text="2A. Source Markdown File (Drag & Drop or Browse):", font=("", 12, "bold"))
        md_lbl.pack(anchor=tk.W, pady=(5, 2))

        self.md_var = tk.StringVar()
        md_frame = ctk.CTkFrame(content, fg_color="transparent")
        md_frame.pack(fill=tk.X, pady=(0, 15))

        self.md_entry = ctk.CTkEntry(md_frame, textvariable=self.md_var)
        self.md_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ctk.CTkButton(md_frame, text="Browse", width=70, command=self.browse_md).pack(side=tk.RIGHT)

        # Direct Text Input Selection
        text_lbl = ctk.CTkLabel(content, text="2B. Or Paste Markdown Directly (Auto-cleans citations on paste):", font=("", 12, "bold"))
        text_lbl.pack(anchor=tk.W, pady=(5, 2))

        self.text_input = ctk.CTkTextbox(content, height=120)
        self.text_input.pack(fill=tk.X, pady=(0, 15))

        # Bind paste events to the textbox specifically
        self.text_input.bind('<Control-v>', self.handle_paste_event)
        self.text_input.bind('<Command-v>', self.handle_paste_event)

        # Register Drag and Drop
        if TkinterDnD:
            self.root_entry.drop_target_register(DND_FILES)
            self.root_entry.dnd_bind('<<Drop>>', self.handle_root_drop)

            self.md_entry.drop_target_register(DND_FILES)
            self.md_entry.dnd_bind('<<Drop>>', self.handle_md_drop)

        # Controls
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill=tk.X, pady=(5, 10))

        ctk.CTkButton(btn_frame, text="Apply Changes", width=140, height=35, command=self.start_extraction).pack(side=tk.RIGHT)

        self.progress = ctk.CTkProgressBar(content, mode="indeterminate")
        self.progress.pack(fill=tk.X, pady=(5, 10))
        self.progress.set(0)

        self.log_text = ctk.CTkTextbox(content, state=tk.DISABLED, height=150)
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
            # Clear the text input to avoid confusion about which source is being used
            self.text_input.delete("1.0", tk.END)

            if self.root_var.get():
                self.start_extraction()
            else:
                self.log_message("Please set a Project Root before applying.")
        else:
            self.log_message("Error: Dropped item is not a file.")

    def handle_paste_event(self, event):
        # Allow the default paste to finish, then process the text slightly after
        self.root.after(50, self.clean_textbox_content)

    def clean_textbox_content(self):
        raw_content = self.text_input.get("1.0", tk.END)
        if raw_content.strip():
            self.log_message("Pasted text detected. Cleaning citations...")
            cleaned_content = process_text(raw_content)

            self.text_input.delete("1.0", tk.END)
            self.text_input.insert("1.0", cleaned_content)

            # Clear the file entry to avoid confusion
            self.md_var.set("")

    def browse_root(self):
        current_path = self.root_var.get()
        path = filedialog.askdirectory(initialdir=current_path if os.path.isdir(current_path) else None)
        if path:
            self.root_var.set(os.path.normpath(path))

    def open_root_folder(self):
        project_root = self.root_var.get()
        if os.path.isdir(project_root):
            open_folder_in_explorer(project_root)
        else:
            self.log_message("Error: Cannot open folder. Project Root is invalid or empty.")

    def browse_md(self):
        path = filedialog.askopenfilename()
        if path:
            self.md_var.set(os.path.normpath(path))
            self.text_input.delete("1.0", tk.END)

    def start_extraction(self):
        project_root = self.root_var.get()
        md_file = self.md_var.get()
        pasted_text = self.text_input.get("1.0", tk.END).strip()

        if not os.path.isdir(project_root):
            self.log_message("Error: Invalid Project Root Directory")
            return

        if not md_file and not pasted_text:
            self.log_message("Error: Please provide a Markdown file or paste text directly.")
            return

        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state=tk.DISABLED)

        self.progress.start()
        threading.Thread(target=self.execute_extraction, args=(project_root, md_file, pasted_text), daemon=True).start()

    def execute_extraction(self, project_root, md_file, pasted_text):
        self.log_message("Starting file extraction...")
        try:
            content = ""
            if pasted_text:
                self.log_message("Using direct text input.")
                content = pasted_text
            elif os.path.isfile(md_file):
                self.log_message(f"Using source file: {os.path.basename(md_file)}")
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Process the file content just in case it wasn't pasted
                content = process_text(content)

            lines = content.splitlines(True)

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
