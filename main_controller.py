from pytube import YouTube
import tkinter as tk
from tkinter import messagebox
from main_window import MainWindow
import os
import requests


class MainController(tk.Frame):
    """
    Controller for our views
    """

    def __init__(self, parent):
        """Creates the main window"""
        tk.Frame.__init__(self, parent)
        # creates an instance of the MainWindow class
        self._root_win = tk.Toplevel()
        self._main_window = MainWindow(self._root_win, self)

        # defines a list to add all of the downloaded video titles
        self._video_titles = []

        # call this function to add all the names to the list at startup
        self.list_titles_callback()

    def download_callback(self, event):
        """Downloads a YouTube video with the specified URL
        Posts the video data to the API"""
        link = self._main_window.get_link()  # returns the input from the entry box
        yt = YouTube(link)  # creates a YouTube object
        video = yt.streams.first()  # chooses the first format available
        file_location = video.download(os.getcwd() +
                                   "\\YouTube_Downloads")  # downloads the video to the
                                                            # specified directory

        # creates a dictionary with the videos properties
        data = {'title': yt.title,
                'author': yt.author,
                'resolution': video.resolution,
                'frame_rate': video.fps,
                'pathname': os.getcwd() + "\\YouTube_Downloads\\",
                'filename': os.path.basename(file_location)
                }

        # posts data to API
        requests.post("http://localhost:5000/videos", json=data)
        msg = "Video has been downloaded."
        messagebox.showinfo(title="Downloaded", message=msg)
        self.list_titles_callback()

    def list_titles_callback(self):
        """ Lists video titles in listbox.
        Gets all the videos stored in the database and adds the title"""
        self._video_titles.clear()  # removes all items in the list

        # get request to the API and returns a list of videos
        response = requests.get("http://localhost:5000/videos/all")
        video_list = response.json()
        for video in video_list:
            self._video_titles.append(video['title'])

        # inserts the titles to the tkinter listbox
        self._main_window.insert_to_listbox(self._video_titles)

    def delete_callback(self):
        """ Deletes selected video from the library. """
        index = self._main_window.get_index()   # returns index of title in listbox
        if self._main_window.get_title() == "":    # checks if you selected a video before deleting
            msg_str = "You must select a video first."
            messagebox.showinfo(title="Error", message=msg_str)
        else:
            # gets a list of all the videos in the database
            get_response = requests.get("http://localhost:5000/videos/all")
            video_list = get_response.json()
            video = video_list[index]   # gets the specific video you chose
            filename = video['filename']
            del_response = requests.delete(
                        "http://localhost:5000/videos/" + filename
                        )   # sends a delete request to the API

            if del_response.status_code == 200:
                msg_str = video['title'] + " has been deleted from library"
                messagebox.showinfo(title="Song Added", message=msg_str)
                self.list_titles_callback()
                os.remove(video['pathname'] + filename)
            else:
                msg_str = del_response.content
                messagebox.showinfo(title="Song Deleted", message=msg_str)


if __name__ == "__main__":
    """ Create Tk window manager and a main window. Start the main loop """
    root = tk.Tk()
    MainController(root).pack()
    tk.mainloop()