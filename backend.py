import streamlit as st
import requests
import io
import base64
from PIL import Image, ImageDraw, ImageFont
import openai
import os
from datetime import datetime
import json
import time
from typing import Dict, List, Tuple, Optional
import math

def validate_api_keys():
    """Validate that required API keys are set."""
    if not st.secrets.get("GROQ_API_KEY"):
        st.error("GROQ API key is not set. Please set it in your secrets.toml file.")
        return False
    if not st.secrets.get("STABILITY_API_KEY"):
        st.error("Stability API key is not set. Please set it in your secrets.toml file.")
        return False
    return True

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
STABILITY_API_KEY = st.secrets.get("STABILITY_API_KEY", "")

SOCIAL_MEDIA_CREDENTIALS = {
    "instagram": st.secrets.get("INSTAGRAM_TOKEN", ""),
    "facebook": st.secrets.get("FACEBOOK_TOKEN", ""),
    "twitter": st.secrets.get("TWITTER_TOKEN", ""),
    "linkedin": st.secrets.get("LINKEDIN_TOKEN", "")
}

def generate_promotional_tagline(hotel_name: str, occasion: str, audience: str) -> str:
    if not GROQ_API_KEY:
        return "Please set your GROQ API key in the app settings."

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        # Special handling for Indian festivals
        festival_context = ""
        if occasion in ["Diwali", "Holi", "Independence Day", "Republic Day"]:
            festival_context = f"Create a culturally appropriate and festive tagline for {occasion} that resonates with Indian audiences. "

        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system",
                 "content": "You are a branding expert specializing in Indian hospitality and festivals. Create catchy promotional taglines (max 10 words) that blend traditional values with modern appeal."},
                {"role": "user",
                 "content": f"{festival_context}Create a short and catchy promotional tagline (max 10 words) for {hotel_name}. Occasion: {occasion}. Target Audience: {audience}. Keep it engaging, professional, and culturally appropriate."}
            ],
            "temperature": 0.9,
            "max_tokens": 20
        }

        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip().strip('"')

    except Exception as e:
        st.error(f"Error generating tagline: {str(e)}")
        return "Error generating tagline. Please try again."
    


