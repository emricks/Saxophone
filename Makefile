# Variables
DEST = /Volumes/CIRCUITPY/


# Default target
deploy:
	@echo "Deploying to CircuitPython..."
	rsync -rtv --exclude='.DS_Store' --exclude='__pycache__' hardware composer data states songs $(DEST)
	rsync -rtv code.py boot.py $(DEST)
	@echo "Deployment complete!"

# Install Python dependencies for local PyCharm autocomplete
deps:
	@echo "Installing CircuitPython stubs and hardware libraries..."
	pip install --upgrade pip
	pip install circuitpython-stubs adafruit-circuitpython-ili9341 adafruit-circuitpython-mcp230xx blinka-displayio-pygamedisplay adafruit-circuitpython-imageload adafruit-circuitpython-display-text adafruit-circuitpython-bmp3xx circup
	@echo "Dependencies installed! (Make sure PyCharm's virtual environment is active)"

setup-device: deps
	@echo "Installing libraries to device"
	circup install asyncio adafruit_display_text adafruit_ili9341 adafruit_mcp230xx adafruit_imageload adafruit_bmp3xx