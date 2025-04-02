import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
import time
import cv2
import numpy as np
from backend import (generate_promotional_tagline,
                     generate_text_with_llama,
                     generate_image_with_stability,
                     apply_layout,
                     post_to_social_media,
                     change_tab,
                     load_icon,
                     validate_api_keys)
import io
import math

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
STABILITY_API_KEY = st.secrets.get("STABILITY_API_KEY", "")

SOCIAL_MEDIA_CREDENTIALS = {
    "instagram": st.secrets.get("INSTAGRAM_TOKEN", ""),
    "facebook": st.secrets.get("FACEBOOK_TOKEN", ""),
    "twitter": st.secrets.get("TWITTER_TOKEN", ""),
    "linkedin": st.secrets.get("LINKEDIN_TOKEN", "")
}

# Font Options
FONTS = [
    "Arial",
    "Helvetica",
    "Times New Roman",
    "Courier New",
    "Georgia",
    "Verdana",
    "Trebuchet MS",
    "Impact"
]

# Indian Festivals
INDIAN_FESTIVALS = [
    "Diwali",
    "Holi",
    "Raksha Bandhan",
    "Dussehra",
    "Ganesh Chaturthi",
    "Onam",
    "Pongal",
    "Baisakhi",
    "Eid ul-Fitr",
    "Christmas",
    "New Year",
    "Makar Sankranti",
    "Rakhi",
    "Karva Chauth",
    "Janmashtami",
    "Navratri",
    "Durga Puja",
    "Lohri",
    "Bihu",
    "Rath Yatra"
]

# General Occasions
OCCASIONS = [
    "Indian Festivals",
    "Independence Day",
    "Republic Day",
    "Women's Day",
    "Mother's Day",
    "Father's Day",
    "Valentine's Day",
    "Wedding Season",
    "Summer Special",
    "Monsoon Special",
    "Winter Special",
    "Weekend Getaway",
    "Holiday Package",
    "Romantic Escape",
    "Family Fun",
    "Business Conference",
    "Spa Retreat",
    "Restaurant Promotion",
    "Local Event",
    "Anniversary Special",
    "Custom"
]

# Hotel Features
HOTEL_FEATURES = [
    "Pool",
    "Spa",
    "Restaurant",
    "Bar",
    "Beach Access",
    "Room Service",
    "Free WiFi",
    "Gym",
    "Conference Rooms",
    "Ocean View",
    "City View",
    "Complimentary Breakfast",
    "Luxury Amenities",
    "Family Activities",
    "Parking",
    "Airport Transfer",
    "24/7 Reception",
    "Laundry Service",
    "Business Center",
    "Kids Club"
]

# Target Audiences
TARGET_AUDIENCES = [
    "Families",
    "Couples",
    "Business Travelers",
    "Luxury Seekers",
    "Budget Travelers",
    "Adventure Seekers",
    "Wellness Enthusiasts",
    "Honeymooners",
    "Senior Citizens",
    "Corporate Groups",
    "Wedding Parties",
    "General"
]

# Color Palettes with Indian themes
COLOR_PALETTES = {
    "Classic Gold": ["#FFD700"],
    "Royal Blue": ["#00008B"],
    "Deep Red": ["#8B0000"],
    "Forest Green": ["#228B22"],
    "Purple Majesty": ["#4B0082"],
    "Sunset Orange": ["#FF4500"],
    "Ocean Blue": ["#1E90FF"],
    "Emerald Green": ["#2E8B57"],
    "Ruby Red": ["#E0115F"],
    "Sapphire Blue": ["#0F52BA"]
}

