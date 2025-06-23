import streamlit as st
import numpy as np
from PIL import Image, ImageDraw
import io
import random
import base64

# Set page config
st.set_page_config(page_title="Photo Collage Maker", layout="wide")

# Initialize session state
if 'images' not in st.session_state:
    st.session_state.images = []
if 'rotations' not in st.session_state:
    st.session_state.rotations = []
if 'collage' not in st.session_state:
    st.session_state.collage = None

# Common image size proportions (width x height in pixels at 300 DPI)
size_options = {
    "4x6 Portrait": (1200, 1800),
    "5x7 Portrait": (1500, 2520),
    "8x10 Portrait": (2400, 3000),
    "6x4 Landscape": (1800, 1200),
    "7x5 Landscape": (2100, 2100),
    "10x8 Landscape": (3000, 2400)
}

def create_collage(images, rotations, size, bg_color, gap=50):
    """Create a collage from images with specified size, background color."""
    width, height = size
    bg_rgb = (255, 255, 255) if bg_color == "White" else (0, 0, 0)
    collage = Image.new('RGB', (width, height), bg_rgb)
    
    if not images:
        return collage
    
    # Calculate thumbnail size (assuming max 4 images per row for simplicity)
    thumb_width = (width - gap * 5) // 4
    thumb_height = (height - gap * 5) // 4
    positions = []
    
    # Generate random positions
    for _ in range(len(images)):
        x = random.randint(gap, width - thumb_width - gap)
        y = random.randint(gap, height - thumb_height - gap)
        positions.append((x, y))
    
    # Paste images
    for img, rot, (x, y) in zip(images, rotations, positions):
        thumb = img.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
        if rot != 0:
            thumb = thumb.rotate(rot, expand=True)
        collage.paste(thumb, (x, y), thumb if thumb.mode == 'RGBA' else None)
    
    return collage

def image_to_base64(img):
    """Convert PIL image to base64 string for download."""
    buffered = io.BytesIO()
    img.save(buffered, format="PNG", dpi=(300, 300))
    return base64.b64encode(buffered.getvalue()).decode()

# App title
st.title("Photo Collage Maker")

# Sidebar for configuration
with st.sidebar:
    st.header("Collage Settings")
    
    # Size selection
    size_choice = st.selectbox("Select Image Size", list(size_options.keys()))
    size = size_options[size_choice]
    
    # Background color
    bg_color = st.radio("Background Color", ["White", "Black"])
    
    # Image upload
    uploaded_files = st.file_uploader("Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    if uploaded_files:
        for file in uploaded_files:
            img = Image.open(file).convert('RGBA')
            st.session_state.images.append(img)
            st.session_state.rotations.append(0)
    
    # Number of images to use
    num_images = st.slider("Number of Images to Use", 1, len(st.session_state.images), len(st.session_state.images))
    
    # Remove images
    if st.session_state.images:
        st.subheader("Remove Images")
        for i, img in enumerate(st.session_state.images[:num_images]):
            if st.button(f"Remove Image {i+1}", key=f"remove_{i}"):
                st.session_state.images.pop(i)
                st.session_state.rotations.pop(i)
                st.rerun()

# Main area
st.header("Image Rotation")
if st.session_state.images:
    cols = st.columns(min(num_images, 4))
    for i, (col, img) in enumerate(zip(cols, st.session_state.images[:num_images])):
        with col:
            st.image(img, caption=f"Image {i+1}", width=100)
            rotation = st.slider(f"Rotate Image {i+1} (degrees)", -180, 180, st.session_state.rotations[i], step=45, key=f"rot_{i}")
            st.session_state.rotations[i] = rotation

# Rearrange button
if st.button("Rearrange Collage"):
    st.session_state.collage = create_collage(st.session_state.images[:num_images], st.session_state.rotations[:num_images], size, bg_color)

# Generate initial collage
if st.session_state.images and not st.session_state.collage:
    st.session_state.collage = create_collage(st.session_state.images[:num_images], st.session_state.rotations[:num_images], size, bg_color)

# Display preview
if st.session_state.collage:
    st.header("Collage Preview")
    st.image(st.session_state.collage, caption="Preview", use_column_width=True)
    
    # Download button
    b64_str = image_to_base64(st.session_state.collage)
    href = f'<a href="data:image/png;base64,{b64_str}" download="collage.png">Download Collage</a>'
    st.markdown(href, unsafe_allow_html=True)
else:
    st.info("Upload images to start creating your collage.")
