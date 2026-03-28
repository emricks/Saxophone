# Variables
DEST = /Volumes/CIRCUITPY/


# Default target
deploy:
	@echo "Deploying to CircuitPython..."
	rsync -rtuv hardware data states $(DEST)
	rsync -rtuv code.py $(DEST)
	@echo "Deployment complete!"

# Install Python dependencies for local PyCharm autocomplete
deps:
	@echo "Installing CircuitPython stubs and hardware libraries..."
	pip install --upgrade pip
	pip install circuitpython-stubs adafruit-circuitpython-ili9341 adafruit-circuitpython-mcp230xx adafruit-circuitpython-imageload adafruit-circuitpython-display-text circup
	@echo "Dependencies installed! (Make sure PyCharm's virtual environment is active)"

setup-device: deps
	@echo "Installing libraries to device"
	circup install asyncio adafruit_display_text adafruit_ili9341 adafruit_mcp230xx adafruit_imageload