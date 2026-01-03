from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestInvoices import FOIRequestInvoices
from .document_generation_service import DocumentGenerationService
from request_api.auth import AuthHelper
from datetime import datetime as datetime2

INVOICE_MEMO = "You have 20 business days to respond to this fee statement or your file will be closed as Abandoned. If the total estimate is over $200 you are only required to pay a 50% deposit, otherwise you are required to pay the full amount."

class foiinvoiceservice:
    def get_invoice(self, foicfrfeeid):
        pass
    
    def generate_invoice(self, invoice, cfrdata, foicfrfeeid, userid):
        try:
            print("FINAL", cfrdata)
            print("inv", invoice)
            feedata = cfrdata["feedata"]
            is_actual_hours = feedata['actualtotaldue'] > 0
            foiministryrequest = FOIMinistryRequest.getrequest(cfrdata["ministryrequestid"])
            invoice_date = datetime2.now()
            current_invoiceid = FOIRequestInvoices.getcurrentinvoiceid().invoiceid if FOIRequestInvoices.getcurrentinvoiceid() is not None else 0
            filename = f"Invoice-{(current_invoiceid+1):010d}-{foiministryrequest['axisrequestid']}.pdf"
            estimated_waived_amt = feedata['estimatedlocatinghrs'] * 30 if feedata['estimatedlocatinghrs'] < 3 else 90
            actual_waived_amt = feedata['actuallocatinghrs'] * 30 if feedata['actuallocatinghrs'] < 3 else 90
            invoice_template_data = {
                "invoice_num": f"{(current_invoiceid+1):010d}",
                "invoice_date": invoice_date.strftime("%B %d, %Y"),
                "request_description": foiministryrequest['description'],
                "balancedue": f"{float(feedata['balanceremaining']):.2f}",
                "amountpaid": f"{float(feedata['amountpaid']):.2f}",
                "axisRequestId": foiministryrequest['axisrequestid'],
                "applicant_name": invoice["applicant_name"],
                "applicant_address": invoice["applicant_address"],
                "invoice_memo": INVOICE_MEMO,
                "waivedAmount": estimated_waived_amt if not is_actual_hours else actual_waived_amt,
                "locatinghrs": feedata["actuallocatinghrs"] if is_actual_hours else feedata["estimatedlocatinghrs"],
                "producinghrs": feedata["actualproducinghrs"] if is_actual_hours else feedata["estimatedproducinghrs"],
                "iaopreparinghrs": feedata["actualiaopreparinghrs"] if is_actual_hours else feedata["estimatediaopreparinghrs"],
                "ministrypreparinghrs": feedata["actualministrypreparinghrs"] if is_actual_hours else feedata["estimatedministrypreparinghrs"],
                "hardcopypages": feedata["actualhardcopypages"] if is_actual_hours else feedata["estimatedhardcopypages"],
                "totaldue": feedata["actualtotaldue"] if is_actual_hours else feedata["estimatedtotaldue"],
            }
            document_service : DocumentGenerationService = DocumentGenerationService("cfr_fee_invoice")
            basepath = 'request_api/receipt_templates/'
            created_invoice = document_service.generate_receipt(invoice_template_data, basepath+document_service.documenttypename+".docx")
            response = document_service.upload_receipt(filename, created_invoice.content, foiministryrequest['foiministryrequestid'], foiministryrequest["programarea.bcgovcode"], foiministryrequest['axisrequestid'], "FEE-INVOICE")
            if response is not None and response['success']:
                invoice["foirequestcfrfee_id"] = foicfrfeeid
                invoice["foicfrefeeversion_id"] = cfrdata['version']
                invoice["filename"] = filename
                invoice["documentpath"] = response['documentpath']
                invoice["created_at"] = invoice_date
                return FOIRequestInvoices.save_invoice(invoice, userid)
        except Exception as exeception:
            raise exeception