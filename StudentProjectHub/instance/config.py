# Optional local overrides.
#
# This app is configured primarily through environment variables loaded from
# `.env` (see config.py). This file exists to follow Flask's instance-folder
# convention and as a place to drop machine-specific secrets that should
# never be committed to version control - it is not loaded automatically.
#
# If you want to use it, load it from config.py with:
#   app.config.from_pyfile("config.py", silent=True)

# Example:
# SECRET_KEY = "a-different-secret-for-this-machine"
