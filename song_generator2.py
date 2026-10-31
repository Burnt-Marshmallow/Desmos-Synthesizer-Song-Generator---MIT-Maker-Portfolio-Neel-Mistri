import pyperclip as pc
import tkinter as tk
from tkinter import filedialog

alpha = "abcdefghjklmnopqrstuvwxyz"

piano_0freqs = {"C": 16.35, "C#": 17.32, "Db": 17.32, "D": 18.35, "D#": 19.45, "Eb": 19.45, "E": 20.60, "F": 21.83, "F#": 23.12, "Gb": 23.12, "G": 24.50, "G#": 25.96, "Gb": 25.96, "A": 27.50, "A#": 29.14, "Bb": 29.14, "B": 30.87}

def note_freq(note_code) -> int:
    if note_code == "_": return 0
    note = note_code[:-1]
    num = int(note_code[-1])
    return piano_0freqs[note]*2**num

class Note:

    def __init__(self, note, vol, dur) -> None:
        self.note = note
        self.frequency = note_freq(note)
        self.volume = vol
        self.duration = dur

    def to_desmos(self) -> str:
        return f"({self.frequency},{self.volume})"


class Song:

    def __init__(self, num_channels) -> None:
        self.channels = num_channels
        self.notes = [[] for _ in range(num_channels)]

    def add_note(self, note: Note, channel: int) -> None:
            self.notes[channel] += [note]

    def add_notes(self, notes: list[Note], channel: int) -> None:
            self.notes[channel] += notes

    def add_rest(self, duration, channel) -> None:
        self.notes[channel] += [Note("_", 0, duration)]

    def pop(self, channel) -> None:
        self.notes[channel] = self.notes[channel][:-1]

    def channel_len(self, channel) -> int:
        length = 0
        for note in self.notes[channel]:
            length += note.duration
        return length

    def get_max_len(self) -> int:
        max_len = 0
        for channel in self.notes:
            curr_max = 0
            for note in channel:
                curr_max += note.duration

            if curr_max > max_len: max_len = curr_max

        return max_len

    def export(self) -> str:
        final_song = ["" for _ in range(self.channels)]

        for channel in range(self.channels):
            for note in self.notes[channel]:
                for _ in range(note.duration):
                    final_song[channel] += note.to_desmos() + ","

        max_len = self.get_max_len()

        for i in range(self.channels):
            if self.channel_len(i) < max_len:
                final_song[i] += "(0,0)," * (max_len - self.channel_len(i))

        final_string = ""

        for idx, channel in enumerate(final_song):
            final_string += f"A_{idx + 1}=[{final_song[idx][:-1]}]\n"

        return final_string

    def to_str(self) -> str:
        final_song = [[] for _ in range(self.channels)]
        
        for channel in range(self.channels):
            for note in self.notes[channel]:
                for _ in range(note.duration):
                    final_song[channel].append((note.note, note.volume))


        max_len = self.get_max_len()
        
        for idx, channel in enumerate(self.notes):
            if self.channel_len(idx) < max_len:
                final_song[idx] += [("_","_") for _ in range(max_len - self.channel_len(idx))]


        final_string = "R\t" + "N\tV\t" * self.channels + "\n"

        for i in range(len(final_song[0])):
            final_string += f"{i}\t"
            for channel in final_song:
                if channel[i] == ("_", 0):
                    final_string += "_\t_\t"
                    continue

                letter = channel[i][0][:-1]
                num = channel[i][0][-1]

                final_string += f"{letter}{num}\t{channel[i][1]}\t"
            final_string += "\n"

        return final_string

    def __str__(self) -> str:
        final_song = [[] for _ in range(self.channels)]
        
        for channel in range(self.channels):
            for note in self.notes[channel]:
                for _ in range(note.duration):
                    final_song[channel].append((note.note, note.volume))


        max_len = self.get_max_len()
        
        for idx, channel in enumerate(self.notes):
            if self.channel_len(idx) < max_len:
                final_song[idx] += [("_","_") for _ in range(max_len - self.channel_len(idx))]


        final_string = "R\t" + "N\tV\t" * self.channels + "\n"

        for i in range(len(final_song[0])):
            final_string += f"{i}\t"
            for channel in final_song:
                if channel[i] == ("_", 0):
                    final_string += "\033[32;1m_\033[0m\t_\t"
                    continue

                letter = channel[i][0][:-1]
                num = channel[i][0][-1]

                final_string += f"\033[33m{letter}\033[32;1m{num}\033[0m\t{channel[i][1]}\t"
            final_string += "\n"

        return final_string



