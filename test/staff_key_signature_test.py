import displayio
import sys,os

# Add the project root to the Python path so we can import 'composer'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from composer.staff import Staff
from composer.key_signature import KeySignatures
from display_utils import prep_display, show_and_wait
from data.config import Config

def test_staff_key_signature():
    # 1. Get a standard configuration containing color profiles
    config = Config()

    # 2. Prepare display
    display = prep_display(config=config)

    # 3. Create a KeySignature
    #key_sig = KeySignatures.C_SHARP_MAJOR
    key_sig = KeySignatures.C_FLAT_MAJOR

    # 4. Create the Staff object, passing the key signature
    staff = Staff(width=160, config=config, key_signature=key_sig)

    # Center the staff vertically
    staff.y = (200 - Staff.HEIGHT) // 2

    # 5. Mount it on the display
    if isinstance(display.root_group, displayio.Group):
        display.root_group.append(staff)
    else:
        main_group = displayio.Group()
        main_group.append(staff)
        display.root_group = main_group

    # 6. View it
    show_and_wait(display)

if __name__ == "__main__":
    test_staff_key_signature()