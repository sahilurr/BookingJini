import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

def merge_image(image, text, layout, colors, font_name, logo, font_size):
    # Open the main image
    img = Image.open(image).convert("RGBA")
    draw = ImageDraw.Draw(img)
    
    # Load font
    try:
        font = ImageFont.truetype(font_name, font_size)
    except:
        font = ImageFont.load_default()
    
    # Load and position the logo
    logo_img = Image.open(logo).convert("RGBA")
    logo_img = logo_img.resize((100, 100))  # Resize logo as needed
    img.paste(logo_img, (10, 10), logo_img)
    
    # Set text color and position (based on layout)
    text_position = (50, img.height - 100) if layout == "bottom" else (50, 50)
    draw.text(text_position, text, fill=colors, font=font)
    
    return img

st.title("Image Merger App")

# Uploads
image = st.file_uploader("Upload Background Image", type=["png", "jpg", "jpeg"])
logo = st.file_uploader("Upload Logo", type=["png", "jpg", "jpeg"])
text = st.text_input("Enter Text")
layout = st.selectbox("Select Layout", ["top", "bottom"])
colors = st.color_picker("Pick Text Color", "#FFFFFF")
font_name = st.text_input("Enter Font Name (e.g., Arial.ttf)")
font_size = st.slider("Select Font Size", 10, 100, 30)

if st.button("Generate Image"):
    if image and logo and text and font_name:
        result_img = merge_image(image, text, layout, colors, font_name, logo, font_size)
        buf = io.BytesIO()
        result_img.save(buf, format="PNG")
        st.image(result_img, caption="Merged Image", use_column_width=True)
        st.download_button("Download Image", buf.getvalue(), file_name="output.png", mime="image/png")
    else:
        st.error("Please upload all required inputs.")