# Guide to Song Making
"""
To turn sheet music into a song:
1. Determine smallest length note (that will be the unit note)
2. Multiply up to get the rest of the note lengths
3. Arduously convert every note into algebraic notation (e.g. C4, E3, Db5)
4. Match the notes with the corresponding lengths and use the functions to build the song

Example Song: Sweden - C418

Shortest note: 8th note (1 unit)
Thus:
    Quarter Notes = 2 units
    Half Notes = 4 units
    Dotted Half = 6 units
    Whole Notes = 8 units

Notes for 4 Measures:
E2 G3 B3 (4)
F#2 (4) A4 (2)
B4 (2)
G2 (4) D4 F#4 (6)
B2 (4)
D4 (1)
E4 (1)
A2 (4) A3 C#4 (6)
G2 (4)
F#4 (1)
A4 (1)
D2 (8) C#4 E4 (8)

"""

# CONTROLS ------------------------------------------------------------

audio_channels = 6
song = Song(audio_channels)

# ---------------------------------------------------------------------


prev_edit_nums = []

def update_song_text(text) -> None:
    songText.config(state="normal")
    songText.delete("1.0", "end")

    def is_note(letter) -> bool:
        return any(letter == note for note in "ABCDEFG#b")

    for idx, letter in enumerate(text):
        if is_note(letter):
            songText.insert("end", letter, "yellow_text")
        elif letter.isdigit() and is_note(text[idx - 1]):
            songText.insert("end", letter, "green_text")
        else:
            songText.insert("end", letter, "white_text")


    songText.config(state="disabled")

def update_song(note) -> None:
    song.add_note(Note(note + str(octave.get()), volume.get(), duration.get()), int(channel.get() - 1))
    update_song_text(song.to_str())
    prev_edit_nums.append(int(channel.get() - 1))

def update_song_rest() -> None:
    song.add_rest(duration.get(), int(channel.get() - 1))
    update_song_text(song.to_str())
    prev_edit_nums.append(int(channel.get() - 1))

def undo_song() -> None:
    if prev_edit_nums:
        song.pop(prev_edit_nums[-1])
        prev_edit_nums.pop()
        update_song_text(song.to_str())

def save_to_file():
    file_path = filedialog.asksaveasfilename(
        initialfile="my_song.txt",          # Default filename suggestion
        defaultextension=".txt",            # Automatically adds .txt if user forgets
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")] # Filters dropdown
    )

    if file_path:
        try:
            # Grab everything from line 1, char 0 to the end of the text box
            desmos_text = song.export()
            styled_text = songText.get("1.0", "end-1c") # 'end-1c' leaves out the trailing newline
            
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(desmos_text)
                file.write("\n")
                file.write(styled_text)
                
            print(f"Successfully saved to: {file_path}")
        except Exception as e:
            print(f"Error saving file: {e}")


root = tk.Tk()
root.title("Music to Desmos Converter")
root.geometry("850x650")

# Controls
controlFrame = tk.Frame(root, bg="lightgray")
controlFrame.grid(row=0, column=0)

# Volume
volFrame = tk.Frame(controlFrame, bg="lightgray", width=750, height=300)
volFrame.pack(pady=10)

volLabel = tk.Label(volFrame, text="Volume")
volLabel.pack()

volBtn = tk.Button(volFrame, text="0.5", command=lambda: volume.set(0.5))
volBtn.pack()

volume = tk.Scale(volFrame, from_=0, to=1, resolution=0.01, length=200, orient="horizontal")
volume.pack()
volume.set(0.5)

# Duration
durFrame = tk.Frame(controlFrame, bg="lightgray", width=750, height=300)
durFrame.pack(pady=10)

durLabel = tk.Label(durFrame, text="Duration")
durLabel.pack()

duration = tk.Scale(durFrame, from_=1, to=16, length=200, orient="horizontal")
duration.pack()

# Octave
octFrame = tk.Frame(controlFrame, bg="lightgray", width=750, height=300)
octFrame.pack(pady=10)

octLabel = tk.Label(octFrame, text="Octave")
octLabel.pack()

octave = tk.Scale(octFrame, from_=0, to=8, length=200, orient="horizontal")
octave.pack()

# Channel
chanFrame = tk.Frame(controlFrame, bg="lightgray", width=750, height=300)
chanFrame.pack(pady=10)

chanLabel = tk.Label(chanFrame, text="Channel")
chanLabel.pack()

