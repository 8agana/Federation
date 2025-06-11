#!/usr/bin/env python3
import tkinter as tk

print("Creating window...")
root = tk.Tk()
root.title("Simple Test")
root.geometry("400x300")

label = tk.Label(root, text="If you see this, tkinter works!")
label.pack(pady=50)

button = tk.Button(root, text="Click me", command=root.quit)
button.pack()

print("Starting mainloop...")
root.mainloop()
print("Done!")