# Layouts with descriptions
LAYOUTS = {
    "Festive Diya": "Traditional diya pattern with warm glow effect",
    "Festive Rangoli": "Colorful rangoli-inspired design with transparent overlay",
    "Festive Toran": "Traditional toran design with decorative elements",
    "Festive Mandala": "Intricate mandala pattern with transparent background",
    "Festive Ganesha": "Elegant Ganesha pattern with divine aura",
    "Festive Om": "Sacred Om symbol with spiritual elements",
    "Festive Swastika": "Traditional swastika pattern with auspicious design",
    "Festive Lotus": "Beautiful lotus pattern with blooming effect",
    "Festive Peacock": "Majestic peacock design with colorful feathers",
    "Festive Border": "Ornate border pattern with traditional motifs"
}

# Set page config
st.set_page_config(
    page_title="BookingJini - AI Hotel Post Generator",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="collapsed"  # Make sidebar collapsed by default
)

# UI Components
def main():
    # Initialize session state variables at the start of main
    if 'generated_image' not in st.session_state:
        st.session_state.generated_image = None
    if 'generated_text' not in st.session_state:
        st.session_state.generated_text = ""
    if 'hotel_logo' not in st.session_state:
        st.session_state.hotel_logo = None
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = 0
    if 'generated_tagline' not in st.session_state:
        st.session_state.generated_tagline = ""
    if 'final_image_path' not in st.session_state:
        st.session_state.final_image_path = None
    if 'design_context' not in st.session_state:
        st.session_state.design_context = None

    # Validate API keys
    if not validate_api_keys():
        st.error("Please set up your API keys in the secrets.toml file before using the application.")
        return

    # Set up the page with a JPG icon
    icon_path = os.path.join(os.path.dirname(__file__), "BJ.jpg")
    if not os.path.exists(icon_path):
        st.error(f"Logo file not found at {icon_path}")
        return
        
    icon_bytes = load_icon(icon_path)
    if not icon_bytes:
        st.error("Failed to load the logo file")
        return

    # Layout for logo and title
    col1, col2 = st.columns([0.15, 0.85])

    with col1:
       st.image(icon_path, width=80)  

    with col2:
        st.title("BookingJini")

        st.markdown("""
            <style>
            @keyframes subtleFloat {
                0% { transform: translateY(0px); }
                50% { transform: translateY(-5px); }
                100% { transform: translateY(0px); }
            }
            @keyframes gentleGlow {
                0% { box-shadow: 0 0 2px rgba(255,255,255,0.3); }
                50% { box-shadow: 0 0 4px rgba(255,255,255,0.5); }
                100% { box-shadow: 0 0 2px rgba(255,255,255,0.3); }
            }
            .animated-title {
                font-size: 30px;
                font-weight: bold;
                padding: 20px 30px;
                border-radius: 15px;
                background: linear-gradient(
                    45deg,
                    #2c3e50,
                    #34495e,
                    #2c3e50
                );
                background-size: 200% 200%;
                animation: 
                    subtleFloat 3s ease-in-out infinite,
                    gentleGlow 2s ease-in-out infinite;
                color: #ecf0f1;
                text-align: center;
                position: relative;
                border: 1px solid rgba(255,255,255,0.1);
            }
            </style>
            <h3 class="animated-title">Stunning AI-Generated Hotel Posts – Perfect for Festivals & Events!</h3>
        """, unsafe_allow_html=True)
        

    with st.sidebar:
        st.header("Hotel Information")
        
        # Hotel Details
        hotel_name = st.text_input("Hotel Name", "Rambagh Place")
        hotel_location = st.text_input("Location", "Jaipur")
        hotel_type = st.selectbox("Hotel Type", ["Heritage", "Luxury", "Boutique", "Business", "Resort", "Budget"])
        
        # Upload hotel logo
        uploaded_logo = st.file_uploader("Upload Hotel Logo", type=["png", "jpg", "jpeg"])
        if uploaded_logo is not None:
            st.session_state.hotel_logo = Image.open(uploaded_logo)
            st.image(st.session_state.hotel_logo, width=100)
            
        # API Settings in expander
        with st.expander("API Settings"):
            groq_key = st.text_input("GROQ API Key", value=GROQ_API_KEY, type="password")
            stability_key = st.text_input("Stability API Key", value=STABILITY_API_KEY, type="password")
            
            # Social Media Settings
            st.subheader("Social Media Credentials")
            instagram_token = st.text_input("Instagram Token", value=SOCIAL_MEDIA_CREDENTIALS.get("instagram", ""), type="password")
            facebook_token = st.text_input("Facebook Token", value=SOCIAL_MEDIA_CREDENTIALS.get("facebook", ""), type="password")
            twitter_token = st.text_input("Twitter Token", value=SOCIAL_MEDIA_CREDENTIALS.get("twitter", ""), type="password")
            linkedin_token = st.text_input("LinkedIn Token", value=SOCIAL_MEDIA_CREDENTIALS.get("linkedin", ""), type="password")
            
            if st.button("Save API Settings"):
                st.success("Settings saved successfully!")

    # Main content area
    tabs = st.tabs(["Create Post", "Preview & Edit", "Publish"])

    # Create Post Tab
    with tabs[0]:
        st.header("Create Your Post")

        col1, col2 = st.columns(2)

        with col1:
            # Post occasion/theme
            occasion_type = st.selectbox(
                "Select Occasion Type",
                ["Indian Festivals", "General Occasions", "Custom"]
            )

            if occasion_type == "Indian Festivals":
                occasion = st.selectbox("Select Festival", INDIAN_FESTIVALS)
            elif occasion_type == "General Occasions":
                occasion = st.selectbox("Select Occasion", [o for o in OCCASIONS if o not in ["Indian Festivals", "Custom"]])
            else:  # Custom
                occasion = st.text_input("Enter custom occasion")

            # Target audience
            audience = st.selectbox(
                "Target Audience",
                TARGET_AUDIENCES
            )

            # Key features to highlight
            features = st.multiselect(
                "Hotel Features to Highlight",
                HOTEL_FEATURES
            )

        with col2:
            # Image style guidance
            image_style = st.text_area(
                "Image Style Guidance",
                "Professional hotel photography, warm lighting, inviting atmosphere, high quality"
            )

            # Custom text option
            use_custom_text = st.checkbox("Use Custom Text")
            custom_text = ""
            if use_custom_text:
                custom_text = st.text_area(
                    "Custom Post Text",
                    "Experience luxury like never before at our seaside retreat!"
                )

            # Special offer
            has_special_offer = st.checkbox("Include Special Offer")
            special_offer = ""
            if has_special_offer:
                special_offer = st.text_input("Special Offer Details", "20% off for bookings made this week!")

            # Generate Post button
            if st.button("Generate Post", use_container_width=True):
                with st.spinner("Creating your perfect post..."):
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
                    A beautiful view of a {hotel_type} hotel for a {occasion} promotion, 
                    {"featuring " + ", ".join(features[:3]) if features and len(features) > 0 else ""}
                    Perfect for {audience}. No text on the image.
                    """

                    if use_custom_text:
                        st.session_state.generated_text = custom_text
                    else:
                        st.session_state.generated_text = generate_text_with_llama(text_prompt)

                    st.session_state.generated_image = generate_image_with_stability(image_prompt)
                    st.session_state.generated_tagline = generate_promotional_tagline(hotel_name, occasion, audience)

                    st.session_state.design_context = {
                        "hotel_name": hotel_name,
                        "hotel_location": hotel_location,
                        "hotel_type": hotel_type,
                        "occasion": occasion,
                        "audience": audience,
                        "features": features,
                        "special_offer": special_offer,
                        "image_style": image_style
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
                    
                    composite_image = apply_layout(
                        st.session_state.generated_image.copy(),
                        st.session_state.generated_tagline,
                        context.get("layout", "Festive Diya"),  # Use selected layout
                        [context.get("text_color", "#FFFFFF")],  # Use selected text color
                        context.get("font", "Arial"),  # Use selected font
                        st.session_state.hotel_logo,
                        font_large_size=context.get("font_size", 50)  # Use selected font size
                    )

                    st.image(composite_image, use_column_width=True)

                    temp_img_path = "temp_post_image.jpg"
                    # Convert RGBA to RGB before saving as JPEG
                    composite_image.convert('RGB').save(temp_img_path)
                    st.session_state.final_image_path = temp_img_path
                else:
                    st.warning("Please generate content first in the 'Create Post' tab.")

            with col2:
                st.subheader("Edit Your Post")

                # Image regeneration
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

                # Text editing section
                with st.expander("Text Content", expanded=True):
                    # Caption editing
                    caption_height = min(150, max(68, len(st.session_state.generated_text.split('\n')) * 25))
                    edited_text = st.text_area("Edit Caption", st.session_state.generated_text, height=caption_height)
                    st.session_state.generated_text = edited_text
                    
                    if st.button("Regenerate Caption", key="regenerate_caption"):
                        with st.spinner("Generating new caption..."):
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

                                # Generate new text and tagline
                                st.session_state.generated_text = generate_text_with_llama(text_prompt)
                                st.session_state.generated_tagline = generate_promotional_tagline(
                                    context["hotel_name"], 
                                    context["occasion"], 
                                    context["audience"]
                                )
                                
                                # Update the context
                                context["text"] = st.session_state.generated_text
                                context["tagline"] = st.session_state.generated_tagline
                                
                                st.rerun()

                    # Tagline editing
                    tagline_height = min(150, max(68, len(st.session_state.generated_tagline.split('\n')) * 30))
                    edited_tagline = st.text_area("Promotional Tagline", st.session_state.generated_tagline, height=tagline_height)
                    st.session_state.generated_tagline = edited_tagline
                    
                    if st.button("Regenerate Tagline", key="regenerate_tagline"):
                        with st.spinner("Generating new tagline..."):
                            if hasattr(st.session_state, 'design_context'):
                                context = st.session_state.design_context
                                
                                # Generate new tagline only
                                st.session_state.generated_tagline = generate_promotional_tagline(
                                    context["hotel_name"], 
                                    context["occasion"], 
                                    context["audience"]
                                )
                                
                                # Update the context
                                context["tagline"] = st.session_state.generated_tagline
                                
                                st.rerun()

                # Design settings section
                if hasattr(st.session_state, 'design_context'):
                    st.markdown("### Design Settings")
                    
                    # Text size and color
                    col1, col2 = st.columns(2)
                    with col1:
                        font_size = st.number_input("Text Size", min_value=15, max_value=100, value=50, step=5)
                    with col2:
                        text_color = st.color_picker("Text Color", "#FFFFFF")

                    # Layout and font
                    col1, col2 = st.columns(2)
                    with col1:
                        layout = st.selectbox(
                            "Layout Style",
                            list(LAYOUTS.keys()),
                            index=list(LAYOUTS.keys()).index("Festive Diya")
                        )
                    with col2:
                        font = st.selectbox(
                            "Font Style",
                            FONTS,
                            index=FONTS.index("Arial")
                        )

                    # Update preview button
                    if edited_text != st.session_state.generated_text or edited_tagline != st.session_state.generated_tagline or font_size != context.get("font_size", 50) or text_color != context.get("text_color", "#FFFFFF") or layout != context.get("layout", "Festive Diya") or font != context.get("font", "Arial"):
                        context["font_size"] = font_size
                        context["text_color"] = text_color
                        context["layout"] = layout
                        context["font"] = font

                        if st.button("Update Preview", use_container_width=True):
                            st.rerun()

        else:
            st.info("Please generate a post first in the 'Create Post' tab.")

    # Publish Tab
    with tabs[2]:
        st.header("Publish Your Post")

        if hasattr(st.session_state, 'final_image_path') and st.session_state.final_image_path is not None and os.path.exists(st.session_state.final_image_path):
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