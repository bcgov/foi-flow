from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestInvoices import FOIRequestInvoices
from .document_generation_service import DocumentGenerationService
from request_api.auth import AuthHelper
from datetime import datetime as datetime2

INVOICE_MEMO = "You have 20 business days to respond to this fee statement or your file will be closed as Abandoned. If the total estimate is over $200 you are only required to pay a 50% deposit, otherwise you are required to pay the full amount."

class foiinvoiceservice:
    def get_invoice(self, foicfrfeedid):
        pass
    
    def generate_invoice(self, invoice, feedata):
        try:
            foiministryrequest = FOIMinistryRequest.getrequest(feedata.ministryrequestid)
            invoice_date = datetime2.now()
            filename = f"Fee Invoice - {foiministryrequest.axisrequestid}"
            current_invoiceid = FOIRequestInvoices.getcurrentinvoiceid()
            invoice_template_data = {
                "invoice_num": f"{(current_invoiceid+1):10d}",
                "invoice_date": invoice_date.strftime("%B %d, %Y"),
                "request_description": foiministryrequest.description,
                "cfrfee": feedata,
                "axisRequestId": foiministryrequest.axisrequestid,
                "applicant_name": invoice["applicant_name"],
                "applicant_address": invoice["applicant_address"],
                "invoice_memo": INVOICE_MEMO,
            }
            document_service : DocumentGenerationService = DocumentGenerationService("cfr_fee_invoice")
            basepath = 'request_api/receipt_templates/'
            created_invoice = document_service.generate_receipt(invoice_template_data, basepath+document_service.documenttypename+".docx")
            response = document_service.upload_receipt(filename, created_invoice.content, foiministryrequest.foiministryrequestid, foiministryrequest.programarea.name, foiministryrequest.axisRequestId, "FEE-INVOICE")
            if response is not None and response['success']:
                invoice["foirequestcfrfee_id"] = feedata.cfrfeeid
                invoice["foicfrefeeversion_id"] = feedata.version
                invoice["filename"] = filename
                invoice["documentpath"] = response['documentpath']
                invoice["created_at"] = invoice_date
                return FOIRequestInvoices.save_invoice(invoice)
        except Exception as exeception:
            raise exeception