import json

class templateconfig:
    """This class is reserved for consolidating all templates 
    """
    
    def gettemplatename(self, key):        
        if key == "PAYONLINE":
            return "fee_estimate_default.html"
        return None

    def getsubject(self, key, requestjson):        
        if key == "PAYONLINE":
            return "Your FOI Request ["+requestjson["axisRequestId"]+"]"
        return None      
    
    def getattachmentname(self, key):
        if key == "PAYONLINE":
            return "Fees - Estimate Sent"
        elif key == "PAYONLINE-SEND-FAILURE":
            return "Fees - Estimate Correspondence Failed"
        return None 
    

    
    