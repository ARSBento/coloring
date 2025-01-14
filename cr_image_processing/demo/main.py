"""
Copyright 2022 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import io
import os

import flask
import numpy as np
import skimage
import cv2

from PIL import Image, ImageOps
from PIL.Image import Image as PilImage
from PIL import ImageFilter 

app = flask.Flask(__name__, static_url_path="")


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.post("/api/coloring-page")
def coloring_page():
    file = flask.request.files.get("input-image")
    if file is None:
        return "Missing input-image parameter", 400

    input_image = Image.open(file.stream)
    output_image = generate_coloring_page(input_image)

    image_io = io.BytesIO()
    output_format = "png"
    output_image.save(image_io, format=output_format)
    image_io.seek(0)

    return flask.send_file(image_io, mimetype=f"image/{output_format}")


def generate_coloring_page(input: PilImage) -> PilImage:
    
    input=input.resize((input.size[0]*4,input.size[1]*4))
    new_image = Image.new("RGBA", input.size, "WHITE") # Create a white rgba background
    try:
        new_image.paste(input, (0, 0), input)
        new_image.convert('RGB').save('test.jpg', "JPEG")
        input=new_image
    except:
        print('error')
        
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
    dilate = cv2.dilate(np_image, kernel, iterations=4)

    

    # Invert to get dark edges on a light background
    np_image = 255 - dilate
    
    
    # Improve the contrast
    #np_image = skimage.exposure.rescale_intensity(np_image)

    output=Image.fromarray(np_image)
    output.resize((output.size[0]//4, output.size[1]//4))

    return output


if __name__ == "__main__":
    # Dev only: run "python main.py" (3.9+) and open http://localhost:8080
    os.environ["FLASK_ENV"] = "development"
    app.run(host="localhost", port=8080, debug=True)
else:
    # Prod only: cache static resources
    app.send_file_max_age_default = 3600  # 1 hour
