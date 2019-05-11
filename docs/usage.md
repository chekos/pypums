Usage
=====

To use pypums in a project:

```python
from pypums import ACS
```
```python
acs = ACS(state = 'California', year = 2012,)
```
```python
acs.download_data()
```