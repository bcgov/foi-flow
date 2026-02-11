from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestInvoices import FOIRequestInvoices
from .document_generation_service import DocumentGenerationService
from request_api.auth import AuthHelper
from datetime import datetime as datetime2

INVOICE_MEMO = "You have 20 business days to respond to this fee statement or your file will be closed as Abandoned. If the total estimate is over $200 you are only required to pay a 50% deposit, otherwise you are required to pay the full amount."
OUTSTANDING_INVOICE_MEMO = "You have 20 business days to respond to this fee statement or your file will be closed as Abandoned."

class foiinvoiceservice:
    def generate_invoice(self, invoice, userid):
        try:
            cfrdata = invoice["cfrfeedata"]
            invoice["created_at"] = datetime2.now()
            foiministryrequest = FOIMinistryRequest.getrequest(cfrdata["ministryrequestid"])
            current_invoiceid = FOIRequestInvoices.getcurrentinvoiceid().invoiceid if FOIRequestInvoices.getcurrentinvoiceid() is not None else 0
            filename = f"Invoice-{(current_invoiceid+1):010d}-{foiministryrequest['axisrequestid']}.pdf"
            invoice_template_data = self.__prepare_invoice_data(cfrdata["feedata"], foiministryrequest, invoice, current_invoiceid)
            document_service : DocumentGenerationService = DocumentGenerationService("cfr_fee_invoice")
            basepath = 'request_api/receipt_templates/'
            created_invoice = document_service.generate_receipt(invoice_template_data, basepath+document_service.documenttypename+".docx")
            response = document_service.upload_receipt(filename, created_invoice.content, foiministryrequest['foiministryrequestid'], foiministryrequest["programarea.bcgovcode"], foiministryrequest['axisrequestid'], "FEE-INVOICE")
            if response is not None and response['success']:
                invoice["filename"] = filename
                invoice["documentpath"] = response['documentpath']
                return FOIRequestInvoices.save_invoice(invoice, userid)
        except Exception:
            raise
    
    def __prepare_invoice_data(self, feedata, foiministryrequest, invoice, current_invoiceid):
        is_actual_hours = feedata['actualtotaldue'] > 0
        estimated_waived_amt = feedata['estimatedlocatinghrs'] * 30 if feedata['estimatedlocatinghrs'] < 3 else 90
        actual_waived_amt = feedata['actuallocatinghrs'] * 30 if feedata['actuallocatinghrs'] < 3 else 90
        return {
            "invoice_num": f"{(current_invoiceid+1):010d}",
            "invoice_date": invoice["created_at"].strftime("%B %d, %Y"),
            "request_description": foiministryrequest['description'],
            "balancedue": f"{float(feedata['balanceremaining']):.2f}",
            "amountpaid": f"{float(feedata['amountpaid']):.2f}",
            "axisRequestId": foiministryrequest['axisrequestid'],
            "applicant_name": invoice["applicant_name"],
            "applicant_address": invoice["applicant_address"],
            "invoice_memo": OUTSTANDING_INVOICE_MEMO if is_actual_hours else INVOICE_MEMO,
            "waivedAmount": estimated_waived_amt if not is_actual_hours else actual_waived_amt,
            "locatinghrs": feedata["actuallocatinghrs"] if is_actual_hours else feedata["estimatedlocatinghrs"],
            "producinghrs": feedata["actualproducinghrs"] if is_actual_hours else feedata["estimatedproducinghrs"],
            "iaopreparinghrs": feedata["actualiaopreparinghrs"] if is_actual_hours else feedata["estimatediaopreparinghrs"],
            "ministrypreparinghrs": feedata["actualministrypreparinghrs"] if is_actual_hours else feedata["estimatedministrypreparinghrs"],
            "hardcopypages": feedata["actualhardcopypages"] if is_actual_hours else feedata["estimatedhardcopypages"],
            "totaldue": feedata["actualtotaldue"] if is_actual_hours else feedata["estimatedtotaldue"],
            "addWaivedAmount": f"{float(feedata['feewaiveramount']):.2f}",
        }