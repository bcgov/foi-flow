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
        elif key == "PAYOUTSTANDINGFULLPAYMENT":
            return "fee_payment_confirmation_outstanding.html"
        elif key == "OIPCAPPLICANTCONSENTEXTENSION":
            return "oipc_applicant_consent_time_extension.html"
        elif key == "OIPCFIRSTTIMEEXTENSION":
            return "oipc_first_time_extension.html"
        elif key == "OIPCSUBSEQUENTTIMEEXTENSION":
            return "oipc_subsequent_time_extension.html"
        else:
            logging.info("Unknown key")
            return None

    def getsubject(self, key, requestjson):        
        if key == "PAYONLINE" or key == "PAYOUTSTANDING" or key == "FEEESTIMATENOTIFICATION" or key == "OUTSTANDINGFEEESTIMATENOTIFICATION":
            return "Your FOI Request ["+requestjson["axisRequestId"]+"]"
        elif key == "FEE-ESTIMATE-PAYMENT-RECEIPT" or key == "OUTSTANDING-PAYMENT-RECEIPT":
            return "Your FOI Request ["+requestjson["axisRequestId"]+"] - Fee Payment Received"
        return "Your FOI Request ["+requestjson["axisRequestId"]+"]"   
        
    def getstage(self, key):        
        if key == "PAYONLINE" or key == "PAYOUTSTANDING":
            return "Fee Estimate"
        elif key == "FEE-ESTIMATE-PAYMENT-RECEIPT":  
            return "Fee Estimate - Payment Receipt"  
        elif key == "OUTSTANDING-PAYMENT-RECEIPT":
            return "Fees - Balance Outstanding - Payment Receipt"
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
            return "Fees - Balance Outstanding Sent"
        elif key == "PAYOUTSTANDING-SEND-FAILURE":
            return "Fees - Balance Outstanding Correspondence Failed"
        if key == "OUTSTANDING-PAYMENT-RECEIPT":
            return "Fees - Balance Outstanding - Payment Receipt Sent"
        elif key == "OUTSTANDING-PAYMENT-RECEIPT-FAILURE":
            return "Fees - Balance Outstanding - Payment Receipt Correspondence Failed"
        return None

    def getattachmentcategory(self, key):
        if key == "PAYONLINE" or key == "FEEESTIMATENOTIFICATION":
            return "FEEASSESSED-ONHOLD"
        elif key == "PAYONLINE-SUCCESSFUL" or key == "FEEESTIMATENOTIFICATION-SUCCESSFUL":
            return "Fee Estimate - Letter"
        elif key == "PAYONLINE-FAILED" or key == "FEEESTIMATENOTIFICATION-FAILED":
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
            return "Fee Balance Outstanding - Letter"
        elif key == "PAYOUTSTANDING-FAILED":
            return "Fee Balance Outstanding - Correspondence Failed"
        elif key == "OUTSTANDING-PAYMENT-RECEIPT":
            return "Fee Balance Outstanding - Payment Receipt"
        elif key == "OUTSTANDING-PAYMENT-RECEIPT-SUCCESSFUL":
            return "Fee Balance Outstanding - Payment Success"
        elif key == "OUTSTANDING-PAYMENT-RECEIPT-FAILED":
            return "Fee Balance Outstanding - Payment Success - Correspondence Failed"
        return None

    
    def isnotreceipt(self, key):
        if key == "FEE-ESTIMATE-PAYMENT-RECEIPT" or key == "OUTSTANDING-PAYMENT-RECEIPT":  
            return False
        return True
    

    
    