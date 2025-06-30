# BookingJini - AI Hotel Post Generator 🏨

A powerful AI-driven application that generates promotional content and social media posts for hotels and hospitality businesses. Built with Streamlit, it combines AI text generation and image creation to help hotels create engaging marketing materials for various occasions and festivals.

## ✨ Features

### 🎯 AI-Powered Content Generation
- **Promotional Taglines**: Generate catchy, culturally-appropriate taglines using Groq's Llama model
- **Social Media Posts**: Create engaging captions tailored for different platforms
- **AI Image Generation**: Generate high-quality hotel images using Stability AI

### 🎨 Customizable Design Elements
- **Multiple Layout Styles**: 10+ traditional Indian festival-inspired layouts
- **Color Palettes**: 10 curated color schemes including classic gold, royal blue, and festive colors
- **Font Options**: 8 professional font choices
- **Logo Integration**: Add your hotel logo to generated posts

### 🏮 Indian Festival & Occasion Support
- **Traditional Festivals**: Diwali, Holi, Raksha Bandhan, Dussehra, Ganesh Chaturthi, and more
- **National Holidays**: Independence Day, Republic Day
- **Special Occasions**: Wedding Season, Valentine's Day, Family Fun, Business Conferences
- **Seasonal Promotions**: Summer, Monsoon, Winter specials

### 📱 Social Media Integration
- **Multi-Platform Support**: Instagram, Facebook, Twitter, LinkedIn
- **Direct Posting**: Post generated content directly to social media platforms
- **Custom Captions**: Tailored content for each platform