def generate_text_with_llama(prompt: str) -> str:
    if not GROQ_API_KEY:
        return "Please set your GROQ API key in the app settings."

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        # Enhance the prompt for better context
        enhanced_prompt = f"""
        Create a short, engaging social media post (max 100 words) that:
        1. Uses warm, inviting language
        2. Highlights the unique aspects of the occasion
        3. Appeals to the target audience
        4. Includes relevant cultural elements for Indian festivals
        5. Maintains a professional yet friendly tone
        
        {prompt}
        """

        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system",
                 "content": "You are a professional social media marketer specializing in Indian hospitality and festivals. Create engaging captions that blend traditional values with modern appeal."},
                {"role": "user", "content": enhanced_prompt}
            ],
            "temperature": 0.8,
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
        # Updated Stability AI API endpoint
        url = "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image"

        headers = {
            "Authorization": f"Bearer {STABILITY_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Enhance the prompt for better image generation
        enhanced_prompt = f"""
        Professional hotel photography, {prompt}
        High quality, 4K resolution, perfect lighting, architectural details, inviting atmosphere
        No text or watermarks, suitable for social media
        """

        payload = {
            "text_prompts": [
                {"text": enhanced_prompt},
                {"text": "blurry, low quality, distorted, text, watermark, signature", "weight": -1}
            ],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30,
        }

        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 401:
            st.error("Invalid Stability API key. Please check your API key in the settings.")
            return None
            
        response.raise_for_status()

        data = response.json()
        image_data = base64.b64decode(data["artifacts"][0]["base64"])
        image = Image.open(io.BytesIO(image_data))
        return image

    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to Stability AI: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None


def apply_layout(image, text, layout_style, colors, font_name, logo=None, font_large_size=50):
    """Apply the selected layout to the image with text and logo."""
    draw = ImageDraw.Draw(image)
    width, height = image.size
    
    # Load fonts
    try:
        font_large = ImageFont.truetype(font_name, font_large_size)
    except:
        font_large = ImageFont.load_default()

    # Function to wrap text into multiple lines
    def wrap_text(text, font, max_width):
        words = text.split()
        lines = []
        current_line = []
        current_width = 0
        
        for word in words:
            word_width = draw.textbbox((0, 0), word + " ", font=font)[2]
            if current_width + word_width <= max_width:
                current_line.append(word)
                current_width += word_width
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_width = word_width
        
        if current_line:
            lines.append(" ".join(current_line))
        return lines

    # Calculate maximum width for text
    max_width = width - 100  # Leave 50px margin on each side
    
    # Wrap text into multiple lines
    lines = wrap_text(text, font_large, max_width)
    
    # Calculate total height needed for all lines
    line_height = font_large_size + 30  # Increased line spacing
    total_height = len(lines) * line_height
    
    # Create a semi-transparent overlay for better text visibility
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    # Apply layout-specific effects
    if layout_style == "Festive Diya":
        # Create a warm glow effect
        glow_radius = 100
        center_x = width // 2
        center_y = height - 150
        
        # Draw multiple layers of glow
        for i in range(3):
            alpha = int(50 * (1 - i/3))
            overlay_draw.ellipse([(center_x - glow_radius - i*20, center_y - glow_radius - i*20),
                                (center_x + glow_radius + i*20, center_y + glow_radius + i*20)],
                               fill=(255, 200, 0, alpha))
        
        # Draw diya pattern
        diya_width = 80
        diya_height = 100
        diya_x = center_x - diya_width // 2
        diya_y = center_y - diya_height // 2
        
        # Draw diya base
        overlay_draw.ellipse([(diya_x, diya_y), (diya_x + diya_width, diya_y + diya_height)],
                           fill=(255, 255, 255, 100))
        
        # Draw flame
        flame_points = [
            (center_x, diya_y - 30),
            (center_x - 20, diya_y - 60),
            (center_x + 20, diya_y - 60)
        ]
        overlay_draw.polygon(flame_points, fill=(255, 150, 0, 150))
        
        text_y = height - total_height - 100
    
    elif layout_style == "Festive Rangoli":
        # Create rangoli-inspired pattern
        pattern_size = 40
        for i in range(0, width, pattern_size):
            for j in range(0, height, pattern_size):
                # Draw flower pattern
                center_x = i + pattern_size // 2
                center_y = j + pattern_size // 2
                
                # Draw petals
                for angle in range(0, 360, 45):
                    rad = math.radians(angle)
                    x1 = center_x + pattern_size // 3 * math.cos(rad)
                    y1 = center_y + pattern_size // 3 * math.sin(rad)
                    x2 = center_x + pattern_size // 2 * math.cos(rad)
                    y2 = center_y + pattern_size // 2 * math.sin(rad)
                    overlay_draw.line([(x1, y1), (x2, y2)], fill=(255, 255, 255, 50), width=2)
                
                # Draw center dot
                overlay_draw.ellipse([(center_x - 3, center_y - 3),
                                    (center_x + 3, center_y + 3)],
                                   fill=(255, 255, 255, 100))
        
        text_y = height - total_height - 50
    
    elif layout_style == "Festive Toran":
        # Create toran-inspired design
        toran_height = 100
        pattern_width = 40
        
        # Draw main toran line
        overlay_draw.line([(0, toran_height), (width, toran_height)],
                         fill=(255, 255, 255, 100), width=3)
        
        # Draw hanging elements
        for i in range(0, width, pattern_width):
            # Draw bell
            bell_x = i + pattern_width // 2
            bell_y = toran_height + 20
            overlay_draw.ellipse([(bell_x - 10, bell_y),
                                (bell_x + 10, bell_y + 20)],
                               fill=(255, 255, 255, 150))
            
            # Draw hanging string
            overlay_draw.line([(bell_x, toran_height),
                             (bell_x, bell_y)],
                            fill=(255, 255, 255, 100), width=2)
        
        text_y = height - total_height - 50
    
    elif layout_style == "Festive Ganesha":
        # Create Ganesha-inspired pattern
        center_x = width // 2
        center_y = height - 150
        
        # Draw Ganesha's face
        face_radius = 60
        overlay_draw.ellipse([(center_x - face_radius, center_y - face_radius),
                            (center_x + face_radius, center_y + face_radius)],
                           fill=(255, 255, 255, 100))
        
        # Draw trunk
        trunk_points = [
            (center_x, center_y),
            (center_x + 40, center_y - 40),
            (center_x + 60, center_y - 20)
        ]
        overlay_draw.line(trunk_points, fill=(255, 255, 255, 150), width=5)
        
        # Draw ears
        ear_radius = 30
        overlay_draw.ellipse([(center_x - 80, center_y - 40),
                            (center_x - 40, center_y)],
                           fill=(255, 255, 255, 100))
        overlay_draw.ellipse([(center_x + 40, center_y - 40),
                            (center_x + 80, center_y)],
                           fill=(255, 255, 255, 100))
        
        text_y = height - total_height - 100
    
    elif layout_style == "Festive Om":
        # Create Om symbol pattern
        center_x = width // 2
        center_y = height - 150
        
        # Draw Om symbol
        om_radius = 80
        overlay_draw.ellipse([(center_x - om_radius, center_y - om_radius),
                            (center_x + om_radius, center_y + om_radius)],
                           outline=(255, 255, 255, 150), width=3)
        
        # Draw crescent moon
        moon_radius = 40
        overlay_draw.arc([(center_x - moon_radius, center_y - moon_radius),
                         (center_x + moon_radius, center_y + moon_radius)],
                        0, 180, fill=(255, 255, 255, 150), width=3)
        
        # Draw dot
        overlay_draw.ellipse([(center_x - 5, center_y - 5),
                            (center_x + 5, center_y + 5)],
                           fill=(255, 255, 255, 200))
        
        text_y = height - total_height - 100
    
    elif layout_style == "Festive Swastika":
        # Create swastika pattern
        center_x = width // 2
        center_y = height - 150
        
        # Draw swastika arms
        arm_length = 60
        arm_width = 20
        
        # Vertical arm
        overlay_draw.rectangle([(center_x - arm_width//2, center_y - arm_length),
                              (center_x + arm_width//2, center_y + arm_length)],
                             fill=(255, 255, 255, 150))
        
        # Horizontal arm
        overlay_draw.rectangle([(center_x - arm_length, center_y - arm_width//2),
                              (center_x + arm_length, center_y + arm_width//2)],
                             fill=(255, 255, 255, 150))
        
        # Draw dots at corners
        dot_radius = 5
        for dx in [-1, 1]:
            for dy in [-1, 1]:
                overlay_draw.ellipse([(center_x + dx*arm_length - dot_radius, center_y + dy*arm_length - dot_radius),
                                    (center_x + dx*arm_length + dot_radius, center_y + dy*arm_length + dot_radius)],
                                   fill=(255, 255, 255, 200))
        
        text_y = height - total_height - 100
    
    elif layout_style == "Festive Lotus":
        # Create lotus pattern
        center_x = width // 2
        center_y = height - 150
        
        # Draw lotus petals
        num_petals = 12
        petal_length = 60
        petal_width = 20
        
        for i in range(num_petals):
            angle = (2 * math.pi * i) / num_petals
            # Draw petal
            points = [
                (center_x, center_y),
                (center_x + petal_length * math.cos(angle), center_y + petal_length * math.sin(angle)),
                (center_x + (petal_length - petal_width) * math.cos(angle), center_y + (petal_length - petal_width) * math.sin(angle))
            ]
            overlay_draw.polygon(points, fill=(255, 255, 255, 150))
        
        # Draw center
        overlay_draw.ellipse([(center_x - 20, center_y - 20),
                            (center_x + 20, center_y + 20)],
                           fill=(255, 255, 255, 200))
        
        text_y = height - total_height - 100
    
    elif layout_style == "Festive Peacock":
        # Create peacock pattern
        center_x = width // 2
        center_y = height - 150
        
        # Draw peacock body
        body_radius = 30
        overlay_draw.ellipse([(center_x - body_radius, center_y - body_radius),
                            (center_x + body_radius, center_y + body_radius)],
                           fill=(255, 255, 255, 150))
        
        # Draw feathers
        num_feathers = 8
        feather_length = 80
        feather_width = 15
        
        for i in range(num_feathers):
            angle = (2 * math.pi * i) / num_feathers
            # Draw feather
            points = [
                (center_x, center_y),
                (center_x + feather_length * math.cos(angle), center_y + feather_length * math.sin(angle)),
                (center_x + (feather_length - feather_width) * math.cos(angle), center_y + (feather_length - feather_width) * math.sin(angle))
            ]
            overlay_draw.polygon(points, fill=(255, 255, 255, 100))
        
        # Draw head
        head_radius = 15
        overlay_draw.ellipse([(center_x + body_radius - head_radius, center_y - head_radius),
                            (center_x + body_radius + head_radius, center_y + head_radius)],
                           fill=(255, 255, 255, 150))
        
        text_y = height - total_height - 100
    
    elif layout_style == "Festive Border":
        # Create ornate border pattern
        border_width = 40
        
        # Draw main border lines
        overlay_draw.line([(0, border_width), (width, border_width)],
                         fill=(255, 255, 255, 100), width=3)
        overlay_draw.line([(0, height - border_width), (width, height - border_width)],
                         fill=(255, 255, 255, 100), width=3)
        
        # Draw corner decorations
        corner_size = 30
        # Top left
        overlay_draw.line([(0, border_width), (corner_size, border_width)],
                         fill=(255, 255, 255, 150), width=3)
        overlay_draw.line([(0, border_width), (0, border_width + corner_size)],
                         fill=(255, 255, 255, 150), width=3)
        
        # Top right
        overlay_draw.line([(width - corner_size, border_width), (width, border_width)],
                         fill=(255, 255, 255, 150), width=3)
        overlay_draw.line([(width, border_width), (width, border_width + corner_size)],
                         fill=(255, 255, 255, 150), width=3)
        
        # Bottom left
        overlay_draw.line([(0, height - border_width), (corner_size, height - border_width)],
                         fill=(255, 255, 255, 150), width=3)
        overlay_draw.line([(0, height - border_width - corner_size), (0, height - border_width)],
                         fill=(255, 255, 255, 150), width=3)
        
        # Bottom right
        overlay_draw.line([(width - corner_size, height - border_width), (width, height - border_width)],
                         fill=(255, 255, 255, 150), width=3)
        overlay_draw.line([(width, height - border_width - corner_size), (width, height - border_width)],
                         fill=(255, 255, 255, 150), width=3)
        
        # Draw decorative elements along borders
        for i in range(0, width, 100):
            # Top border
            overlay_draw.ellipse([(i - 5, border_width - 5),
                                (i + 5, border_width + 5)],
                               fill=(255, 255, 255, 150))
            # Bottom border
            overlay_draw.ellipse([(i - 5, height - border_width - 5),
                                (i + 5, height - border_width + 5)],
                               fill=(255, 255, 255, 150))
        
        text_y = height - total_height - 50
    
    else:  # Festive Mandala
        # Create mandala pattern
        center_x = width // 2
        center_y = height // 2
        max_radius = min(width, height) // 3
        
        # Draw concentric circles
        for i in range(5):
            radius = max_radius * (i + 1) / 5
            overlay_draw.ellipse([(center_x - radius, center_y - radius),
                                (center_x + radius, center_y + radius)],
                               outline=(255, 255, 255, 100), width=2)
        
        # Draw decorative elements
        for i in range(8):
            angle = (2 * math.pi * i) / 8
            x = center_x + max_radius * math.cos(angle)
            y = center_y + max_radius * math.sin(angle)
            overlay_draw.ellipse([(x - 10, y - 10),
                                (x + 10, y + 10)],
                               fill=(255, 255, 255, 150))
        
        text_y = height - total_height - 50
    
    # Merge the overlay with the original image
    image = Image.alpha_composite(image.convert('RGBA'), overlay)
    draw = ImageDraw.Draw(image)
    
    # Draw text with shadow for better visibility
    shadow_offset = 2
    for i, line in enumerate(lines):
        # Draw shadow
        draw.text((51, text_y + i * line_height + 1), line, font=font_large, fill=(0, 0, 0, 128))
        # Draw main text
        draw.text((50, text_y + i * line_height), line, font=font_large, fill=colors[0])
    
    # Add logo if provided
    if logo:
        logo_width = 100
        logo_height = int(logo_width * (logo.size[1] / logo.size[0]))
        logo_x = width - logo_width - 20
        logo_y = 20
        image.paste(logo, (logo_x, logo_y), logo)

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

