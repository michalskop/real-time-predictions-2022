"""Settings."""

def get_settings():
  """Get settings."""
  return {
    'name': 'My App',
    'version': '1.0',
    'author': 'John Doe',
    'path': '/'.join(abspath(getsourcefile(lambda:0)).split("/")[0:-1]) + "/"
  }
