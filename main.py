import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import yt_dlp
import re

#pyinstaller --onefile --noconsole --icon=logo.ico main.py


def extract_comments(video_url):
    ydl_opts = {
        'quiet': True,
        'extractor_args': {'youtube:comment_sort': ['top']},
        'skip_download': True,
        'extract_flat': True,
        'getcomments': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)
            comments = info.get("comments", [])

            filtered_comments = [
                (c.get("author", "Unknown"), c.get("text", "")) for c in comments
                if re.search(r'\blocation\b', c.get("text", ""), re.IGNORECASE)
            ]
            return filtered_comments
        except Exception as e:
            messagebox.showerror("Error", f"Error extracting comments: {e}")
            return []


def start_extraction():
    url = entry_url.get()
    if not url:
        messagebox.showwarning("Warning", "Please enter a YouTube link!")
        return

    loading_label.configure(text="Extracting comments... (Please wait)", fg_color="black")
    root.update_idletasks()

    global extracted_comments
    extracted_comments = extract_comments(url)
    text_output.delete('0.0', "end")

    if extracted_comments:
        for author, comment in extracted_comments:
            text_output.insert("end", f"{author}: {comment}\n\n")
    else:
        text_output.insert("end", "No comments containing 'location' found.")

    loading_label.configure(text="")


def save_to_excel():
    if not extracted_comments:
        messagebox.showwarning("Warning", "No comments to save!")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
    if not file_path:
        return

    try:
        df = pd.DataFrame(extracted_comments, columns=["User", "Comment"])
        df.to_excel(file_path, index=False)
        messagebox.showinfo("Success", f"Comments have been saved to {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save file: {e}")


# Create UI
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("YouTube Comment Scraper")
root.geometry("600x500")
root.configure(fg_color="black")
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)


ctk.CTkLabel(root, text="Enter YouTube video link:", fg_color="black").pack(pady=5)
entry_url = ctk.CTkEntry(root, width=400)
entry_url.pack(pady=5, fill="x", padx=10)

btn_extract = ctk.CTkButton(root, text="Start", command=start_extraction, fg_color="red")
btn_extract.pack(pady=5, fill="x", padx=10)

loading_label = ctk.CTkLabel(root, text="", fg_color="black")
loading_label.pack()

text_output = ctk.CTkTextbox(root, width=500, height=250, fg_color="black", text_color="white")
text_output.pack(pady=5, fill="both", expand=True, padx=10)

btn_save = ctk.CTkButton(root, text="Save to Excel", command=save_to_excel, fg_color="red")
btn_save.pack(pady=5, fill="x", padx=10)

extracted_comments = []
root.mainloop()