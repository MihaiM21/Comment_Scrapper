import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import yt_dlp
import re
from geotext import GeoText
from urllib.parse import quote

#pyinstaller --onefile --noconsole --icon=logo.ico main.py

# Lista cu toate statele din SUA
us_states = {
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida",
    "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
    "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska",
    "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota",
    "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
}


def generate_google_maps_link(location):
    """Generează un link Google Maps pentru o locație validă."""
    query = quote(location)
    return f"https://www.google.com/maps/search/?api=1&query={query}"


def extract_valid_location(text):
    """Extrage orașe, state și țări din textul întregului comentariu."""
    places = GeoText(text)

    detected_cities = places.cities if places.cities else []
    detected_countries = places.countries if places.countries else []
    detected_states = [state for state in us_states if state.lower() in text.lower()]

    if detected_cities:
        return detected_cities[0], "City"  # Returnează primul oraș valid
    elif detected_states:
        return detected_states[0], "State"  # Returnează primul stat valid
    elif detected_countries:
        return detected_countries[0], "Country"  # Returnează prima țară validă
    return None, None  # Dacă nu găsim nimic valid


def extract_comments(video_url):
    """Extrage comentariile din videoclipul YouTube dat."""
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

            extracted_data = []
            for c in comments:
                author = c.get("author", "Unknown")
                text = c.get("text", "")

                # Verifică dacă textul conține "location" și/sau o locație validă
                if re.search(r'\blocation\b', text, re.IGNORECASE) or extract_valid_location(text)[0]:
                    valid_location, loc_type = extract_valid_location(text)
                    google_maps_link = generate_google_maps_link(
                        valid_location) if valid_location else "No valid location found"

                    extracted_data.append(
                        (author, text, valid_location if valid_location else "Unknown", loc_type, google_maps_link))

            return extracted_data
        except Exception as e:
            messagebox.showerror("Error", f"Error extracting comments: {e}")
            return []


def start_extraction():
    """Pornește extracția și afișează rezultatele în interfață."""
    url = entry_url.get()
    if not url:
        messagebox.showwarning("Warning", "Please enter a YouTube link!")
        return

    loading_label.configure(text="Extracting comments...", fg_color="blue")
    root.update_idletasks()

    global extracted_comments
    extracted_comments = extract_comments(url)
    text_output.delete('0.0', "end")

    if extracted_comments:
        for author, comment, location, loc_type, link in extracted_comments:
            text_output.insert("end", f"{author}: {comment}\nLocation: {location} ({loc_type})\nLink: {link}\n\n")
    else:
        text_output.insert("end", "No valid locations found in comments.")

    loading_label.configure(text="")


def save_to_excel():
    """Salvează comentariile extrase și locațiile într-un fișier Excel."""
    if not extracted_comments:
        messagebox.showwarning("Warning", "No comments to save!")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
    if not file_path:
        return

    try:
        df = pd.DataFrame(extracted_comments, columns=["User", "Comment", "Location", "Type", "Google Maps Link"])
        df.to_excel(file_path, index=False)
        messagebox.showinfo("Success", f"Comments have been saved to {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save file: {e}")


# Creare interfață
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
