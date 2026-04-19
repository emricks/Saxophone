import os
import time

def prep_display(width=320, height=200, config=None):
    """
    Initializes a fake display using PyGame for testing CircuitPython displayio code.
    Sets up the required environment variables and returns the display object.
    
    If config is provided, it sets the background color of the display
    to match config.color_data.bg_color.
    """
    os.environ["BLINKA_PYGAMEDISPLAY"] = "1"
    os.environ["BLINKA_DISPLAYIO_MACROS"] = "1"

    import displayio
    from blinka_displayio_pygamedisplay import PyGameDisplay

    displayio.release_displays()

    # The auto_refresh parameter is essential for PyGameDisplay to automatically pump frames 
    display = PyGameDisplay(width=width, height=height, auto_refresh=True)
    
    if config:
        # Create a base group to act as the solid background color
        bg_group = displayio.Group()
        display.root_group = bg_group
        
        bg_bitmap = displayio.Bitmap(width, height, 1)
        bg_palette = displayio.Palette(1)
        bg_palette[0] = config.color_data.bg_color
        
        bg_grid = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette, x=0, y=0)
        bg_group.append(bg_grid)

    return display

def show_and_wait(display):
    """
    Keeps the PyGame window open until the user closes it or presses Ctrl+C.
    Useful for visually verifying test output.
    """
    import pygame
    
    print("Displaying image... close the PyGame window or press Ctrl+C to exit.")
    try:
        while True:
            # We can use PyGame's standard event loop pump so the window doesn't freeze
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            
            # Explicitly tell the Blinka display to refresh if it hasn't
            display.refresh()
            time.sleep(0.01)
    except KeyboardInterrupt:
        pygame.quit()
        pass

def save_to_image(display, filename):
    """
    Forces a display refresh and saves the current screen buffer to an image file.
    Great for automated assertions without keeping a window open.
    """
    import pygame
    display.refresh()
    # The internal PyGame surface is accessible via _pygame_screen
    pygame.image.save(display._pygame_screen, filename)
    print(f"Saved display output to {filename}")
