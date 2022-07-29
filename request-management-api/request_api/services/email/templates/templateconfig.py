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
        
    def getstage(self, key):        
        if key == "PAYONLINE":
            return "Fee Estimate"
        return None 
    
    def getattachmentname(self, key):
        if key == "PAYONLINE":
            return "Fees - Estimate Sent"
        elif key == "PAYONLINE-SEND-FAILURE":
            return "Fees - Estimate Correspondence Failed"
        return None

    def getattachmentcategory(self, key):
        if key == "FEE-ESTIMATE-LETTER":
            return "Fee Estimate - Letter"
        elif key == "FEE-ESTIMATE-SUCCESSFUL":
            return "Fee Estimate - Successful"
        elif key == "FEE-ESTIMATE-FAILED":
            return "Fee Estimate - Failed"
        return None 
    

    
    