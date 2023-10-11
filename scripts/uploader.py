import os
import requests
import json
from requests.auth import HTTPBasicAuth

# Set your WordPress site URL and access token
wordpress_url = "https://print.ideashortcut.com/wp-json/wp/v2/custom-gallery"
username = 'arsb888'
password = 'AHS4 zsqC hXU9 FMwU B0gm pSu4'

# Path to the folder containing images
image_folder = '/Users/arsbento/code/pokemon_images_colouring'  # Replace with the actual path to your image folder

# Step 1: Iterate through the images in the folder
for filename in os.listdir(image_folder):
    if filename.endswith('.jpg'):  # You can change the file extension if needed
        image_path = os.path.join(image_folder, filename)
        featured_image_path = os.path.join(image_folder+'_featured', filename)
        try:
            image = open(image_path, 'rb')
            featured_image = open(featured_image_path, 'rb')
        except:
            continue

        pokemon=os.path.splitext(filename)[0]
        with open('/Users/arsbento/code/excerpts/'+pokemon+'_excerpt.txt', "r") as f:
            content=f.read()

        excerpt="Explore our exclusive "+pokemon+" Pokémon coloring page, perfect for fans of all ages. Unleash your creativity as you bring this mysterious Pokémon to life with your favorite hues. Download and print for hours of coloring fun! Catch 'em all with our free "+pokemon+ " coloring sheet."

        title=pokemon+" Coloring Page"
        keyword=title
        # Step 3: Create a Custom Post with Featured Media
        post_data = {
            "title": title,  # Use the filename as the title (without extension)
            "content": content,
            "status": "publish",
            "categories": "1",  # Replace with the desired category ID
            "excerpt": excerpt,
            "rank_math_focus_keyword": keyword,
            "licensing":"This image is copyrighted and possibly a registered trademark as well. It was taken from the Pokemon.co.jp Pokédex. The contributor claims this to be fair use."
        }
        post_response = requests.post(wordpress_url, 
                                      auth=HTTPBasicAuth(username, password),
                                      data=post_data,
                                      files=[('custom_image_upload', image),('featured_media', featured_image)],
                                    verify=False)

        if post_response.status_code == 201:
            print(f"Post created successfully for {filename}!")
        else:
            print(f"Error creating post for {filename}. Status code: {post_response.status_code}.  Response: {post_response.content}")
