import sys
import os

# Add the project root to the Python path so we can import 'composer'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from composer.staff import Staff
from display_utils import prep_display, show_and_wait
from data.config import Config

def test_staff_static_lines():
    # 1. Get a standard configuration containing color profiles
    config = Config()

    # 2. Prepare display, passing the config so the entire display background is colored
    display = prep_display(config=config)

    # 3. Create the Staff object (which inherits from displayio.Group)
    staff = Staff(width=160, config=config)
    
    # Let's center the staff vertically on the 200px tall display just so it looks nice
    staff.y = (display.height - staff.height) // 2
    staff.x = (display.width - staff.width) // 2
    
    display.root_group.append(staff)

    # 5. View it
    show_and_wait(display)

if __name__ == "__main__":
    test_staff_static_lines()
