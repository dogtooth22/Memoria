# Makefile for Python project

# Variables
PYTHON = python3
SRC_DIR = src
SRC_FILES = $(wildcard /*.py)
TXT_FILES = $(wildcard instancias/*.txt)
FILE = instancias/InstanceBEP-$(instance)_$(v).txt
MAIN_FILE = main.py

# Default target
all: run

# Build target
build:
	@echo "Building the project..."

# Run target
run:
	@for file in $(TXT_FILES); do \
		if [ "$$file" = "$(FILE)" ]; then \
			echo "Reading $$file..."; \
			echo $(PYTHON) $(MAIN_FILE) $(i) $(alpha) $(beta) $(decay) $(q) $$file; \
			$(PYTHON) $(MAIN_FILE) $(i) $(alpha) $(beta) $(decay) $(q) $$file; \
		fi; \
	done

# Clean target
clean:
	@echo "Cleaning up..."
	@rm -rf $(SRC_DIR)/*.pyc

# Phony targets
.PHONY: all build run clean