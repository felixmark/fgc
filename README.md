# Fancy Galaxy Code (FGC)
Fancy Galaxy Code (FGC) is an open source standard for fast and reliable data representation while maintaining a nice look and feel.  
FGC strifes to serve as a prettier QR-Code straight from the future.  
Contributions and integrations into projects are highly appreciated!  
  
## Links
[PyPI Package](https://pypi.org/project/fgc-tools/)  
[Online FGC Creator](https://ghostfox.de/fgc)  
  
## Specification

### Data processing
- 4 Version bits
- n Data + Hamming Code correction bits
- 1 end bit (can be cut away when decoded)


### Data representation
#### General structure
Center point is thick and has a distance d to the ring surrounding it.  
All of the rings have exactly distance d to every previous and next ring.  
The dot in the ring around it represents the orientation (0 degrees).  
The black dot in the outer ring is for orientation purposes as well. 

Every ring has an amount of n bits, calculated with: degree_per_bit = max(5, max(1, 20 / max(1, ring_number / 2)))  
That means the rings can store up to degree_per_bit - 1 bits, since the first bit of every layer is always a 0.  
  
#### Data representation
If the next bit is the same as this bit: Draw an arc  
If the next bit is not the same as this bit: Draw a dot  
  
Also:  
In the last layer there is an orientation point for easier orientation calculation, if it fits.  
It fits if the last layer has space for it.  
If it does not fit, it has to be placed in a seperate layer without any data.  
After the orientation point, the sequence starts with the normal non-data 0.  
  
#### Visual explanation
![Visual over on GitHub](./static/explanation.png)
  
## Code execution
Before execution you have to install the requirements by executing:  
```
pip install -r requirements.txt
```  
  
Execution:  
```
python3 fgc_tools_creator.py 'Content of fgc' outputfile.svg
```
  
## Use the fgc-tools package
Install the package via:
```sh
pip install fgc-tools
```

Import the FGCCreator class and create an fgc:
```python
from fgc_tools import FGCCreator

FGCCreator.create_fgc(data, output_file, color_start, color_end, background_color)
```  
  
## Example svg
![Visual over on GitHub](./static/example.svg)
