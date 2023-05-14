# Import tkinter, PIL, pathlib and multiprocessing modules
import tkinter as tk
from PIL import Image, ImageTk
from pathlib import Path
import multiprocessing as mp
import os
import hashlib

# Define global variables
images = [] # A generator expression of image file names in the folder
index = 0 # The current index of the image being displayed
trash = Path("trash") # The path of the trash folder
coords = [] # A list of coordinates of the regions drawn on the image
output = Path("output.txt") # The path of the file to save the coordinates
cavsize = 768
regions = {} # Create a dictionary variable to store the regions and their coordinates
# create a list of folder names to create
folders = ['images', 'export', 'trash']

# loop through the list of folders and create each one
for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)

def load_images(folder):
  print("load image")
  # Loop through the files in the folder
  for file in os.listdir(folder):
    # Check if the file is an image (you can change the extensions as needed)
    if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".gif"):
      # Append the image file name with full path to the images list
      images.append(os.path.join(folder, file))
  print(images)
  print("end load")

def next_image():
  # Increment the index by one and wrap around if it reaches the end of the images list
  global index
  index = (index + 1) % len(images)
  # Call show_image()
  show_image()

def prev_image():
  # Decrement the index by one and wrap around if it reaches the beginning of the images list
  global index
  index = (index - 1) % len(images)
  # Call show_image()
  show_image()

def delete_image():
  # Move the image at the current index from the folder to the trash folder
  import shutil
  shutil.move(images[index], trash)
  # Remove the image file name from the images list
  images.pop(index)
  # Call show_image()
  show_image()

def show_image():
  # Load the image at the current index from the images list
  global image
  global imagename
  image = Image.open(images[index])
  imagename = image.filename
  print(imagename)
  # Get the image size as width and height
  width, height = image.size
  print(f'SIZE: {image.size}')
  # Calculate the maximum dimension and scale factor
  max_dim = cavsize
  scale_factor = min(max_dim/width, max_dim/height)
  # Apply the scaling factor to the image size
  new_width = int(scale_factor*width)
  new_height = int(scale_factor*height)
  # Configure the canvas width and height to match the scaled image size
  canvas.config(width=new_width, height=new_height)
  # Resize the image to match the new size
  image2 = image.resize((new_width, new_height))
  # Convert the image to tkinter format
  photo = ImageTk.PhotoImage(image2)
  # Display the image on the canvas
  canvas.create_image(0, 0, anchor=tk.NW, image=photo)
  # Keep a reference to the photo object to prevent garbage collection
  canvas.image2 = photo
  # Update the label with the image file name and index
  label.config(text=f"{images[index]} '{width}x{height}' ({index + 1} of {len(images)})")

def start_draw(event):
  # Get the x and y coordinates of the mouse click on the canvas and append them to coords list
  global coords
  coords.append(event.x)
  coords.append(event.y)

def save_coords():
  # Open the output file in write mode and write the coordinates in coords list to it
  with open(output, "w") as f:
    for coord in coords:
      f.write(str(coord) + "\n")
    f.close()


def end_draw(event):
  # Get the x and y coordinates of the mouse release on the canvas and append them to coords list
  global coords
  coords.append(event.x)
  coords.append(event.y)
  # Get the image size as width and height
  width, height = image.size
  # Clamp the coordinates to the image bounds using min and max functions
  x1 = max(0, coords[-4])
  y1 = max(0, coords[-3])
  x2 = min(width, coords[-2])
  y2 = min(height, coords[-1])
  # Draw a rectangle on the canvas using only the clamped coordinates
  canvas.create_rectangle(x1, y1, x2, y2, outline="red")
  # Assign a unique name to the region using the index of the region (you can change this as needed)
  name = f"region{len(coords)//4 - 1}"
  # Store the clamped coordinates of the region as a value in the regions dictionary
  regions[name] = [x1, y1, x2, y2]

def export_regions():
 # Loop through the keys and values in the regions dictionary
 i=0
 for name, coord in regions.items():
  # Get the dimensions of the original and resized images
  original_width, original_height = image.size
  resized_width, resized_height = canvas.image2.width(), canvas.image2.height()
  # Scale the coordinates of the region using the formula
  x1 = coord[0] * original_width / resized_width
  y1 = coord[1] * original_height / resized_height
  x2 = coord[2] * original_width / resized_width
  y2 = coord[3] * original_height / resized_height
  # Crop the image using the scaled coordinates of the region
  region = image.crop((x1, y1, x2, y2))
  # Save each cropped region as a separate image file in a new folder (you can change the folder name as needed)
  filename = imagename.split("\\")[-1].split('.')[0]
  region_hash = hashlib.sha256(region.tobytes()).hexdigest()[:8]
  region_name = f"{filename}_{i+1}_{region_hash}"
  region.save(f"export/{region_name}.png")
  print(f'Exported {region_name}')
  i+=1
  


def clear_canvas():
  # Delete all the items on the canvas
  canvas.delete("all")
  # Clear the regions dictionary and the coords list
  regions.clear()
  coords.clear()
  show_image()

# Create a tkinter window
window = tk.Tk()
# Initialize the variable with the current window size
window_size = (window.winfo_width(), window.winfo_height())
# Create widgets
frame = tk.Frame(window)
canvas = tk.Canvas(window)
label = tk.Label(window)
buttons = tk.Frame(frame, bg="red")
buttons2a = tk.Frame(buttons, bg="blue")
buttons2b = tk.Frame(buttons, bg="green")
buttons3 = tk.Frame(frame)

label.pack()
canvas.pack()
canvas.configure(bg='dark gray')
buttons.pack(side="left", fill=tk.BOTH, expand=True)
buttons2a.pack(side="top", fill=tk.BOTH, expand=True)
buttons2b.pack(side="bottom", fill=tk.BOTH, expand=True)
buttons3.pack(side="left", fill=tk.BOTH, expand=True)
frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)


next_button = tk.Button(buttons2a, text="Next", command=next_image, width=10)
prev_button = tk.Button(buttons2a, text="Previous", command=prev_image, width=10)
delete_button = tk.Button(buttons3, text="Delete", command=delete_image, fg="red", width=15,height=15)
#save_button = tk.Button(buttons2, text="Save", command=save_coords, width=10)
export_button = tk.Button(buttons2b, text="Export", command=export_regions, width=10)
clear_button = tk.Button(buttons2b, text="Clear", command=clear_canvas, width=10)





# Arrange widgets using pack

canvas.pack(fill=tk.BOTH, expand=True)
next_button.pack(side="left", fill="both", expand=True)
prev_button.pack(side="left", fill="both", expand=True)
delete_button.pack(side="right", fill=tk.Y, expand=False)
#save_button.pack(side="left", fill="both", expand=True)
export_button.pack(side="left", fill="both", expand=True)
clear_button.pack(side="left", fill="both", expand=True)



# Load images from a folder (change this to your folder name)
# Bind mouse events to canvas
canvas.bind("<Button-1>", start_draw) # Bind left mouse click to start drawing a region
canvas.bind("<ButtonRelease-1>", end_draw) # Bind left mouse release to end drawing a region
load_images("images")

# Show first image
show_image()

# Start main loop
window.mainloop() # This should be the last line of the code