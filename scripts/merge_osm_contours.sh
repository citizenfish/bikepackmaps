#!/bin/bash

# Define the directory containing the .pbf files
input_directory="osm_contours"

# Directory for sorted files
sorted_directory="sorted_files"
mkdir -p "$sorted_directory"

# Sort each .pbf file in the input directory
for input_file in "$input_directory"/*.pbf; do
  filename=$(basename "$input_file")
  sorted_file="$sorted_directory/sorted_$filename"
  echo "Sorting file $filename..."
  osmium sort "$input_file" --overwrite -o "$sorted_file"
done

echo "All files sorted."

# Merge sorted files
output_file="merged_contours.osm.pbf"
sorted_files=$(ls "$sorted_directory"/*.osm.pbf)
osmium merge $sorted_files --overwrite -o "$output_file"

echo "Merge completed. Output file: $output_file"

