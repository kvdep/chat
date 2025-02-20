import socket
import threading
import tkinter as tk
import webbrowser
import re
import tempfile
import os
from tkinter import simpledialog, scrolledtext
from PIL import Image, ImageTk
from sympy import preview

HOST = 'localhost'
PORT = 12345

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Client")
        self.root.geometry("500x400")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.nickname = simpledialog.askstring("Nickname", "Enter your nickname:")
        if not self.nickname:
            self.root.destroy()
            return

        self.chat_display = scrolledtext.ScrolledText(root, state='disabled', wrap='word')
        self.chat_display.grid(row=0, column=0, padx=10, pady=10, columnspan=2, sticky='nsew')
        self.chat_display.bind("<Button-1>", self.open_link)

        self.message_entry = tk.Entry(root)
        self.message_entry.grid(row=1, column=0, padx=10, pady=5, sticky='ew')
        self.message_entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=10, pady=5, sticky='ew')

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((HOST, PORT))
        self.client_socket.send(self.nickname.encode('utf-8'))

        self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.receive_thread.start()

        self.image_references = []

    def latex_to_image(self, latex_code):
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp:
            temp_filename = temp.name

        try:
            preview(
                f'$${latex_code}$$',
                viewer='file',
                filename=temp_filename,
                dvioptions=['-D', '150']
            )
            img = Image.open(temp_filename)
            img = img.convert("RGBA")
            img = img.resize((img.width // 2, img.height // 2), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)
            self.image_references.append(tk_img)
            return tk_img
        except Exception as e:
            return None
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                self.display_message(message)
            except:
                break

    def display_message(self, message):
        self.chat_display.config(state='normal')
        parts = re.split(r'(\$\$.*?\$\$)', message)
        for part in parts:
            if not part:
                continue
            if part.startswith('$$') and part.endswith('$$'):
                latex_code = part[2:-2].strip()
                image = self.latex_to_image(latex_code)
                if image:
                    self.chat_display.image_create(tk.END, image=image)
                    self.chat_display.insert(tk.END, ' ')
                else:
                    self.chat_display.insert(tk.END, f'$${latex_code}$$')
            else:
                self.chat_display.insert(tk.END, part)
        self.chat_display.insert(tk.END, '\n')
        self.chat_display.config(state='disabled')
        self.chat_display.yview(tk.END)

    def open_link(self, event):
        index = self.chat_display.index(tk.CURRENT)
        line = self.chat_display.get(index + " linestart", index + " lineend")
        words = line.split()
        for word in words:
            if word.startswith("http://") or word.startswith("https://"):
                webbrowser.open(word)
                break

    def send_message(self, event=None):
        message = self.message_entry.get()
        if message:
            self.client_socket.send(f"{self.nickname}: {message}".encode('utf-8'))
            self.message_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()
