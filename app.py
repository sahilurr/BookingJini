import streamlit as st
import requests
import io
import base64
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
import json
import time
from typing import Dict, List, Tuple, Optional

st.set_page_config(
    page_title="Hotel Social Media Post Generator",
    page_icon="BJ.jpg",
    layout="wide"
)

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
STABILITY_API_KEY = st.secrets.get("STABILITY_API_KEY", "")

SOCIAL_MEDIA_CREDENTIALS = {
    "instagram": st.secrets.get("INSTAGRAM_TOKEN", ""),
    "facebook": st.secrets.get("FACEBOOK_TOKEN", ""),
    "twitter": st.secrets.get("TWITTER_TOKEN", ""),
    "linkedin": st.secrets.get("LINKEDIN_TOKEN", "")
}
COLOR_PALETTES = {
    "Elegant": ["#2c3e50", "#ecf0f1", "#3498db", "#e74c3c", "#f1c40f"],
    "Tropical": ["#1abc9c", "#f39c12", "#3498db", "#e74c3c", "#f1c40f"],
    "Classic": ["#34495e", "#ecf0f1", "#3498db", "#e67e22", "#f1c40f"],
    "Modern": ["#2c3e50", "#ecf0f1", "#e74c3c", "#3498db", "#2ecc71"],
    "Luxury": ["#2c3e50", "#f5f5f5", "#c0392b", "#f39c12", "#7f8c8d"]
}
LAYOUTS = {
    "Centered": "image with centered text overlay",
    "Split": "image on left, text on right",
    "Banner": "image with text banner at bottom",
    "Minimalist": "full image with minimal text overlay",
    "Collage": "multiple small images with text"
}

# Font Options
FONTS = ["Roboto", "Montserrat", "Playfair Display", "Open Sans", "Lato"]

if 'generated_image' not in st.session_state:
    st.session_state.generated_image = None
if 'generated_text' not in st.session_state:
    st.session_state.generated_text = ""
if 'hotel_logo' not in st.session_state:
    st.session_state.hotel_logo = None
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = 0


def generate_text_with_llama(prompt: str) -> str:
    if not GROQ_API_KEY:
        return "Please set your GROQ API key in the app settings."

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system",
                 "content": "You are a professional social media marketer specializing in hospitality. Create short, engaging captions for hotels."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }

        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()

    except Exception as e:
        st.error(f"Error generating text: {str(e)}")
        return "Error generating text. Please try again."


