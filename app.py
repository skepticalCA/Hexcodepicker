import streamlit as st
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans

# Set the page configuration for a wider layout
st.set_page_config(layout="wide", page_title="Image Color Palette Extractor")

st.title("🎨 Image Color Palette Extractor")
st.markdown("Upload an image to extract its dominant colors and their hex codes.")

# Function to convert RGB to Hex code
def rgb_to_hex(rgb):
    """Converts an RGB tuple (0-255, 0-255, 0-255) to a hex string."""
    return f"#{int(rgb[0]):02x}{int(rgb[1]):02x}{int(rgb[2]):02x}".upper()

# Function to extract color palette using K-Means
def extract_color_palette(img, n_colors=10):
    # Resize image for faster processing (e.g., to 100x100)
    img = img.resize((100, 100))
    # Convert image to a flat array of RGB pixels
    pixels = np.array(img).reshape(-1, 3)
    
    # Run K-Means clustering
    kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
    kmeans.fit(pixels)
    
    # Get the dominant colors (cluster centers) and convert to integer RGB
    colors_rgb = kmeans.cluster_centers_.astype(int)
    
    # Convert RGB to Hex
    colors_hex = [rgb_to_hex(rgb) for rgb in colors_rgb]
    
    return colors_rgb, colors_hex

# --- Streamlit UI Components ---

uploaded_file = st.file_uploader(
    "Choose an image...", 
    type=["jpg", "jpeg", "png", "webp"],
    help="Upload a file (JPG, JPEG, PNG, or WEBP) to extract the color palette."
)

if uploaded_file is not None:
    try:
        # Open the image using PIL
        image = Image.open(uploaded_file)
        
        # Display the uploaded image
        st.subheader("Uploaded Image")
        st.image(image, caption="Source Image", use_column_width=True)
        
        # Sidebar for color selection
        st.sidebar.header("Settings")
        n_colors = st.sidebar.slider(
            "Number of Dominant Colors", 
            min_value=2, 
            max_value=20, 
            value=10, 
            step=1
        )
        
        st.sidebar.info("The colors are extracted using K-Means Clustering to find the most representative colors.")

        st.subheader(f"Extracted Color Palette ({n_colors} Colors)")
        
        # Extract the palette
        with st.spinner('Extracting colors...'):
            colors_rgb, colors_hex = extract_color_palette(image, n_colors)
        
        # Visually appealing display of the color palette
        
        # Create columns for the color swatches
        cols = st.columns(n_colors)
        
        # Display swatches and hex codes
        for i, hex_code in enumerate(colors_hex):
            with cols[i]:
                # 1. Color Swatch (using Streamlit's markdown with HTML/CSS)
                color_box_html = f"""
                <div style="
                    background-color: {hex_code};
                    height: 100px; 
                    border-radius: 10px;
                    border: 1px solid #ddd;
                    margin-bottom: 5px;
                "></div>
                """
                st.markdown(color_box_html, unsafe_allow_html=True)
                
                # 2. Hex Code
                st.markdown(
                    f"<p style='text-align: center; font-weight: bold; margin: 0;'>{hex_code}</p>", 
                    unsafe_allow_html=True
                )
                
                # 3. RGB Value (Optional)
                rgb_value = f"({colors_rgb[i][0]}, {colors_rgb[i][1]}, {colors_rgb[i][2]})"
                st.markdown(
                    f"<p style='text-align: center; font-size: small; color: #666;'>{rgb_value}</p>", 
                    unsafe_allow_html=True
                )

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.warning("Please ensure the uploaded file is a valid image.")
else:
    st.info("Please upload an image to generate the color palette.")

st.markdown("---")
st.caption("Built with Streamlit and scikit-learn (K-Means)")
