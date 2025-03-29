import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# --- SETTINGS / CUSTOMIZATIONS ---
POST_SIZE = (1080, 1080)  # Adjust if you want a 5000x5000 layout
BACKGROUND_COLOR = (9, 30, 66)  # Dark blue-ish
ACCENT_COLOR = (255, 190, 0)    # Gold / yellow accent
TEXT_COLOR = (255, 255, 255)    # White text

# Fonts: Update the path to fonts on your system or use a standard PIL font
TITLE_FONT_PATH = "arial.ttf"    # Replace with your local font path
BODY_FONT_PATH = "arial.ttf"     # Replace with your local font path
TITLE_FONT_SIZE = 80
BODY_FONT_SIZE = 36
BUTTON_FONT_SIZE = 40

def create_social_media_post(
    main_text: str,
    sub_text: str,
    website: str,
    button_text: str,
    account_name: str,
    accent_color=ACCENT_COLOR,
    background_color=BACKGROUND_COLOR,
    text_color=TEXT_COLOR,
    size=POST_SIZE
):
    """Create a social media post image with Pillow."""
    # 1. Create blank image
    img = Image.new("RGB", size, background_color)
    draw = ImageDraw.Draw(img)

    # 2. Load fonts
    try:
        title_font = ImageFont.truetype(TITLE_FONT_PATH, TITLE_FONT_SIZE)
        body_font = ImageFont.truetype(BODY_FONT_PATH, BODY_FONT_SIZE)
        button_font = ImageFont.truetype(BODY_FONT_PATH, BUTTON_FONT_SIZE)
    except:
        # Fallback: use a basic PIL font if the TTF isn't found
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        button_font = ImageFont.load_default()

    W, H = img.size

    # 3. Draw the circular accent shape (e.g., to show a room photo)
    #    For demonstration, we’ll just draw a circle (yellow). 
    #    You could paste an image in a circle mask here instead.
    circle_diameter = W // 3
    circle_x = W - circle_diameter - 60
    circle_y = (H // 2) - (circle_diameter // 2)
    draw.ellipse(
        [(circle_x, circle_y), (circle_x + circle_diameter, circle_y + circle_diameter)],
        fill=accent_color
    )

    # 4. Main text (e.g. "PREMIUM HOTEL")
    main_text_w, main_text_h = draw.textsize(main_text, font=title_font)
    main_text_x = 60
    main_text_y = H // 3 - main_text_h // 2
    draw.text((main_text_x, main_text_y), main_text, fill=text_color, font=title_font)

    # 5. Sub text (e.g. "Luxury Hotel")
    sub_text_w, sub_text_h = draw.textsize(sub_text, font=body_font)
    sub_text_x = 60
    sub_text_y = main_text_y + main_text_h + 20
    draw.text((sub_text_x, sub_text_y), sub_text, fill=text_color, font=body_font)

    # 6. Website text
    website_w, website_h = draw.textsize(website, font=body_font)
    website_x = 60
    website_y = sub_text_y + sub_text_h + 20
    draw.text((website_x, website_y), website, fill=text_color, font=body_font)

    # 7. Account name
    account_w, account_h = draw.textsize(account_name, font=body_font)
    account_x = 60
    account_y = website_y + website_h + 20
    draw.text((account_x, account_y), account_name, fill=text_color, font=body_font)

    # 8. "Book Now" button (rectangle)
    button_padding_x = 20
    button_padding_y = 10
    button_w, button_h = draw.textsize(button_text, font=button_font)
    # Button background
    btn_x1 = 60
    btn_y1 = account_y + account_h + 40
    btn_x2 = btn_x1 + button_w + 2 * button_padding_x
    btn_y2 = btn_y1 + button_h + 2 * button_padding_y
    draw.rectangle(
        [(btn_x1, btn_y1), (btn_x2, btn_y2)],
        fill=accent_color
    )
    # Button text
    text_x = btn_x1 + button_padding_x
    text_y = btn_y1 + button_padding_y
    draw.text((text_x, text_y), button_text, fill=background_color, font=button_font)

    return img

def main():
    st.title("Social Media Post Layout Demo")
    st.write("Use the sidebar to customize your post content, then download or preview the result.")

    # -- Sidebar for text inputs --
    main_text = st.sidebar.text_input("Main Text (Title)", "PREMIUM HOTEL")
    sub_text = st.sidebar.text_input("Subtitle", "Luxury Hotel")
    website = st.sidebar.text_input("Website", "www.websitename.com")
    account_name = st.sidebar.text_input("Account Name", "@account")
    button_text = st.sidebar.text_input("Button Text", "BOOK NOW")

    # Generate the image
    post_img = create_social_media_post(
        main_text=main_text,
        sub_text=sub_text,
        website=website,
        account_name=account_name,
        button_text=button_text
    )

    # Display in Streamlit
    st.image(post_img, caption="Generated Social Media Post")

    # Download button
    img_bytes = post_img.convert("RGB").tobytes()
    st.download_button(
        label="Download Post (PNG)",
        data=post_img.tobytes("raw", "RGB"),
        file_name="social_media_post.png",
        mime="image/png"
    )

if __name__ == "__main__":
    main()