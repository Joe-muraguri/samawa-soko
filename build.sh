#!/bin/bash

# Step 1: Install dependencies
pip install -r requirements.txt

# Step 2: Run database migrations
flask db upgrade