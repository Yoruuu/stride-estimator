import customtkinter
from PIL import ImageTk, Image
from tkVideoPlayer import TkinterVideo
import datetime
from stride_estimator import stride_estimator

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

root = customtkinter.CTk()
root.title("fyp")
root.geometry("1920x1080")

# side frame
side_frame = customtkinter.CTkFrame(master=root)
side_frame.pack(pady=20, padx=20, fill="both", side=customtkinter.LEFT)

# video frame
video_frame = customtkinter.CTkFrame(master=root)
video_frame.pack(pady=20, padx=20, fill="both", expand=True, side=customtkinter.LEFT)

video = TkinterVideo(master=video_frame, scaled=True)
playing = False

video_label = customtkinter.CTkLabel(master=video_frame, text="Video", anchor="w")
video_label.pack(pady=12, padx=10)

def browsefile():
    video.stop()
    filename = customtkinter.filedialog.askopenfilename(initialdir="/",
                                                        title="Select a File",
                                                        filetypes=(("Video files",
                                                                    "*.mov *.mp4"),
                                                                   ("all files",
                                                                    "*.*")))


    if filename == "":
        video_label.configure(text="No Video Detected")
    else:
        loading_label = customtkinter.CTkLabel(master=root, text="  Processing video frames...")
        loading_label.place(relx=0.0, rely=1.0, anchor="sw")

        if len(filename) > 80:
            filename = filename[:80] + '\n' + filename[80:]
        video_label.configure(text="File Opened: " + filename)

        # get the shoe size
        shoe_size = popup_shoesize("Please enter your shoe size in centimetres")

        # loop if invalid input
        # empty input, not numbers, negative numbers or 0
        while (shoe_size == "" or shoe_size == None or
               shoe_size.isdigit() is False or
               (shoe_size.isdigit() is True and int(shoe_size) <= 0)):
            shoe_size = popup_shoesize("Please enter your shoe size in centimetres\n\n(Incorrect input: Input should be a positive integer)")


        # preprocess the vid
        # print(filename, shoe_size)
        # time.sleep(10)
        se = stride_estimator(filename, shoe_size)
        
        loading_label.destroy()

        for i in range(len(se.step_array)):
            text = customtkinter.CTkLabel(master = step_scrollable_frame, text="step " + str(i+1) + ": " + str(se.step_array[i]) + "cm")
            text.pack(pady=10, padx=10)
        for i in range(len(se.stride_array)):
            text = customtkinter.CTkLabel(master = stride_scrollable_frame, text="stride " + str(i+1) + ": " + str(se.stride_array[i]) + "cm")
            text.pack(pady=10, padx=10)

        # play the result
        playvideo()


browsefile_button = customtkinter.CTkButton(video_frame, text="Browse Files", command=browsefile)
browsefile_button.pack(pady=12, padx=10)
video.pack(expand=True, fill="both")
video.config(background="#323536")


def update_duration(event):
    """ updates the duration after finding the duration """
    duration = video.video_info()["duration"]
    # end_time["text"] = str(datetime.timedelta(seconds=duration))
    progress_slider["to"] = duration


def update_scale(event):
    """ updates the scale value """
    progress_value.set(video.current_duration())


# def load_video():
#     """ loads the video """
#     file_path = filedialog.askopenfilename()

#     if file_path:
#         video.load(file_path)

#         progress_slider.config(to=0, from_=0)
#         play_pause_btn["text"] = "Play"
#         progress_value.set(0)


def seek(value):
    """ used to seek a specific timeframe """
    video.seek(int(value))


def skip(value: int):
    """ skip seconds """
    video.seek(int(progress_slider.get())+value)
    print(progress_value.get())
    progress_value.set(progress_slider.get() + value)
    print(progress_value.get())



def video_ended(event):
    """ handle video ended """
    progress_slider.set(progress_slider["to"])
    progress_slider.set(0)


skip_plus_5sec = customtkinter.CTkButton(video_frame, text="-5 sec", command=lambda: skip(-5))
skip_plus_5sec.pack(side="left")

start_time = customtkinter.CTkLabel(video_frame, text=str(datetime.timedelta(seconds=0)))
start_time.pack(side="left")

progress_value = customtkinter.IntVar(video_frame)

progress_slider = customtkinter.CTkSlider(video_frame, variable=progress_value, orientation="horizontal",from_=0, to=50, command=seek)
        

progress_slider.bind("<ButtonRelease-1>", seek)
progress_slider.pack(side="left", fill="x", expand=True)


video.bind("<<Duration>>", update_duration)
video.bind("<<SecondChanged>>", update_scale)
video.bind("<<Ended>>", video_ended )

skip_plus_5sec = customtkinter.CTkButton(video_frame, text="+5 sec", command=lambda: skip(5))
skip_plus_5sec.pack(side="left")

def popup_shoesize(txt):

    shoesize_inputbox = customtkinter.CTkInputDialog(title="Shoe Size",
                                                     text=txt)
    res = shoesize_inputbox.get_input()
    return res


def playvideo():
    video.load("res.mp4")
    progress_slider.configure(to=50, from_=0)
    progress_value.set(0)
    video.play()
    # playing = True


# data frame
step_scrollable_frame = customtkinter.CTkScrollableFrame(master=root, label_text="Step Data")
step_scrollable_frame.pack(pady=20, padx=20, fill="both", side=customtkinter.TOP)

stride_scrollable_frame = customtkinter.CTkScrollableFrame(master=root, label_text="Stride Data")
stride_scrollable_frame.pack(pady=12, padx=10, side=customtkinter.BOTTOM)



# buttons
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

# mainloop
root.mainloop()