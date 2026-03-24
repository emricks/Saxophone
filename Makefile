# Variables
DEST = /Volumes/CIRCUITPY/
SRC = src/

# Default target
deploy:
	@echo "Deploying to CircuitPython..."
	rsync -rtuv $(SRC) $(DEST)
	@echo "Deployment complete!"

# Install Python dependencies for local PyCharm autocomplete
deps:
	@echo "Installing CircuitPython stubs and hardware libraries..."
	pip install --upgrade pip
	pip install circuitpython-stubs adafruit-circuitpython-ili9341 adafruit-circuitpython-display-text
	@echo "Dependencies installed! (Make sure PyCharm's virtual environment is active)"