### 🎯 Target Audience Focus
- Families, Couples, Business Travelers
- Luxury Seekers, Budget Travelers
- Adventure Seekers, Wellness Enthusiasts
- Honeymooners, Corporate Groups

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- API keys for Groq and Stability AI
- Social media platform tokens (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/BookingJini.git
   cd BookingJini
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API keys**
   
   Create a `.streamlit/secrets.toml` file:
   ```toml
   GROQ_API_KEY = "your_groq_api_key_here"
   STABILITY_API_KEY = "your_stability_api_key_here"
   
   # Optional: Social media tokens
   INSTAGRAM_TOKEN = "your_instagram_token"
   FACEBOOK_TOKEN = "your_facebook_token"
   TWITTER_TOKEN = "your_twitter_token"
   LINKEDIN_TOKEN = "your_linkedin_token"
   ```

5. **Run the application**
   ```bash
   streamlit run frontend.py
   ```

## 🛠️ Tools, Frameworks & Libraries

### Core Framework
- **Streamlit (v1.32.0)** - Web application framework for creating interactive data apps
  - Provides the main UI components and web interface
  - Handles session state management and user interactions
  - Enables real-time updates and responsive design

### AI & Machine Learning
- **Groq (v0.4.2)** - High-performance AI inference platform
  - Powers the Llama 3.3 70B model for text generation
  - Generates promotional taglines and social media content
  - Provides fast, reliable AI responses

- **Stability SDK (v0.8.5)** - Official Python SDK for Stability AI
  - Integrates with Stable Diffusion v1.6 for image generation
  - Creates high-quality hotel and promotional images
  - Supports custom prompts and image customization

### Image Processing & Graphics
- **Pillow (v10.2.0)** - Python Imaging Library (PIL)
  - Handles image manipulation and processing
  - Applies layouts, text overlays, and design elements
  - Supports various image formats (JPEG, PNG, etc.)
  - Manages font rendering and text positioning

- **OpenCV (cv2)** - Computer vision library
  - Image preprocessing and enhancement
  - Color space conversions and filtering
  - Image analysis and manipulation

- **NumPy** - Numerical computing library
  - Array operations for image data
  - Mathematical computations for image processing
  - Data manipulation and transformation

### Web & API Integration
- **Requests (v2.31.0)** - HTTP library for Python
  - Makes API calls to Groq and Stability AI
  - Handles social media platform integrations
  - Manages authentication and response processing

### Development & Environment
- **python-dotenv (v1.0.1)** - Environment variable management
  - Loads environment variables from .env files
  - Manages API keys and configuration securely
  - Separates development and production settings

### UI Enhancement
- **streamlit-image-cropper (v0.1.0)** - Image cropping component
  - Provides interactive image cropping functionality
  - Allows users to customize image dimensions
  - Enhances user experience for image editing

### Additional Dependencies
- **datetime** - Date and time handling
  - Manages timestamps for posts and content
  - Handles date-based occasion selection

- **json** - JSON data processing
  - Parses API responses
  - Handles configuration data

- **io** - Input/output operations
  - Manages file and data streams
  - Handles image data conversion

- **base64** - Base64 encoding/decoding
  - Processes image data for API transmission
  - Handles binary data encoding

- **math** - Mathematical operations
  - Calculates layout positioning
  - Handles geometric computations

- **os** - Operating system interface
  - File path management
  - Environment variable access

- **time** - Time-related functions
  - API  limiting
  - Performance monitoring

## 🔧 API Setup

### Groq API (Required)
1. Sign up at [Groq Console](https://console.groq.com/)
2. Generate an API key
3. Add to `secrets.toml` as `GROQ_API_KEY`

### Stability AI API (Required)
1. Sign up at [Stability AI](https://platform.stability.ai/)
2. Generate an API key
3. Add to `secrets.toml` as `STABILITY_API_KEY`

### Social Media APIs (Optional)
- **Instagram**: Use Facebook Graph API
- **Facebook**: Facebook Graph API
- **Twitter**: Twitter API v2
- **LinkedIn**: LinkedIn Marketing API

## 📖 Usage Guide

### 1. Basic Post Generation
1. Enter your hotel name
2. Select an occasion or festival
3. Choose your target audience
4. Click "Generate Tagline" to create a promotional tagline
5. Click "Generate Post" to create full social media content

### 2. Customizing Design
1. **Layout**: Choose from 10 traditional Indian festival-inspired layouts
2. **Colors**: Select from curated color palettes
3. **Fonts**: Pick from 8 professional font options
4. **Logo**: Upload your hotel logo for branding

### 3. Image Generation
1. Describe your desired hotel image
2. The AI will generate a high-quality image
3. Apply your chosen layout and design elements
4. Download the final image

### 4. Social Media Posting
1. Review your generated content
2. Select target social media platforms
3. Click "Post to Social Media" to publish directly

## 🏗️ Project Structure

```
BookingJini/
├── frontend.py          # Main Streamlit application
├── backend.py           # AI integration and business logic
├── requirements.txt     # Python dependencies
├── BJ.jpg              # Application logo
├── .streamlit/         # Streamlit configuration
│   └── secrets.toml    # API keys and secrets
└── README.md           # This file
```

## 🎨 Design Features

### Layout Styles
- **Festive Diya**: Traditional diya pattern with warm glow
- **Festive Rangoli**: Colorful rangoli-inspired design
- **Festive Toran**: Traditional toran design
- **Festive Mandala**: Intricate mandala patterns
- **Festive Ganesha**: Elegant Ganesha patterns
- And 5 more traditional Indian designs

### Color Palettes
- Classic Gold, Royal Blue, Deep Red
- Forest Green, Purple Majesty, Sunset Orange
- Ocean Blue, Emerald Green, Ruby Red, Sapphire Blue

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/BookingJini/issues) page
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce

## 🙏 Acknowledgments

- **Groq** for providing the Llama 3.3 70B model
- **Stability AI** for Stable Diffusion image generation
- **Streamlit** for the amazing web app framework
- **Indian Cultural Heritage** for inspiring the traditional designs

---

**Made with ❤️ for the Indian hospitality industry**

*Transform your hotel's social media presence with AI-powered content generation!* 
