import cv2

# Load templates
sun_template = cv2.imread("src/data/templates/sun.png", 0)
moon_template = cv2.imread("src/data/templates/moon.png", 0)

# Load and preprocess grid image
img = cv2.imread("src/data/screenshots/grid1.png", 0)

rows, cols = 6, 6

# Dynamically calculate cell size
img_h, img_w = img.shape
cell_h = img_h // rows
cell_w = img_w // cols

result_grid = []

for y in range(rows):
    row = []
    for x in range(cols):
        # Crop cell
        cell = img[y*cell_h:(y+1)*cell_h, x*cell_w:(x+1)*cell_w]
        # Match Sun
        res_sun = cv2.matchTemplate(cell, sun_template, cv2.TM_CCOEFF_NORMED)
        max_val_sun = res_sun.max()
        # Match Moon
        res_moon = cv2.matchTemplate(cell, moon_template, cv2.TM_CCOEFF_NORMED)
        max_val_moon = res_moon.max()
        # Decide symbol
        if max_val_sun > 0.5 and max_val_sun > max_val_moon:
            row.append("S")
        elif max_val_moon > 0.5:
            row.append("M")
        else:
            row.append("0")
    result_grid.append("".join(row))

# Write to file
with open("src/data/inputs/input_generated.txt", "w") as f:
    for row in result_grid:
        f.write(row + "\n")