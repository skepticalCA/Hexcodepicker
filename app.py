import streamlit as st
from PIL import Image
import numpy as np
import base64
import io

# Set the page configuration for a wider layout
st.set_page_config(layout="wide", page_title="Interactive Color Picker")
st.title("🖱️ Interactive Image Color Sampler")
st.markdown("Upload an image, then **move your cursor over it** to sample the hex code for any pixel!")

def get_base64_image(image):
    """Encodes PIL image to a base64 string for use in HTML/CSS."""
    buffered = io.BytesIO()
    # Save as JPEG for better compression/smaller size in the HTML payload
    image.save(buffered, format="JPEG", quality=90)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

def rgb_to_hex(r, g, b):
    """Converts RGB tuple to Hex code (e.g., '#FF00A0')."""
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}".upper()

# --- Main Streamlit Logic ---

uploaded_file = st.file_uploader(
    "Upload an image (JPEG or PNG) to sample colors",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    try:
        # 1. Image Processing
        image = Image.open(uploaded_file).convert("RGB")
        
        # Resize image for faster JavaScript processing and smaller data size
        # We cap the size to prevent the app from crashing on huge images
        MAX_SIZE = 600
        if image.width > MAX_SIZE or image.height > MAX_SIZE:
            image.thumbnail((MAX_SIZE, MAX_SIZE))
            
        pixels = np.array(image)
        width, height = image.size
        
        # Get Base64 String for HTML Embedding
        img_b64 = get_base64_image(image)
        
        # 2. Prepare Hex Data for JavaScript
        hex_data = []
        for row in pixels:
            for r, g, b in row:
                # Store hex codes without the '#' prefix
                hex_data.append(rgb_to_hex(r, g, b)[1:]) 

        # CRITICAL FIX: Format the Python list into a clean JavaScript array string
        # e.g., 'FF0000', '00FF00', ...
        js_hex_data = ','.join([f"'{h}'" for h in hex_data])
        
        # 3. Embed HTML/CSS/JavaScript
        html_code = f"""
        <div style="position: relative; width: {width}px; height: {height}px; margin: 20px 0;">
            <img id="colorSamplerImage" 
                 src="data:image/jpeg;base64,{img_b64}" 
                 style="width: {width}px; height: {height}px; cursor: crosshair;">
            
            <div id="hexTooltip" style="
                position: absolute; 
                background: rgba(255, 255, 255, 0.9); 
                padding: 5px 10px; 
                border-radius: 5px; 
                pointer-events: none; /* Allows mouse to pass through */
                z-index: 1000;
                display: none;
                font-weight: bold;
                border: 2px solid #333;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            ">#HEXCODE</div>
        </div>
        
        <script>
            const img = document.getElementById('colorSamplerImage');
            const tooltip = document.getElementById('hexTooltip');
            
            // Python data injection (now fixed)
            const hexData = [{js_hex_data}]; 
            
            const imgWidth = {width};
            const imgHeight = {height};
            
            img.addEventListener('mousemove', function(e) {{
                // Get image's bounding box to calculate relative position
                const rect = img.getBoundingClientRect();
                
                // Calculate coordinates relative to the image (0 to width/height)
                const x = Math.floor(e.clientX - rect.left);
                const y = Math.floor(e.clientY - rect.top);
                
                // Calculate 1D array index: index = (row * width) + column
                const index = y * imgWidth + x;
                
                if (index >= 0 && index < hexData.length) {{
                    const hex = "#" + hexData[index];
                    
                    // Simple contrast check for text color (optional but nice)
                    // Checks if the color is dark (sum of RGB values < threshold)
                    const r = parseInt(hexData[index].substring(0, 2), 16);
                    const g = parseInt(hexData[index].substring(2, 4), 16);
                    const b = parseInt(hexData[index].substring(4, 6), 16);
                    const isDark = (r * 0.299 + g * 0.587 + b * 0.114) < 150;
                    
                    // Update tooltip position, content, and style
                    tooltip.style.left = (x + 15) + 'px'; // Offset right
                    tooltip.style.top = (y - 30) + 'px';  // Offset up
                    tooltip.innerHTML = hex;
                    tooltip.style.backgroundColor = hex; 
                    tooltip.style.color = isDark ? 'white' : 'black';
                    tooltip.style.border = isDark ? '2px solid white' : '2px solid black';
                    tooltip.style.display = 'block';
                }}
            }});
            
            img.addEventListener('mouseleave', function() {{
                tooltip.style.display = 'none';
            }});
        </script>
        """
        
        # Use st.components.v1.html to render the isolated HTML/JS
        st.components.v1.html(html_code, height=height + 50)

    except Exception as e:
        st.error(f"An error occurred while processing the image: {e}")
        st.warning("Please ensure the uploaded file is a valid image.")
else:
    st.info("Upload an image to activate the color sampler. Works best on images up to 600 pixels wide/high.")

st.markdown("---")
st.caption("Built with Streamlit, Pillow, and custom JavaScript.")
