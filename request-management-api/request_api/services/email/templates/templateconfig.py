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
        elif key == "PAYOUTSTANDING":
            return "fee_estimate_notification_outstanding.html"
        else:
            logging.info("Unknown key")
            return None
        return None

    def getsubject(self, key, requestjson):        
        if key == "PAYONLINE":
            return "Your FOI Request ["+requestjson["axisRequestId"]+"]"
        elif key == "FEE-ESTIMATE-PAYMENT-RECEIPT":
            return "Your FOI Request ["+requestjson["axisRequestId"]+"] - Fee Payment Received"
        elif key == "PAYOUTSTANDING":
            return "Your FOI Request ["+requestjson["axisRequestId"]+"] - Outstanding Fee Estimate"
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
        elif key == "PAYOUTSTANDING":
            return "Fees - Estimate Outstanding Sent"
        elif key == "PAYOUTSTANDING-SEND-FAILURE":
            return "Fees - Estimate Outstanding Correspondence Failed"
        return None

    def getattachmentcategory(self, key):
        if key == "PAYONLINE":
            return "FEEASSESSED-ONHOLD"
        elif key == "PAYONLINE-SUCCESSFUL":
            return "Fee Estimate - Letter"
        elif key == "PAYONLINE-FAILED":
            return "Fee Estimate - Correspondence Failed"
        elif key == "FEE-ESTIMATE-PAYMENT-RECEIPT":
            return "Fee Estimate - Payment Receipt"
        elif key == "FEE-ESTIMATE-PAYMENT-RECEIPT-SUCCESSFUL":
            return "Fee Estimate - Payment Success"
        elif key == "FEE-ESTIMATE-PAYMENT-RECEIPT-FAILED":
            return "Fee Estimate - Payment Success - Correspondence Failed"
        elif key == "PAYOUTSTANDING":
            return "RESPONSE-ONHOLD"
        elif key == "PAYOUTSTANDING-SUCCESSFUL":
            return "Fee Estimate Outstanding - Letter"
        elif key == "PAYOUTSTANDING-FAILED":
            return "Fee Estimate Outstanding - Correspondence Failed"
        return None 
    

    
    