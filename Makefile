# Variables
DEST = /Volumes/CIRCUITPY/
SRC = src/

# Default target
deploy:
	@echo "Deploying to CircuitPython..."
	rsync -rtuv $(SRC) $(DEST)
	@echo "Deployment complete!"