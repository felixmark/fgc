from .commonconstants import CommonConstants

class CommonFunctions():
    
    @staticmethod
    def get_degrees_per_bit(ring_number): 
        if ring_number <= len(CommonConstants.DEGREES_PER_BIT):
            return CommonConstants.DEGREES_PER_BIT[ring_number-1]
        return 3

    @staticmethod
    def print_seperation_line(character):
        print(character * 80)