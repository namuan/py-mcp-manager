#!/bin/bash

# Prerequisites:
# brew install imagemagick

# Check if a source PNG file is provided as an argument
if [ -z "$1" ]; then
  echo "Error: Please provide a source PNG file as an argument."
  echo "Usage: $0 <source_png>"
  exit 1
fi

# Check if the source file exists
if [ ! -f "$1" ]; then
  echo "Error: Source file '$1' does not exist."
  exit 1
fi

# Extract the base name of the input file (without extension)
BASENAME=$(basename "$1" .png)

# Generate individual PNG files (original commands)
magick "$1" -background none -gravity center -resize 16x16 "${BASENAME}-icon16.png"
magick "$1" -background none -gravity center -resize 32x32 "${BASENAME}-icon32.png"
magick "$1" -background none -gravity center -resize 48x48 "${BASENAME}-icon48.png"
magick "$1" -background none -gravity center -resize 128x128 "${BASENAME}-icon128.png"
magick "$1" -background none -gravity center -resize 256x256 "${BASENAME}-icon256.png"
magick "$1" -background none -gravity center -resize 512x512 "${BASENAME}-icon512.png"
magick "$1" -background none -gravity center -resize 1024x1024 "${BASENAME}-icon1024.png"

# Create a temporary iconset directory for ICNS generation
mkdir "${BASENAME}.iconset"

# Generate different sizes for ICNS and ICO
magick "$1" -background none -gravity center -resize 16x16 "${BASENAME}.iconset/icon_16x16.png"
magick "$1" -background none -gravity center -resize 32x32 "${BASENAME}.iconset/icon_32x32.png"
magick "$1" -background none -gravity center -resize 48x48 "${BASENAME}.iconset/icon_48x48.png"
magick "$1" -background none -gravity center -resize 128x128 "${BASENAME}.iconset/icon_128x128.png"
magick "$1" -background none -gravity center -resize 256x256 "${BASENAME}.iconset/icon_256x256.png"
magick "$1" -background none -gravity center -resize 512x512 "${BASENAME}.iconset/icon_512x512.png"
magick "$1" -background none -gravity center -resize 1024x1024 "${BASENAME}.iconset/icon_1024x1024.png"

# Convert the iconset to ICNS
iconutil -c icns "${BASENAME}.iconset" -o "${BASENAME}.icns"

# Generate ICO file by combining multiple sizes
magick "${BASENAME}.iconset/icon_16x16.png" \
       "${BASENAME}.iconset/icon_32x32.png" \
       "${BASENAME}.iconset/icon_48x48.png" \
       "${BASENAME}.iconset/icon_128x128.png" \
       "${BASENAME}.iconset/icon_256x256.png" \
       "${BASENAME}.iconset/icon_512x512.png" \
       "${BASENAME}.iconset/icon_1024x1024.png" \
       -background none "${BASENAME}.ico"

# Clean up the temporary iconset directory
rm -rf "${BASENAME}.iconset"
