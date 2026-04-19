import displayio
import terminalio
from adafruit_display_text import label
from display_utils import prep_display, show_and_wait

def test_blue_hello_screen():
    # 1. Prepare our fake display
    display = prep_display(width=320, height=200)

    # 2. Set up standard displayio components
    main_group = displayio.Group()
    display.root_group = main_group

    bg_bitmap = displayio.Bitmap(320, 200, 1)
    
    bg_palette = displayio.Palette(1)
    bg_palette[0] = 0x0000FF
    
    bg_tilegrid = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette, x=0, y=0)
    main_group.append(bg_tilegrid)

    text_area = label.Label(
        terminalio.FONT, 
        text="hello", 
        color=0xFFFFFF,
        scale=3 
    )
    
    text_area.x = 100
    text_area.y = 100
    
    main_group.append(text_area)

    # 3. Block and show the image on the screen
    show_and_wait(display)

if __name__ == "__main__":
    test_blue_hello_screen()
