import customtkinter
from tkVideoPlayer import TkinterVideo
from stride_estimator import stride_estimator

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

root = customtkinter.CTk()
root.title("fyp")
root.geometry("1920x1080")
root.grid_columnconfigure(0, weight=3)
root.grid_columnconfigure(1, weight=1)

# video frame
video_frame = customtkinter.CTkFrame(master=root)
video_frame.pack(pady=20, padx=80, fill="both", expand=True, side=customtkinter.LEFT)

video = TkinterVideo(master=video_frame, scaled=True)
playing = False

video_label = customtkinter.CTkLabel(master=video_frame, text="Video", anchor="w")
video_label.pack(pady=12, padx=10)


def browsefile():
    video.stop()
    filename = customtkinter.filedialog.askopenfilename(initialdir="/",
                                                        title="Select a File",
                                                        filetypes=(("Text files",
                                                                    "*.mov *.mp4"),
                                                                   ("all files",
                                                                    "*.*")))

    # Change label contents
    video_label.configure(text="File Opened: " + filename)

    print(filename, type(filename))

    if filename == "":
        print("None detected")
    else:
        print("something detected")
        # video = TkinterVideo(master=video_frame, scaled=True)
        # if playing:
        #     video.bind('<<Loaded>>', stopvideo)
        #     video.load("vid1.mp4")
        # get the shoe size
        shoe_size = popup_shoesize()

        # loop if invalid input
        # empty input, not numbers, negative numbers or 0
        while (shoe_size == "" or shoe_size == None or
               shoe_size.isdigit() is False or
               (shoe_size.isdigit() is True and int(shoe_size) <= 0)):
            shoe_size = popup_shoesize()

        ##call loading screen here

        # preprocess the vid
        print(filename, shoe_size)
        stride_estimator(filename, shoe_size)

        ##remove loading screen here

        # play the result
        playvideo()


browsefile_button = customtkinter.CTkButton(video_frame, text="Browse Files", command=browsefile)
browsefile_button.pack(pady=12, padx=10)


def popup_shoesize():

    shoesize_inputbox = customtkinter.CTkInputDialog(title="Shoe Size",
                                                     text="Please enter your shoe size in centimetres")
    # shoesize_inputbox.place(relx=0.5, rely=0.5, anchor='n')
    # print("Shoe Size:", shoesize_inputbox.get_input())
    res = shoesize_inputbox.get_input()
    return res


# occupied = False
def playvideo():
    # if playing:
    #     video.stop()
    # print("heyyy")

    # video = TkinterVideo(master=video_frame, scaled=True)
    video.load("res.mp4")
    video.pack(expand=True, fill="both")
    video.play()
    # video.bind('<<Ended>>', loopVideo)
    # video.config
    playing = True


# side frame
side_frame = customtkinter.CTkFrame(master=root)
side_frame.pack(pady=20, padx=20, fill="both", expand=True)

def pause():
    video.pause()


def play():
    video.play()


def replay():
    video.stop()
    video.after(100, video.play)


play_button = customtkinter.CTkButton(master=side_frame, text="Play", width=80, command=play)
play_button.pack(pady=12, padx=10)
pause_button = customtkinter.CTkButton(master=side_frame, text="Pause", width=80, command=pause)
pause_button.pack(pady=12, padx=10)
replay_button = customtkinter.CTkButton(master=side_frame, text="Replay", width=80, command=replay)
replay_button.pack(pady=12, padx=10)


def change_appearance_mode_event(new_appearance_mode: str):
    customtkinter.set_appearance_mode(new_appearance_mode)


appearance_mode_optionemenu = customtkinter.CTkOptionMenu(side_frame, values=["Dark", "Light", "System"],
                                                          command=change_appearance_mode_event)
appearance_mode_optionemenu.pack(pady=12, padx=10, side=customtkinter.BOTTOM)
appearance_mode_label = customtkinter.CTkLabel(side_frame, text="Appearance Mode:")
appearance_mode_label.pack(pady=5, padx=10, side=customtkinter.BOTTOM)

root.mainloop()