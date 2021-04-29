exec-wrapper
===

Allows creating executable wrappers for any executable.
Tested on Linux, Windows.

Example
---
```python
import os
import subprocess
from exec_wrapper import write_exec_wrapper

wrapper = '/tmp/ssh-wrapper'
write_exec_wrapper(wrapper, ['ssh', '-i', 'my-key', '-o', 'BatchMode=yes'])

subprocess.run(['git', 'fetch', '...'], env={**os.environ, 'GIT_SSH': wrapper})
```
