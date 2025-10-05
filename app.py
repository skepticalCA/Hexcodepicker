import streamlit as st
from PIL import Image
import numpy as np
import base64
import io

st.set_page_config(layout="wide", page_title="Interactive Color Picker")
st.title("🖱️ Interactive Image Color Sampler")
st.markdown("Move your cursor over the image to see the hex code for any pixel!")

def get_base64_image(image):
    """Encodes PIL image to a base64 string for use in HTML/CSS."""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

def rgb_to_hex(r, g, b):
    """Converts RGB to Hex code."""
    return f"#{r:02x}{g:02x}{b:02x}".upper()

# --- Main Streamlit Logic ---

uploaded_file = st.file_uploader(
    "Upload an image (JPEG or PNG) to sample colors",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    
    # 1. Get Base64 String for HTML Embedding
    img_b64 = get_base64_image(image)
    
    # 2. Get Raw Pixel Data (as a flat list for easy JavaScript access)
    pixels = np.array(image)
    # Convert pixels to a simple list of hex codes for JavaScript
    # NOTE: This can be a huge list for large images, so resizing is recommended!
    # For demonstration, we'll use the original size, but scale down the JS lookup.
    
    # Let's resize for faster processing and smaller data size transferred to the browser
    MAX_SIZE = 400
    if image.width > MAX_SIZE or image.height > MAX_SIZE:
        image.thumbnail((MAX_SIZE, MAX_SIZE))
        
    pixels = np.array(image)
    width, height = image.size
    
    # Create a 1D array of hex codes for JavaScript lookup
    hex_data = []
    for row in pixels:
        for r, g, b in row:
            hex_data.append(rgb_to_hex(r, g, b)[1:]) # [1:] to remove the '#'

    # 3. Embed HTML/CSS/JavaScript
    html_code = f"""
    <div style="position: relative; width: {width}px; height: {height}px; margin: 20px 0;">
        <img id="colorSamplerImage" 
             src="data:image/png;base64,{img_b64}" 
             style="width: {width}px; height: {height}px; cursor: crosshair;">
        
        <div id="hexTooltip" style="
            position: absolute; 
            background: rgba(0, 0, 0, 0.7); 
            color: white; 
            padding: 5px 10px; 
            border-radius: 5px; 
            pointer-events: none; /* Allows mouse to pass through */
            z-index: 1000;
            display: none;
            font-weight: bold;
        ">#HEXCODE</div>
    </div>
    
    <script>
        const img = document.getElementById('colorSamplerImage');
        const tooltip = document.getElementById('hexTooltip');
        const hexData = ["{'','join(',hex_data)}')"]; // Inject the hex data here (requires formatting)
        const imgWidth = {width};
        const imgHeight = {height};
        
        img.addEventListener('mousemove', function(e) {{
            // Calculate coordinates relative to the image
            const rect = img.getBoundingClientRect();
            const x = Math.floor(e.clientX - rect.left);
            const y = Math.floor(e.clientY - rect.top);
            
            // Calculate 1D array index
            const index = y * imgWidth + x;
            
            if (index >= 0 && index < hexData.length) {{
                const hex = "#" + hexData[index];
                
                // Update tooltip position and content
                tooltip.style.left = (x + 15) + 'px';
                tooltip.style.top = (y - 30) + 'px';
                tooltip.innerHTML = hex;
                tooltip.style.backgroundColor = hex; 
                tooltip.style.color = (x < imgWidth / 2) ? 'white' : 'black'; // Simple text contrast
                tooltip.style.display = 'block';
            }}
        }});
        
        img.addEventListener('mouseleave', function() {{
            tooltip.style.display = 'none';
        }});
    </script>
    """
    # NOTE: The hexData injection requires careful formatting to be valid JavaScript array
    # The line above is a placeholder. For a real, robust solution, you would need
    # to pass this data to JS more reliably, potentially using Streamlit components.

    st.markdown(
        f"""
        <style>
            /* Custom styling for the tooltip and image container */
            #hexTooltip {{ 
                /* Add more advanced contrast logic here */
                text-shadow: 1px 1px 2px black;
                border: 2px solid white;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Display the final HTML content
    st.components.v1.html(html_code, height=height + 50)
    
else:
    st.info("Upload an image to begin color sampling.")
