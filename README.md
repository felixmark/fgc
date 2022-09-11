# Fancy Galaxy Code (FGC)
Fancy Galaxy Code (FGC) strifes to serve as the new and prettier QR Code straight from the future.  
Contributions are highly appreciated!

## Specification

### Data processing
- 4 Version bits
- n Data + Correction bits


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
In the last layer there is an orientation Point for easier orientation calculation, if it fits.  
It fits if the last layer has space for it.  
If it does not fit, it has to be placed in a seperate layer without any data.  
  
### Example svg
![Alt text](./static/example.svg)
