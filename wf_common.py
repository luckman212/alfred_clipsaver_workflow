"""
Common Functions, Vars, Constants
"""

import os
import time

def envvar(v: str, dv: str) -> str:
  return str(os.getenv(v) or dv)

#for checkboxes - unchecked aka `0` returns `false`
def envvar_to_bool(v: str) -> str:
  raw_val = os.getenv(v)
  
  # Handle both '1'/'0' and 'true'/'false' strings
  if raw_val is None:
    b = 0
  elif raw_val.lower() in ('true', '1', 'yes'):
    b = 1
  elif raw_val.lower() in ('false', '0', 'no', ''):
    b = 0
  else:
    # Try to parse as integer
    try:
      b = int(raw_val)
    except:
      b = 0
  
  result = str(bool(b)).lower()
  return result

def envvar_to_int(v: str, dv: int=0) -> int:
  try:
    return int(os.getenv(v))
  except:
    pass
  try:
    return int(dv)
  except:
    return 0

#wf vars
db_name = envvar('db_name', 'clipboard.alfdb')
db_path = os.path.expanduser(envvar('db_path', '~/Library/Application Support/Alfred/Databases'))
dest_dir = os.path.expanduser(envvar('dest_dir', '~/Desktop/saved_clips')).lower()
default_format = envvar('default_format', 'png').lower()
delete_after_convert = envvar_to_bool('delete_after_convert')
save_to_current = envvar_to_bool('save_to_current')
sf_clip_limit = envvar_to_int('sf_clip_limit', -1)

#home_path = os.getenv('HOME')
db_res = os.path.join(db_path, db_name)
i_path = f'{db_res}.data'
uidSeed = str(os.getenv('uidSeed', time.time()))
img_exts = [ 'png', 'gif', 'jpg', 'jpeg', 'tiff', 'tif', 'bmp' ]
