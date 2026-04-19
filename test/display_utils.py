import os
import time

def prep_display(width=320, height=200):
    """
    Initializes a fake display using PyGame for testing CircuitPython displayio code.
    Sets up the required environment variables and returns the display object.
    """
    os.environ["BLINKA_PYGAMEDISPLAY"] = "1"
    os.environ["BLINKA_DISPLAYIO_MACROS"] = "1"

    import displayio
    from blinka_displayio_pygamedisplay import PyGameDisplay

    displayio.release_displays()

    # The auto_refresh parameter is essential for PyGameDisplay to automatically pump frames 
    display = PyGameDisplay(width=width, height=height, auto_refresh=True)
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
