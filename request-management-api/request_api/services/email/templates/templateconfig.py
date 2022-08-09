import json
import logging

class templateconfig:
    """This class is reserved for consolidating all templates 
    """
    
    def gettemplatename(self, key):        
        if key == "PAYONLINE":
            return "fee_estimate_notification.html"
        elif key == "HALFPAYMENT":
            return "fee_payment_confirmation_half.html"
        elif key == "FULLPAYMENT":
            return "fee_payment_confirmation_full.html"
        else:
            logging.info("Unknown key")
            return None
        return None

    def getsubject(self, key, requestjson):        
        if key == "PAYONLINE":
            return "Your FOI Request ["+requestjson["axisRequestId"]+"]"
        elif key == "FEE-ESTIMATE-PAYMENT-RECEIPT":
            return "Your FOI Request ["+requestjson["axisRequestId"]+"] - Fee Payment Received"
        return None   
        
    def getstage(self, key):        
        if key == "PAYONLINE":
            return "Fee Estimate"
        elif key == "FEE-ESTIMATE-PAYMENT-RECEIPT":  
            return "Fee Estimate - Payment Receipt"  
        return None 
    
    def getattachmentname(self, key):
        if key == "PAYONLINE":
            return "Fees - Estimate Sent"
        elif key == "PAYONLINE-SEND-FAILURE":
            return "Fees - Estimate Correspondence Failed"
        if key == "FEE-ESTIMATE-PAYMENT-RECEIPT":
            return "Fee Estimate - Payment Receipt Sent"
        elif key == "FEE-ESTIMATE-PAYMENT-RECEIPT-FAILURE":
            return "Fee Estimate - Payment Receipt Correspondence Failed"
        return None

    def getattachmentcategory(self, key):
        if key == "PAYONLINE":
            return "Fee Estimate - Letter"
        elif key == "PAYONLINE-SUCCESSFUL":
            return "Fee Estimate - Correspondence - Successful"
        elif key == "PAYONLINE-FAILED":
            return "Fee Estimate - Correspondence - Failed"
        elif key == "FEE-ESTIMATE-PAYMENT-RECEIPT":
            return "Fee Estimate - Payment Receipt"
        elif key == "FEE-ESTIMATE-PAYMENT-RECEIPT-SUCCESSFUL":
            return "Fee Estimate - Payment - Correspondence - Successful"
        elif key == "FEE-ESTIMATE-PAYMENT-RECEIPT-FAILED":
            return "Fee Estimate - Payment - Correspondence - Failed"
        return None 
    

    
    