import asyncio
import sys
import threading
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

BASE_DIR = Path(__file__).resolve().parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from app.myAPI import openai_request_endpoint
    from app.models import OpenAIInput
    from app.pdf_converter import pdf_to_text, text_to_pdf
except ImportError as e:
    raise ImportError(
        "Could not import the required project files.\n\n"
        "Expected structure:\n"
        "main_directory/\n"
        "├── summary_app.py\n"
        "├── pdf_converter.py\n"
        "└── app/\n"
        "    ├── myAPI.py\n"
        "    ├── models.py\n"
        "    ├── services.py\n"
        "    └── prompts.py\n"
    ) from e


class SummaryApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Paper Summary Studio")
        self.root.geometry("1240x800")
        self.root.minsize(1020, 700)
        self.root.configure(bg="#0f172a")

        self.selected_input_path: Path | None = None
        self.output_dir = BASE_DIR / "summaries"
        self.output_dir.mkdir(exist_ok=True)

        self.latest_summary = ""
        self.is_running = False

        self._configure_style()
        self._build_ui()
        self._set_export_state(False)
        self._set_status("Ready. Load a file or paste text, then click Summarize Now.")

    def _configure_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Main.TFrame", background="#0f172a")
        style.configure("Card.TFrame", background="#111827")
        style.configure("Header.TLabel", background="#0f172a", foreground="#f8fafc", font=("Segoe UI", 22, "bold"))
        style.configure("Sub.TLabel", background="#0f172a", foreground="#cbd5e1", font=("Segoe UI", 10))
        style.configure("CardTitle.TLabel", background="#111827", foreground="#e2e8f0", font=("Segoe UI", 12, "bold"))
        style.configure("Body.TLabel", background="#111827", foreground="#cbd5e1", font=("Segoe UI", 10))
        style.configure("Path.TLabel", background="#111827", foreground="#93c5fd", font=("Consolas", 9))
        style.configure("Status.TLabel", background="#0f172a", foreground="#93c5fd", font=("Segoe UI", 10, "italic"))
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=10)
        style.configure("Secondary.TButton", font=("Segoe UI", 10), padding=8)

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, style="Main.TFrame", padding=18)
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="Paper Summary Studio", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            outer,
            text="Use your existing pipeline from the app folder to summarize text and PDFs.",
            style="Sub.TLabel",
        ).pack(anchor="w", pady=(4, 14))

        top_bar = ttk.Frame(outer, style="Main.TFrame")
        top_bar.pack(fill="x", pady=(0, 14))

        self.summarize_button = ttk.Button(top_bar, text="Summarize Now", style="Action.TButton", command=self._start_summary)
        self.summarize_button.pack(side="left", padx=(0, 8))

        ttk.Button(top_bar, text="Load File", style="Secondary.TButton", command=self._load_file).pack(side="left", padx=(0, 8))
        ttk.Button(top_bar, text="Clear Input", style="Secondary.TButton", command=self._clear_input).pack(side="left", padx=(0, 8))
        ttk.Button(top_bar, text="Choose Folder", style="Secondary.TButton", command=self._choose_output_folder).pack(side="left", padx=(0, 8))

        self.hint_var = tk.StringVar(value="Step 1: Load or paste content. Step 2: Click Summarize Now.")
        ttk.Label(top_bar, textvariable=self.hint_var, style="Sub.TLabel").pack(side="right")

        content = ttk.Frame(outer, style="Main.TFrame")
        content.pack(fill="both", expand=True)

        left = ttk.Frame(content, style="Card.TFrame", padding=16)
        right = ttk.Frame(content, style="Card.TFrame", padding=16)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right.pack(side="left", fill="both", expand=True)

        self._build_input_panel(left)
        self._build_output_panel(right)

        bottom = ttk.Frame(outer, style="Main.TFrame")
        bottom.pack(fill="x", pady=(12, 0))
        self.status_var = tk.StringVar()
        ttk.Label(bottom, textvariable=self.status_var, style="Status.TLabel").pack(anchor="w")

    def _build_input_panel(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="Input", style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(parent, text="Paste text directly or import a .txt / .pdf file.", style="Body.TLabel").pack(anchor="w", pady=(4, 10))

        self.input_path_var = tk.StringVar(value="No file selected")
        ttk.Label(parent, textvariable=self.input_path_var, style="Path.TLabel").pack(anchor="w", pady=(0, 10))

        self.input_text = tk.Text(
            parent,
            wrap="word",
            font=("Segoe UI", 11),
            bg="#020617",
            fg="#e2e8f0",
            insertbackground="#f8fafc",
            selectbackground="#1d4ed8",
            relief="flat",
            padx=12,
            pady=12,
            undo=True,
            height=20,
        )
        self.input_text.pack(fill="both", expand=True)

        footer = ttk.Frame(parent, style="Card.TFrame")
        footer.pack(fill="x", pady=(12, 0))

        folder_block = ttk.Frame(footer, style="Card.TFrame")
        folder_block.pack(side="left", fill="both", expand=True)

        ttk.Label(folder_block, text="Summary Save Folder", style="CardTitle.TLabel").pack(anchor="w")
        self.output_dir_var = tk.StringVar(value=str(self.output_dir))
        ttk.Label(folder_block, textvariable=self.output_dir_var, style="Path.TLabel").pack(anchor="w", pady=(6, 0))

    def _build_output_panel(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="Summary", style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(parent, text="Review the result, then choose a format and export it.", style="Body.TLabel").pack(anchor="w", pady=(4, 10))

        self.output_text = tk.Text(
            parent,
            wrap="word",
            font=("Segoe UI", 11),
            bg="#020617",
            fg="#e2e8f0",
            insertbackground="#f8fafc",
            selectbackground="#1d4ed8",
            relief="flat",
            padx=12,
            pady=12,
            height=20,
            state="disabled",
        )
        self.output_text.pack(fill="both", expand=True)

        export_bar = ttk.Frame(parent, style="Card.TFrame")
        export_bar.pack(fill="x", pady=(12, 0))

        ttk.Label(export_bar, text="Export format:", style="Body.TLabel").pack(side="left", padx=(0, 8))

        self.export_format_var = tk.StringVar(value="TXT")
        self.export_format_dropdown = ttk.Combobox(
            export_bar,
            textvariable=self.export_format_var,
            values=["TXT", "PDF"],
            width=10,
            state="readonly",
        )
        self.export_format_dropdown.pack(side="left", padx=(0, 8))

        self.export_button = ttk.Button(export_bar, text="Export", style="Action.TButton", command=self._export_summary)
        self.export_button.pack(side="left")

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)

    def _set_export_state(self, enabled: bool) -> None:
        self.export_button.config(state="normal" if enabled else "disabled")
        self.export_format_dropdown.config(state="readonly" if enabled else "disabled")

    def _load_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Select input file",
            filetypes=[
                ("Supported files", "*.txt *.pdf"),
                ("Text files", "*.txt"),
                ("PDF files", "*.pdf"),
                ("All files", "*.*"),
            ],
        )
        if not file_path:
            return

        path = Path(file_path)
        try:
            if path.suffix.lower() == ".txt":
                content = path.read_text(encoding="utf-8")
            elif path.suffix.lower() == ".pdf":
                content = pdf_to_text(path)
            else:
                raise ValueError("Only .txt and .pdf files are supported.")
        except Exception as e:
            messagebox.showerror("Load Failed", str(e))
            self._set_status("Could not load file.")
            return

        self.selected_input_path = path
        self.input_path_var.set(str(path))
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", content)
        self._set_status(f"Loaded input from {path.name}")

    def _clear_input(self) -> None:
        self.selected_input_path = None
        self.input_path_var.set("No file selected")
        self.input_text.delete("1.0", "end")
        self.latest_summary = ""
        self._update_summary_box("")
        self._set_export_state(False)
        self._set_status("Input cleared.")

    def _choose_output_folder(self) -> None:
        folder = filedialog.askdirectory(title="Choose summary save folder")
        if not folder:
            return
        self.output_dir = Path(folder)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir_var.set(str(self.output_dir))
        self._set_status(f"Summary folder set to {self.output_dir}")

    def _start_summary(self) -> None:
        if self.is_running:
            return

        raw_text = self.input_text.get("1.0", "end").strip()
        if not raw_text:
            messagebox.showwarning("Missing Input", "Please paste text or load a file first.")
            return

        self.is_running = True
        self.summarize_button.config(state="disabled")
        self._set_export_state(False)
        self._set_status("Running your pipeline...")

        threading.Thread(target=self._run_pipeline, args=(raw_text,), daemon=True).start()

    def _run_pipeline(self, raw_text: str) -> None:
        try:
            result = asyncio.run(openai_request_endpoint(OpenAIInput(text=raw_text)))
            summary = result.final_text
            self.root.after(0, lambda: self._handle_summary_success(summary))
        except Exception as e:
            self.root.after(0, lambda: self._handle_summary_error(str(e)))

    def _handle_summary_success(self, summary: str) -> None:
        self.latest_summary = summary
        self._update_summary_box(summary)
        self._set_export_state(True)
        self.summarize_button.config(state="normal")
        self.is_running = False
        self._set_status("Summary generated successfully.")

    def _handle_summary_error(self, error_message: str) -> None:
        self.summarize_button.config(state="normal")
        self.is_running = False
        self._set_export_state(bool(self.latest_summary.strip()))
        self._set_status("Pipeline failed.")
        messagebox.showerror("Pipeline Error", error_message)

    def _update_summary_box(self, text: str) -> None:
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", text)
        self.output_text.config(state="disabled")

    def _safe_base_name(self) -> str:
        base_name = self.selected_input_path.stem if self.selected_input_path else "summary"
        cleaned = "".join(ch if ch.isalnum() or ch in ("_", "-") else "_" for ch in base_name).strip("_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{cleaned or 'summary'}_{timestamp}"

    def _export_summary(self) -> None:
        if not self.latest_summary.strip():
            messagebox.showwarning("No Summary", "Generate a summary first.")
            return

        selected_format = self.export_format_var.get().strip().upper()
        if selected_format == "TXT":
            self._export_txt()
        elif selected_format == "PDF":
            self._export_pdf()
        else:
            messagebox.showerror("Export Error", "Please choose a valid export format.")

    def _export_txt(self) -> None:
        suggested_name = f"{self._safe_base_name()}.txt"
        save_path = filedialog.asksaveasfilename(
            title="Save summary as TXT",
            initialdir=str(self.output_dir),
            initialfile=suggested_name,
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
        )
        if not save_path:
            return

        path = Path(save_path)
        path.write_text(self.latest_summary, encoding="utf-8")
        self._set_status(f"TXT exported to {path}")
        messagebox.showinfo("Export Complete", f"Saved to:\n{path}")

    def _export_pdf(self) -> None:
        suggested_name = f"{self._safe_base_name()}.pdf"
        save_path = filedialog.asksaveasfilename(
            title="Save summary as PDF",
            initialdir=str(self.output_dir),
            initialfile=suggested_name,
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
        )
        if not save_path:
            return

        path = Path(save_path)
        text_to_pdf(self.latest_summary, path)
        self._set_status(f"PDF exported to {path}")
        messagebox.showinfo("Export Complete", f"Saved to:\n{path}")


def main() -> None:
    root = tk.Tk()
    SummaryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
