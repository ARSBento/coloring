import requests
from bs4 import BeautifulSoup
import os

from io import BytesIO
import numpy as np
import skimage
import cv2
import vertexai
from vertexai.language_models import TextGenerationModel

from PIL import Image, ImageOps
from PIL.Image import Image as PilImage
from PIL import ImageFilter 
default_excerpt="Explore our exclusive Abra Pokémon coloring page, perfect for fans of all ages. Unleash your creativity as you bring this mysterious Pokémon to life with your favorite hues. Download and print for hours of coloring fun! Catch 'em all with our free Abra coloring sheet. #AbraColoringPage #PokémonColoring #CreativeFun"
def create_excerpt(pokemon):
    vertexai.init(project="optimum-entity-318521", location="us-central1")
    parameters = {
        "max_output_tokens": 160,
        "temperature": 0.2,
        "top_p": 0.8,
        "top_k": 40
    }
    model = TextGenerationModel.from_pretrained("text-bison@001")
    response = model.predict(
        "write me an excerpt describing "+pokemon+" the pokemon coloring page.",
        **parameters
    )
    content=response.text+"\nExplore our exclusive "+pokemon+" Pokémon coloring page, perfect for fans of all ages. Unleash your creativity as you bring this mysterious Pokémon to life with your favorite hues. Download and print for hours of coloring fun! Catch 'em all with our free "+pokemon+ " coloring sheet."
    filename='excerpts/'+pokemon+'_excerpt.txt'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write(content)


def generate_coloring_page(input: PilImage) -> PilImage:
    trueInput=input.copy()
    ratio=1
    if(input.size[0]<1000):
        input=input.resize((input.size[0]*3,input.size[1]*3))
        ratio=3
    new_image = Image.new("RGBA", input.size, "WHITE") # Create a white rgba background
    try:
        new_image.paste(input, (0, 0), input)
        input=new_image
    except:
        print('error')
    else:
        input=input.convert('RGBA')

        
    # Convert to grayscale if needed
    if input.mode != "L":
        input = input.convert("L")

    # Transpose if taken in non-native orientation (rotated digital camera)
    NATIVE_ORIENTATION = 1
    if input.getexif().get(0x0112, NATIVE_ORIENTATION) != NATIVE_ORIENTATION:
        input = ImageOps.exif_transpose(input)

    
      
    np_image = np.asarray(input)

    

    # Remove some noise to keep the most visible edges
    np_image = skimage.restoration.denoise_tv_chambolle(np_image, weight=0.15)

    # Detect the edges
    #np_image = skimage.filters.sobel(np_image)
    np_image = skimage.filters.butterworth(np_image)
    np_image = skimage.feature.canny(np_image)
    
    # # Convert to 8 bpp
    np_image = skimage.util.img_as_ubyte(np_image)

    # define a (3, 3) structuring element
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    # # apply the dilation operation to the edged image
    dilate = cv2.dilate(np_image, kernel, iterations=3)

    

    # Invert to get dark edges on a light background
    np_image = 255 - dilate
    
    
    # Improve the contrast
    #np_image = skimage.exposure.rescale_intensity(np_image)

    output=Image.fromarray(np_image)
    output=output.resize((output.size[0]//ratio, output.size[1]//ratio))

    new_image=output
    new_image2 = Image.new("RGB", (trueInput.size[0]*2,trueInput.size[1]), "WHITE") # Create a white rgba background
    new_image2.paste(trueInput, (0, 0), trueInput)
    new_image2.paste(new_image, (trueInput.size[0], 0))
    return [new_image,new_image2]



# URL of the Bulbapedia page containing the list of Pokémon images
url = 'https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_name#B'

# Send an HTTP GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content of the page using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table containing the Pokémon images
    image_tables = soup.find_all('table', class_='roundy')

    # Create a directory to save the images if it doesn't exist
    if not os.path.exists('pokemon_images_colouring'):
        os.makedirs('pokemon_images_colouring')
    # Create a directory to save the images if it doesn't exist
    if not os.path.exists('pokemon_images_colouring_featured'):
        os.makedirs('pokemon_images_colouring_featured')
    for table in image_tables:
        # Find and download the Pokémon images
        for row in table.find_all('tr')[1:]:  # Skip the header row
            columns = row.find_all('td')
            if len(columns) >= 4:
                name = columns[2].text.strip()
                try:
                    image_url = columns[1].find('img')['src'].replace('/thumb','')
                except:
                    continue
                # Find the last occurrence of "/"
                last_slash_index = image_url.rfind('/')

                # Slice the string to remove everything after the last "/"
                image_url = 'https:'+image_url[:last_slash_index]

                image_filename = f'pokemon_images_colouring/{name}.jpg'
                featured_image_filename = f'pokemon_images_colouring_featured/{name}.jpg'
                # Download the image
                response = requests.get(image_url)
                if response.status_code == 200:
                    input_image = Image.open(BytesIO(response.content))
                    try: 
                        # create_excerpt(name)
                        output_images = generate_coloring_page(input_image)
                        output_images[0].save(image_filename)
                        output_images[1].save(featured_image_filename)
                        print(f'Downloaded: {name}.jpg')
                    except Exception as e:
                        print(e)
                        print(f'Failed to convert: {name}.png')
                else:
                    print(f'Failed to download: {name}.jpg')

    print('All Pokémon images downloaded successfully.')
else:
    print('Failed to retrieve the Bulbapedia page.')

