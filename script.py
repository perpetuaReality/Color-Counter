import os
import numpy as np
from PIL import Image

FILES_LOCATION = "" # Location of files to scan.
EXCLUSION_LIST = [] # Directory names to exclude.
VALID_FILE_EXTENSIONS = [".png", ".gif", ".jpg", ".jpeg", ".bmp"] # Extensions of files to include.
OUTPUT_FILE = "colors.csv" # Where to output final tally.

fileList = []

def scanFilesRecursive(walk_path):
    for root, subdirs, files in os.walk(walk_path):
        # Add all valid files in directory to list.
        for file in files:
            _, ext = os.path.splitext(file)
            if ext not in VALID_FILE_EXTENSIONS: continue # Exclude files with invalid extensions.
            fileList.append(os.path.join(root, file))

        # Recursively scan all subdirectories.
        if len(subdirs):
            for dir in subdirs:
                if dir in EXCLUSION_LIST: continue
                scanFilesRecursive(os.path.join(root, dir))

scanFilesRecursive(FILES_LOCATION)

colorCounts = { }

for file in set(fileList):
    print("Processing " + file)
    with Image.open(file) as im:
        # Pixels are arrays of R, G, B, A
        raw = np.asarray(im, dtype="int32") # Array of rows of pixels
        pixels = raw.reshape(-1, raw.shape[-1]) # Array of pixels
        uniques, counts = np.unique(pixels, axis=0, return_counts=True) # Unique colors and their respective counts
        # RBGA => Hex
        colors = [
            '#%02x%02x%02x%02x' % (color[0], color[1], color[2], color[3])
            for color in uniques.tolist()
        ]
        for i in range(len(colors)):
            color = colors[i]
            count = counts[i].item()
            if not color.endswith("ff"): continue # Exclude all non-opaque colors.
            if color not in colorCounts: colorCounts[color] = count
            else: colorCounts[color] = colorCounts[color] + count

orderedCounts = dict(sorted(colorCounts.items(), key=lambda item: item[1], reverse=True))

with open(OUTPUT_FILE, 'w') as f:
    print('color, count', file=f)
    for color, count in orderedCounts.items():
        print(f'{color}, {count}', file=f)