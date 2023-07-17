import tkinter as tk
from PIL import ImageGrab, ImageTk, Image
import pytesseract

from dotenv import load_dotenv
import os
import openai

load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]

# model_name = "google/flan-t5-large"
# tokenizer = T5Tokenizer.from_pretrained(model_name)
# model = T5ForConditionalGeneration.from_pretrained(model_name)

pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

# create the root window
root = tk.Tk()
root.attributes('-alpha', 1) #set the transparency of the window

# get the screen size
screen_width = 1470
screen_height = 956
print(screen_width, screen_height)

screenshot = ImageGrab.grab() #take a screenshot
screenshot_resized = screenshot.resize((screen_width, screen_height), Image.LANCZOS) #resize the screenshot
screenshot_resized = screenshot_resized.crop((0, 60, screen_width, screen_height)) #crop the screenshot

# screenshot_resized.save("screenshot.png") #save the screenshot
tk_screenshot = ImageTk.PhotoImage(screenshot_resized) #convert the screenshot to a tkinter image
print (screenshot_resized.size)

canvas = tk.Canvas(root, width=screenshot.width, height=screenshot.height)
canvas.pack()
canvas.create_image(0, 0, image=tk_screenshot, anchor=tk.NW)


def start_rect(event):
    global start_x, start_y, rectangle
    start_x = event.x
    start_y = event.y
    rectangle = None

def draw_rect(event):
    global start_x, start_y, rectangle
    canvas.delete(rectangle)
    rectangle = canvas.create_rectangle(start_x, start_y, event.x, event.y)

def capture(event):
    global start_x, start_y, screenshot, screenshot_resized, text

    top_left_x = min(start_x, event.x)
    top_left_y = min(start_y, event.y)
    bottom_right_x = max(start_x, event.x)
    bottom_right_y = max(start_y, event.y)

    box = (top_left_x, top_left_y, bottom_right_x, bottom_right_y)
    sub_img = screenshot_resized.crop(box)
    text = pytesseract.image_to_string(sub_img)
    
    print(text)

    del sub_img

    screenshot = ImageGrab.grab() #take a screenshot
    screenshot_resized = screenshot.resize((screen_width, screen_height)) #resize the screenshot

    tk_screenshot = ImageTk.PhotoImage(screenshot_resized) #convert the screenshot to a tkinter image
    canvas.create_image(0, 0, image=tk_screenshot, anchor=tk.NW) #add the screenshot to the canvas

    print("What is your question about this highlighted text?")
    question = input()

    print(ask_question(question, text))
    print("I hope that was helpful!")

def ask_question(question, context):
    
    # this is the format OpenAI's API requires
    input_text = "context: %s question: %s" % (context, question)
    model = "gpt-3.5-turbo"

    response = openai.ChatCompletion.create(
        model=model, 
        messages=[
            {"role": "system", "content": "You are a friendly and helpful teaching assistant. You receive text context from a highlighted section of a user's screen, and you explain clearly what they ask about"},
            {"role": "user", "content": input_text},
        ],
        top_p=0.95,
        max_tokens=200
    )

    output_text = response.choices[0].message.content.strip()

    return output_text

canvas.bind('<Button-1>', start_rect)
canvas.bind('<B1-Motion>', draw_rect)
canvas.bind("<ButtonRelease-1>", capture)

root.mainloop()