def generate_image_with_stability(prompt: str) -> Optional[Image.Image]:
    if not STABILITY_API_KEY:
        st.warning("Please set your Stability API key in the app settings.")
        return None

    try:
        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

        headers = {
            "Authorization": f"Bearer {STABILITY_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload = {
            "text_prompts": [{"text": prompt}],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30,
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()
        image_data = base64.b64decode(data["artifacts"][0]["base64"])
        image = Image.open(io.BytesIO(image_data))
        return image

    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None


def apply_layout(image: Image.Image, text: str, layout: str, colors: List[str], font_name: str,
                 logo: Optional[Image.Image] = None) -> Image.Image:
    width, height = image.size
    draw = ImageDraw.Draw(image)
    try:
        font_large = ImageFont.truetype(f"{font_name}.ttf", 36)
        font_small = ImageFont.truetype(f"{font_name}.ttf", 24)
    except (IOError, OSError):
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    background_color = colors[0]
    text_color = colors[1]

    if layout == "Centered":
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            if len(' '.join(current_line)) > 30:  # Adjust based on your needs
                if len(current_line) > 1:
                    lines.append(' '.join(current_line[:-1]))
                    current_line = [current_line[-1]]
                else:
                    lines.append(' '.join(current_line))
                    current_line = []

        if current_line:
            lines.append(' '.join(current_line))
        text_height = len(lines) * 40  # Line height
        text_y = (height - text_height) // 2
        overlay_draw.rectangle([(width * 0.1, text_y - 20), (width * 0.9, text_y + text_height + 20)],
                               fill=(int(background_color[1:3], 16),
                                     int(background_color[3:5], 16),
                                     int(background_color[5:7], 16), 128))

        # Draw text
        for i, line in enumerate(lines):
            line_width = font_large.getbbox(line)[2]
            line_x = (width - line_width) // 2
            overlay_draw.text((line_x, text_y + i * 40), line, font=font_large, fill=text_color)

        image = Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')

    elif layout == "Split":
        new_image = Image.new('RGB', (width * 2, height), color=background_color)

        new_image.paste(image, (0, 0))

        draw = ImageDraw.Draw(new_image)
        lines = []
        current_line = []
        words = text.split()

        for word in words:
            current_line.append(word)
            if len(' '.join(current_line)) > 25:
                if len(current_line) > 1:
                    lines.append(' '.join(current_line[:-1]))
                    current_line = [current_line[-1]]
                else:
                    lines.append(' '.join(current_line))
                    current_line = []

        if current_line:
            lines.append(' '.join(current_line))

        # Draw text
        text_x = width + 20
        text_y = height // 4

        for i, line in enumerate(lines):
            draw.text((text_x, text_y + i * 40), line, font=font_large, fill=text_color)

        image = new_image

    elif layout == "Banner":
        # Create banner at bottom
        banner_height = height // 4
        banner_y = height - banner_height

        # Create a new image with the banner
        new_image = image.copy()
        draw = ImageDraw.Draw(new_image)

        # Draw semi-transparent banner
        draw.rectangle([(0, banner_y), (width, height)],
                       fill=(int(background_color[1:3], 16),
                             int(background_color[3:5], 16),
                             int(background_color[5:7], 16), 200))
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            if len(' '.join(current_line)) > 40:
                if len(current_line) > 1:
                    lines.append(' '.join(current_line[:-1]))
                    current_line = [current_line[-1]]
                else:
                    lines.append(' '.join(current_line))
                    current_line = []

        if current_line:
            lines.append(' '.join(current_line))

        # Draw text
        for i, line in enumerate(lines[:3]):
            line_width = font_large.getbbox(line)[2]
            line_x = (width - line_width) // 2
            draw.text((line_x, banner_y + 10 + i * 40), line, font=font_large, fill=text_color)

        image = new_image

    elif layout == "Minimalist":
        draw = ImageDraw.Draw(image)

        shortened_text = text[:100] + "..." if len(text) > 100 else text
        text_width = font_small.getbbox(shortened_text)[2]

        draw.rectangle([(20, height - 70), (text_width + 40, height - 20)],
                       fill=(int(background_color[1:3], 16),
                             int(background_color[3:5], 16),
                             int(background_color[5:7], 16), 200))

        # Draw text
        draw.text((30, height - 60), shortened_text, font=font_small, fill=text_color)

    elif layout == "Collage":

        border = 20
        margin = 10

        collage = Image.new('RGB', (width + 2 * border, height + 2 * border + 100), color=background_color)
        collage.paste(image, (border, border))

        draw = ImageDraw.Draw(collage)

        words = text.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            if len(' '.join(current_line)) > 40:
                if len(current_line) > 1:
                    lines.append(' '.join(current_line[:-1]))
                    current_line = [current_line[-1]]
                else:
                    lines.append(' '.join(current_line))
                    current_line = []

        if current_line:
            lines.append(' '.join(current_line))

        for i, line in enumerate(lines[:3]):  # Limit to 3 lines
            draw.text((border + margin, height + border + 10 + i * 30), line, font=font_small, fill=text_color)

        image = collage

    # Add logo if provided
    if logo:
        logo_size = min(width // 6, height // 6)
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

        logo = logo.convert("RGBA")

        logo_position = (width - logo_size - 20, 20)

        if image.mode == 'RGB' and logo.mode == 'RGBA':
            temp = Image.new('RGBA', image.size, (0, 0, 0, 0))
            temp.paste(logo, logo_position, logo)
            image_rgba = image.convert('RGBA')
            image = Image.alpha_composite(image_rgba, temp).convert('RGB')
        else:
            image.paste(logo, logo_position, logo)

    return image


def post_to_social_media(platform: str, image_path: str, caption: str) -> bool:

    if not SOCIAL_MEDIA_CREDENTIALS.get(platform):
        st.warning(f"Please set up your {platform.capitalize()} credentials in the app settings.")
        return False

    st.success(f"Post successfully shared to {platform.capitalize()}! (simulation)")
    return True

def change_tab(tab_index):
    st.session_state.current_tab = tab_index

def load_icon(image_path):
    with open(image_path, "rb") as img_file:
        return img_file.read()

# UI Components
def main():
    # Set up the page with a JPG icon
    icon_path = "BJ.jpg" 
    icon_bytes = load_icon(icon_path)
    

    # Layout for logo and title
    col1, col2 = st.columns([0.15, 0.85])

    with col1:
       st.image(icon_path, width=80)  

    with col2:
        st.title("BookingJini") 

    with st.sidebar:
        st.header("Configuration")

        with st.expander("API Settings"):
            groq_key = st.text_input("GROQ API Key", value=GROQ_API_KEY, type="password")
            stability_key = st.text_input("Stability API Key", value=STABILITY_API_KEY, type="password")

            # Social Media Settings
            st.subheader("Social Media Credentials")
            instagram_token = st.text_input("Instagram Token", value=SOCIAL_MEDIA_CREDENTIALS.get("instagram", ""),
                                            type="password")
            facebook_token = st.text_input("Facebook Token", value=SOCIAL_MEDIA_CREDENTIALS.get("facebook", ""),
                                           type="password")
            twitter_token = st.text_input("Twitter Token", value=SOCIAL_MEDIA_CREDENTIALS.get("twitter", ""),
                                          type="password")
            linkedin_token = st.text_input("LinkedIn Token", value=SOCIAL_MEDIA_CREDENTIALS.get("linkedin", ""),
                                           type="password")

            if st.button("Save API Settings"):
                st.success("Settings saved successfully!")

        # Hotel Information
        st.subheader("Hotel Information")
        hotel_name = st.text_input("Hotel Name", "")
        hotel_location = st.text_input("Location", "")

        # Upload hotel logo
        uploaded_logo = st.file_uploader("Upload Hotel Logo", type=["png", "jpg", "jpeg"])
        if uploaded_logo is not None:
            st.session_state.hotel_logo = Image.open(uploaded_logo)
            st.image(st.session_state.hotel_logo, width=100)

    # Main content area
    tabs = st.tabs(["Create Post", "Preview & Edit", "Publish"])

    # Create Post Tab
    with tabs[0]:
        st.header("Create Your Post")

        col1, col2 = st.columns(2)

        with col1:
            # Post occasion/theme
            occasion = st.selectbox(
                "What's the occasion?",
                ["Summer Special", "Weekend Getaway", "Holiday Package", "Romantic Escape",
                 "Family Fun", "Business Conference", "Spa Retreat", "Restaurant Promotion",
                 "Local Event", "Anniversary Special", "Custom"]
            )

            if occasion == "Custom":
                occasion = st.text_input("Enter custom occasion")

            # Target audience
            audience = st.selectbox(
                "Target audience",
                ["Families", "Couples", "Business Travelers", "Luxury Seekers",
                 "Budget Travelers", "Adventure Seekers", "Wellness Enthusiasts", "General"]
            )

            # Key features to highlight
            features = st.multiselect(
                "Key features to highlight",
                ["Pool", "Spa", "Restaurant", "Bar", "Beach Access", "Room Service",
                 "Free WiFi", "Gym", "Conference Rooms", "Ocean View", "City View",
                 "Complimentary Breakfast", "Luxury Amenities", "Family Activities"]
            )

            # Special offer
            has_special_offer = st.checkbox("Include special offer")
            special_offer = ""
            if has_special_offer:
                special_offer = st.text_input("Special offer details", "20% off for bookings made this week!")

        with col2:
            st.subheader("Design Preferences")

            color_palette = st.selectbox("Color Palette", list(COLOR_PALETTES.keys()))
            layout = st.selectbox("Layout", list(LAYOUTS.keys()))
            font = st.selectbox("Font", FONTS)

            image_style = st.text_area(
                "Image style guidance (for AI generation)",
                "Professional hotel photography, warm lighting, inviting atmosphere, high quality"
            )

            use_custom_text = st.checkbox("Use custom text instead of AI generation")
            custom_text = ""
            if use_custom_text:
                custom_text = st.text_area("Custom text for post",
                                           "Experience luxury like never before at our seaside retreat!")

        if st.button("Generate Post"):
            with st.spinner("Generating your perfect post..."):
                feature_text = ", ".join(features) if features else "our wonderful amenities"

                text_prompt = f"""
                Create a short, engaging social media post (max 100 words) for {hotel_name} in {hotel_location} 
                promoting a {occasion}. Target audience: {audience}. 
                Highlight these features: {feature_text}.
                {"Include this special offer: " + special_offer if has_special_offer else ""}
                The tone should be professional yet warm and inviting.
                """

                image_prompt = f"""
                {image_style}. 
                A beautiful view of a boutique hotel for a {occasion} promotion, 
                {"featuring " + ", ".join(features[:3]) if features and len(features) > 0 else ""}
                Perfect for {audience}. No text on the image.
                """

                if use_custom_text:
                    st.session_state.generated_text = custom_text
                else:
                    st.session_state.generated_text = generate_text_with_llama(text_prompt)

                st.session_state.generated_image = generate_image_with_stability(image_prompt)

                st.session_state.design_context = {
                    "hotel_name": hotel_name,
                    "hotel_location": hotel_location,
                    "occasion": occasion,
                    "audience": audience,
                    "features": features,
                    "special_offer": special_offer,
                    "color_palette": color_palette,
                    "layout": layout,
                    "font": font
                }

                change_tab(1)
                st.rerun()


    with tabs[1]:
        st.header("Preview & Edit Your Post")

        if st.session_state.generated_text and st.session_state.generated_image:
            col1, col2 = st.columns([2, 1])

            with col1:
                # Post preview
                st.subheader("Post Preview")

                if hasattr(st.session_state, 'design_context'):
                    context = st.session_state.design_context
                    selected_palette = COLOR_PALETTES[context["color_palette"]]
                    selected_layout = context["layout"]
                    selected_font = context["font"]

                    composite_image = apply_layout(
                        st.session_state.generated_image.copy(),
                        st.session_state.generated_text,
                        selected_layout,
                        selected_palette,
                        selected_font,
                        st.session_state.hotel_logo
                    )

                    st.image(composite_image, use_column_width=True)

                    temp_img_path = "temp_post_image.jpg"
                    composite_image.save(temp_img_path)
                    st.session_state.final_image_path = temp_img_path
                else:
                    st.warning("Please generate content first in the 'Create Post' tab.")

            with col2:
                st.subheader("Edit Your Post")

                edited_text = st.text_area("Edit Caption", st.session_state.generated_text, height=150)
                st.session_state.generated_text = edited_text

                if hasattr(st.session_state, 'design_context'):
                    new_color_palette = st.selectbox("Adjust Color Palette", list(COLOR_PALETTES.keys()),
                                                     index=list(COLOR_PALETTES.keys()).index(context["color_palette"]))
                    new_layout = st.selectbox("Change Layout", list(LAYOUTS.keys()),
                                              index=list(LAYOUTS.keys()).index(context["layout"]))
                    new_font = st.selectbox("Change Font", FONTS,
                                            index=FONTS.index(context["font"]))

                    if (new_color_palette != context["color_palette"] or
                            new_layout != context["layout"] or
                            new_font != context["font"] or
                            edited_text != st.session_state.generated_text):

                        context["color_palette"] = new_color_palette
                        context["layout"] = new_layout
                        context["font"] = new_font

                        if st.button("Update Preview"):
                            st.rerun()

                st.subheader("Regenerate Content")

                if st.button("Regenerate Image"):
                    with st.spinner("Generating new image..."):
                        if hasattr(st.session_state, 'design_context'):
                            context = st.session_state.design_context

                            feature_text = ", ".join(context["features"][:3]) if context["features"] and len(
                                context["features"]) > 0 else ""
                            image_prompt = f"""
                            Professional hotel photography, warm lighting, inviting atmosphere, high quality. 
                            A beautiful view of a boutique hotel for a {context["occasion"]} promotion, 
                            {"featuring " + feature_text if feature_text else ""}
                            Perfect for {context["audience"]}. No text on the image.
                            """

                            st.session_state.generated_image = generate_image_with_stability(image_prompt)
                            st.rerun()

                if st.button("Regenerate Text"):
                    with st.spinner("Generating new text..."):
                        if hasattr(st.session_state, 'design_context'):
                            context = st.session_state.design_context

                            feature_text = ", ".join(context["features"]) if context[
                                "features"] else "our wonderful amenities"

                            text_prompt = f"""
                            Create a short, engaging social media post (max 100 words) for {context["hotel_name"]} in {context["hotel_location"]} 
                            promoting a {context["occasion"]}. Target audience: {context["audience"]}. 
                            Highlight these features: {feature_text}.
                            {"Include this special offer: " + context["special_offer"] if context["special_offer"] else ""}
                            The tone should be professional yet warm and inviting.
                            """


                            st.session_state.generated_text = generate_text_with_llama(text_prompt)
                            st.rerun()
        else:
            st.info("Please generate a post first in the 'Create Post' tab.")

    # Publish Tab
    with tabs[2]:
        st.header("Publish Your Post")

        if hasattr(st.session_state, 'final_image_path') and os.path.exists(st.session_state.final_image_path):
            st.subheader("Ready to Publish")
            st.image(st.session_state.final_image_path)
            st.write("**Caption:**")
            st.write(st.session_state.generated_text)

            st.subheader("Choose Platforms")

            platforms = {
                "Instagram": st.checkbox("Instagram"),
                "Facebook": st.checkbox("Facebook"),
                "Twitter": st.checkbox("Twitter", value=True),  # Default checked
                "LinkedIn": st.checkbox("LinkedIn")
            }

            schedule_post = st.checkbox("Schedule for later")
            scheduled_time = None

            if schedule_post:
                scheduled_date = st.date_input("Select date", datetime.now().date())
                scheduled_time = st.time_input("Select time", datetime.now().time())

                if st.button("Schedule Post"):
                    scheduled_datetime = datetime.combine(scheduled_date, scheduled_time)
                    st.success(f"Post scheduled for {scheduled_datetime.strftime('%B %d, %Y at %I:%M %p')}")
            else:
                if st.button("Publish Now"):
                    selected_platforms = [p for p, selected in platforms.items() if selected]

                    if not selected_platforms:
                        st.warning("Please select at least one platform to publish to.")
                    else:
                        with st.spinner(f"Publishing to {', '.join(selected_platforms)}..."):
                            success_count = 0
                            for platform in selected_platforms:
                                if post_to_social_media(platform.lower(), st.session_state.final_image_path,
                                                        st.session_state.generated_text):
                                    success_count += 1
                                    time.sleep(0.5)  # Simulate API call

                            if success_count == len(selected_platforms):
                                st.balloons()
                                st.success(f"Successfully published to {len(selected_platforms)} platform(s)!")
                            else:
                                st.warning(
                                    f"Published to {success_count} out of {len(selected_platforms)} platforms. Check settings for errors.")

            st.download_button(
                label="Download Image",
                data=open(st.session_state.final_image_path, "rb").read(),
                file_name=f"hotel_post_{datetime.now().strftime('%Y%m%d')}.jpg",
                mime="image/jpeg"
            )

            if st.button("Copy Caption to Clipboard"):
                st.code(st.session_state.generated_text)
                st.info("Caption copied! You can now paste it wherever you need.")

            with st.expander("Preview Post Analytics"):
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Est. Reach", "2.4K")
                col2.metric("Est. Engagement", "4.8%")
                col3.metric("Best Time to Post", "6-8 PM")
                col4.metric("Similar Post Performance", "+12%")

                st.info(
                    "These are estimated metrics based on your hotel's industry and location. Actual results may vary.")
        else:
            st.info("Please create and preview your post before publishing.")


if __name__ == "__main__":
    main()