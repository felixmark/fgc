# Fancy Galaxy Code (FGC)
Fancy Galaxy Code (FGC) strifes to serve as the new and prettier QR Code straight from the future.  
Contributions are highly appreciated!

## Specification

### Data processing
- 1 Starting bit (always 0)
- 4 Version bits
- n Data + Correction bits
- 1 End bit (always 0)
  
All data gets inversed at the end, so all 0s turn into 1s and thus into dots in the final Code.


### Data representation
#### General structure
Center point is thick and has a distance d to the ring surrounding it.  
All of the rings have exactly distance d to every previous and next ring.  
The dot in the ring around it represents the orientation (0 degrees).  
The black dot in the outer ring is for orientation purposes as well. 

Every ring has an amount of 1 bit per 45° / # of ring with a minimum of 4 degrees per bit.  
I.e. that means the first ring can store up to 8 bits, the second one 16 and so forth.

#### Data representation
If the next bit is the same as this bit: Draw an arc  
If the next bit is not the same as this bit: Draw a dot  
  
Also:  
In the last layer there is an orientation Point for easier orientation calculation, if it fits.  
It fits if the last layer has space for it plus some space around it.  
If it does not fit, it has to be placed in a seperate layer without any data.  
  
### Example svg
![Alt text](./static/example.svg)
