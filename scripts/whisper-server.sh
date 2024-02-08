#!/bin/bash
source "$(dirname "\$0")/bin/activate"
python "$(dirname "\$0")/src/main.py" "$@"
