
import os
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

def add_watermark_to_image(image_path, watermark_text):
    """
    Adds a text watermark to an image.
    """
    try:
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        
        # Get image size
        width, height = image.size
        
        # Set font size (adjust as needed)
        font_size = int(width / 20)
        
        # Use a default font or specify a path to a .ttf file
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        # Calculate text size and position
        # Create a separate drawing context to measure text size
        temp_draw = ImageDraw.Draw(Image.new('RGB', (0, 0)))
        left, top, right, bottom = temp_draw.textbbox((0, 0), watermark_text, font=font)
        textwidth = right - left
        textheight = bottom - top
        
        x = width - textwidth - 10
        y = height - textheight - 10
        
        # Add watermark text with a semi-transparent background
        # Create a transparent overlay
        overlay = Image.new('RGBA', image.size, (255, 255, 255, 0))
        draw_overlay = ImageDraw.Draw(overlay)
        
        # Define background rectangle position and size
        rect_x0 = x - 5
        rect_y0 = y - 5
        rect_x1 = x + textwidth + 5
        rect_y1 = y + textheight + 5
        
        # Draw the semi-transparent background
        draw_overlay.rectangle([rect_x0, rect_y0, rect_x1, rect_y1], fill=(0, 0, 0, 128))
        
        # Composite the overlay with the original image
        image = Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
        
        # Re-create the draw object for the composited image
        draw = ImageDraw.Draw(image)

        # Add the text on top of the background
        draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255))
        
        # Save the watermarked image
        watermarked_path = os.path.splitext(image_path)[0] + "_watermarked.png"
        image.save(watermarked_path, "PNG")
        
        return watermarked_path
    except Exception as e:
        print(f"Error adding watermark to image: {e}")
        return None

def add_watermark_to_video(video_path, watermark_text):
    """
    Adds a text watermark to a video.
    """
    try:
        video_clip = VideoFileClip(video_path)
        
        # Create a text clip for the watermark
        txt_clip = TextClip(watermark_text, fontsize=50, color='white', bg_color='black')
        
        # Position the text clip at the bottom right
        txt_clip = txt_clip.set_position(('right', 'bottom')).set_duration(video_clip.duration)
        
        # Composite the video clip with the text clip
        video = CompositeVideoClip([video_clip, txt_clip])
        
        # Write the result to a new file
        watermarked_path = os.path.splitext(video_path)[0] + "_watermarked.mp4"
        video.write_videofile(watermarked_path, codec="libx264")
        
        return watermarked_path
    except Exception as e:
        print(f"Error adding watermark to video: {e}")
        return None

async def apply_watermark(file_path, watermark_text):
    """
    Applies a watermark to an image or video file.
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext in ['.jpg', '.jpeg', '.png']:
        return add_watermark_to_image(file_path, watermark_text)
    elif file_ext in ['.mp4', '.avi', '.mov', '.mkv']:
        return add_watermark_to_video(file_path, watermark_text)
    else:
        # Unsupported file type
        return file_path
