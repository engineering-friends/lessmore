from PIL import Image, ImageDraw, ImageFont


def create_image_with_text(text, image_size=(400, 200), font_size=20):
    # Create an image with a white background
    image = Image.new("RGB", image_size, "white")
    draw = ImageDraw.Draw(image)

    # Use a default font
    font = ImageFont.load_default()

    # Calculate text width and height
    text_width, text_height = draw.textsize(text, font=font)

    # Calculate the position for the text to be centered
    text_x = (image_size[0] - text_width) / 2
    text_y = (image_size[1] - text_height) / 2

    # Add the text to the image
    draw.text((text_x, text_y), text, fill="black", font=font)

    # Save the image
    image.save("text_image.png")


# Example usage
create_image_with_text("Hello, World!")
