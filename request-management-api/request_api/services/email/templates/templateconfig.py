import json

class templateconfig:
    """This class is reserved for consolidating all templates 
    """
    
    def gettemplatename(self, key):        
        if key == "PAYONLINE":
            return "fee_estimate_default.html"
        return None
    

    
    