"""Testing paths."""

from inspect import getsourcefile
from os.path import abspath, exists
import json


path = '/'.join(abspath(getsourcefile(lambda:0)).split("/")[0:-1]) + "/"
# path = '/home/michal/dev/real-time-predictions-2022/2022/preparation/'

if exists(path + "settings.json"):
  with open(path + 'settings.json') as f:
    settings = json.load(f)
else:
  with open(path + 'default_settings.json') as f:
    settings = json.load(f) 
print(settings)