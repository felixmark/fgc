# Fancy Galaxy Code (FGC)
Fancy Galaxy Code (FGC) strifes to serve as the new and prettier QR Code straight from the future.  
Contributions are highly appreciated!

## Specification

### Data processing
- 2 Bits Error Correction selection
- 4 Bits Version Code
- n Bits data which is XORed in error correction intervals
- 0 End bit

All data gets inversed at the end, so all 0s turn into 1s and thus into dots in the final Code.


### Data representation
Center point is thick and has a distance d to the ring surrounding it.
The dot in the ring around it represents the orientation (0 degrees).
All of the rings have exactly distance d to every previous and next ring.

Every ring has aan amount of 1 bit per 30° / # of ring with a minimum of 4 degrees per bit.
I.e. that means the first ring can store up to 12 bits, the second one 24 and so forth.

### Example svg
![Alt text](./fgc.svg)