channel = tk.Scale(chanFrame, from_=1, to=audio_channels, length=100, orient="horizontal")
channel.pack()

# Piano
pianoBFrame = tk.Frame(controlFrame, bg="lightgray", width=750, height=300)
pianoBFrame.pack(pady=0)

pianoWFrame = tk.Frame(controlFrame, bg="lightgray", width=750, height=300)
pianoWFrame.pack(pady=0)

Wwidth = 3
Wheight = 3
Bwidth = 3
Bheight = 3

Ckey = tk.Button(pianoWFrame, bg="white", width=Wwidth, height=Wheight, text="C", command=lambda: update_song("C"))
Ckey.grid(row=1, column=0, sticky="we")

CSkey = tk.Button(pianoBFrame, bg="black", fg="white", width=Bwidth, height=Bheight, text="C#\nDb", command=lambda: update_song("C#"))
CSkey.grid(row=0, column=0)

Dkey = tk.Button(pianoWFrame, bg="white", width=Wwidth, height=Wheight, text="D", command=lambda: update_song("D"))
Dkey.grid(row=1, column=1)

DSkey = tk.Button(pianoBFrame, bg="black", fg="white", width=Bwidth, height=Bheight, text="D#\nEb", command=lambda: update_song("D#"))
DSkey.grid(row=0, column=1)

EmptyBtn = tk.Label(pianoBFrame, bg="lightgray", width=Bwidth)
EmptyBtn.grid(row=0, column=2)

Ekey = tk.Button(pianoWFrame, bg="white", width=Wwidth, height=Wheight, text="E", command=lambda: update_song("E"))
Ekey.grid(row=1, column=2)

Fkey = tk.Button(pianoWFrame, bg="white", width=Wwidth, height=Wheight, text="F", command=lambda: update_song("F"))
Fkey.grid(row=1, column=3)

FSkey = tk.Button(pianoBFrame, bg="black", fg="white", width=Bwidth, height=Bheight, text="F#\nGb", command=lambda: update_song("F#"))
FSkey.grid(row=0, column=3)

Gkey = tk.Button(pianoWFrame, bg="white", width=Wwidth, height=Wheight, text="G", command=lambda: update_song("G"))
Gkey.grid(row=1, column=4)

GSkey = tk.Button(pianoBFrame, bg="black", fg="white", width=Bwidth, height=Bheight, text="G#\nAb", command=lambda: update_song("G#"))
GSkey.grid(row=0, column=4)

Akey = tk.Button(pianoWFrame, bg="white", width=Wwidth, height=Wheight, text="A", command=lambda: update_song("A"))
Akey.grid(row=1, column=5)

ASkey = tk.Button(pianoBFrame, bg="black", fg="white", width=Bwidth, height=Bheight, text="A#\nBb", command=lambda: update_song("A#"))
ASkey.grid(row=0, column=5)

Bkey = tk.Button(pianoWFrame, bg="white", width=Wwidth, height=Wheight, text="B", command=lambda: update_song("B"))
Bkey.grid(row=1, column=6)

RestFrame = tk.Frame(controlFrame, bg="lightgray", width=750, height=300)
RestFrame.pack()

RestKey = tk.Button(RestFrame, bg="lightgray", width=Wwidth*9, text="Rest", command=update_song_rest)
RestKey.pack()

undoButton = tk.Button(controlFrame, text="Undo", width=10, height=3, command=undo_song)
undoButton.pack(pady=5)

exportButton = tk.Button(controlFrame, text="Copy to Clipboard", command=lambda: pc.copy(song.export()))
exportButton.pack(pady=5)

fileButton = tk.Button(controlFrame, text="Save to File", command=save_to_file)
fileButton.pack(pady=5)


# Song Preview
songFrame = tk.Frame(root, bg="lightgray")
songFrame.grid(row=0, column=1, sticky="ns")

songText = tk.Text(songFrame, bg="black", wrap="none", font=("Arial", 10), state="disabled")
songText.pack(side="left", fill="both", expand=True)
songText.tag_config("yellow_text", foreground="#ffff00")
songText.tag_config("green_text", foreground="#00ff00")
songText.tag_config("white_text", foreground="#ffffff")

yscrollbar = tk.Scrollbar(songFrame, command=songText.yview)
yscrollbar.pack(side="right", fill="y")

xscrollbar = tk.Scrollbar(songFrame, orient="horizontal", command=songText.xview)
xscrollbar.pack(side="bottom", fill="x")


root.mainloop()