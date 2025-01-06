import React, { useState } from 'react';
import { useDispatch, useSelector } from "react-redux";
import TextField from '@mui/material/TextField';
import InputAdornment from "@mui/material/InputAdornment";
import MenuItem from '@mui/material/MenuItem';
import '.././index.scss'
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { formatDate, isMinistryLogin } from "../../../../../helper/FOI/helper";
import { ApplicationFeeStatuses, paymentMethods } from '../util';
import _ from 'lodash';
import CustomizedTooltip from '../../Tooltip/MuiTooltip/Tooltip';
import FileUpload from '../../FileUpload';
import { generateReceiptFromOnlinePayment } from '../../../../../apiManager/services/FOI/foiApplicationFeeFormServices';
import { getFileFromS3, getFOIS3DocumentPreSignedUrl } from '../../../../../apiManager/services/FOI/foiOSSServices';


export const ApplicationFeeTab = ({
    requestNumber,
    requestState,
    requestDetails,
    ministryId,
    requestId,
    userDetail,
    setCFRUnsaved,
    formData,
    setFormData,
    rerenderFileUpload,
    updateFilesCb
  }: any) => {

    const dispatch = useDispatch();
    const userGroups = userDetail.groups.map((group: any) => group.slice(1));
    const isMinistry = isMinistryLogin(userGroups);
    const initialApplicationFeeState: any = useSelector((state: any) => state.foiRequests.foiRequestApplicationFeeForm);

    const [initialFormData, setInitialFormData] = useState(initialApplicationFeeState);

    const handleTextChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
      const name : string = e.target.name;
      const value : string = e.target.value;
  
      setFormData((values: any) => ({...values, [name]: value}));
    };

    const handleAmountPaidChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
      const re = new RegExp('^-?\\d+(?:\.\\d{0,' + (2 || -1) + '})?');
      const value : number = +(e.target.value.match(re)?.[0] || 0)
  
      setFormData((values: any) => ({...values, ['amountPaid']: value}));
    }

    const handleRefundAmountChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
      const re = new RegExp('^-?\\d+(?:\.\\d{0,' + (2 || -1) + '})?');
      const value : number = +(e.target.value.match(re)?.[0] || 0)
  
      setFormData((values: any) => ({...values, ['refundAmount']: value}));
    }

    const tooltipTotals = {
      "title": "Payment Details",
      "content": [
        <div className="toolTipContent">
          <p>The balance remaining for a fee estimate is the Estimated total subtracted by the amount paid.
            When actuals are entered, the balance remaining is the actual totals subtracted by the amount paid.
            If the balance is negative, then an applicant may be owed a refund.</p>
        </div>]
    };

    React.useEffect(() => {
      if (!_.isEqual(initialFormData, formData)) {
        setCFRUnsaved(true);
      } else {
        setCFRUnsaved(false);
      }
    }, [initialFormData, formData]);

    const applicationFeeStatusField = (
      <div className="col-lg-6 foi-details-col">
        <TextField
          id="applicationFeeStatus"
          label={"Application Fee Status"}
          inputProps={{ "aria-labelledby": "applicationFeeStatus-label"}}
          InputLabelProps={{ shrink: true }}
          select
          name="applicationFeeStatus"
          value={formData?.applicationFeeStatus}
          onChange={handleTextChanges}
          variant="outlined"
          fullWidth
          required
          disabled={formData?.paymentSource == 'creditcardonline' ? true : false}
        >
          {ApplicationFeeStatuses.map((option) => (
          <MenuItem
            key={option.value}
            value={option.value}
            disabled={option.disabled}
          >
            {option.label}
          </MenuItem>
          ))}
        </TextField>
      </div>
    )

    const amountPaidFieldDisabled = () => {
      return formData?.applicationFeeStatus == 'na-ige' ? true : false
    }

    const amountPaidFieldError = () => {
      if (formData?.paymentSource != 'creditcardonline' && formData?.paymentSource != 'init') {
        if (formData?.amountPaid % 10 != 0 || formData?.amountPaid == 0) return true;
      }
    }
    const amountPaidField = (
      <div className="col-lg-6 foi-details-col">
        <TextField
          id="amountpaid"
          label="Amount Paid"
          inputProps={{
            "aria-labelledby": "amountpaid-label",
            step: 0.01,
            min: 0
          }}
          InputProps={{
            startAdornment: <InputAdornment position="start">$</InputAdornment>
          }}
          InputLabelProps={{ shrink: true }}
          variant="outlined"
          name="amountPaid"
          type="number"
          value={formData?.amountPaid}
          onChange={handleAmountPaidChanges}
          onBlur={(e) => {
            e.target.value = parseFloat(e.target.value).toFixed(2);
          }}
          fullWidth
          required
          error={amountPaidFieldError()}
          helperText={formData?.amountPaid % 10 != 0 && 'You can only enter as increments of 10'}
          disabled={amountPaidFieldDisabled()}
        />
      </div>
    )

    const paymentSourceFieldDisabled = () => {
      if (formData?.applicationFeeStatus == 'na-ige') return true
      if (formData?.paymentSource == paymentMethods.filter((option) => option.value === 'creditcardonline')[0].value) return true
      return false;
    }

    const paymentSourceField = (
      <div className="col-lg-6 foi-details-col">
        <TextField
          id="paymentSource"
          label={"Payment Source"}
          inputProps={{ "aria-labelledby": "paymentSource-label"}}
          InputLabelProps={{ shrink: true }}
          select
          name="paymentSource"
          value={formData?.paymentSource}
          onChange={handleTextChanges}
          variant="outlined"
          fullWidth
          required
          disabled={paymentSourceFieldDisabled()}
        >
          {paymentMethods.map((option) => (
          <MenuItem
            key={option.value}
            value={option.value}
            disabled={option.disabled}
          >
            {option.label}
          </MenuItem>
          ))}
        </TextField>
      </div>
    )

    const paymentDateFieldError = () => {
      if (formData?.paymentSource != 'creditcardonline' && formData?.paymentSource != 'init') {
        if (formData?.paymentDate == '' || formData?.paymentDate == null) return true;
      }
    }
    const paymentDateField = (
      <div className="col-lg-6 foi-details-col">
        <TextField
          id="paymentDate"
          label="Payment Date"
          type="date"
          value={formData?.paymentDate?.split(' ')[0] || ''}
          name="paymentDate"
          onChange={handleTextChanges}
          inputProps={{ "aria-labelledby": "paymentDate-label"}}
          InputLabelProps={{
          shrink: true,
          }}
          InputProps={{inputProps: { max: formatDate(new Date())} }}
          variant="outlined"
          required
          fullWidth
          disabled={formData?.applicationFeeStatus == 'na-ige' ? true : false}
          error={paymentDateFieldError()}
        />
      </div>
    )

    const orderIdFieldDisabled = () => {
      if (formData?.applicationFeeStatus == 'na-ige') return true;
      if (formData?.paymentSource == paymentMethods.filter((option) => option.value === 'creditcardonline')[0].value) {
        return false;
      } else {
        return true;
      }
    }
    const orderIdField = (
      <div className="col-lg-6 foi-details-col">
        <TextField
          id="orderId"
          label="Order ID"
          inputProps={{
            "aria-labelledby": "orderid-label"
          }}
          InputLabelProps={{ shrink: true }}
          variant="outlined"
          name="orderId"
          type="text"
          value={formData?.orderId}
          onChange={handleTextChanges}
          fullWidth
          disabled={orderIdFieldDisabled()}
        />
      </div>
    )

    const transactionNumberFieldDisabled = () => {
      if (formData?.applicationFeeStatus == 'na-ige') return true;
      if (formData?.paymentSource == paymentMethods.filter((option) => option.value === 'creditcardonline')[0].value) {
        return false;
      } else {
        return true;
      }
    }
    const transactionNumberField = (
      <div className="col-lg-6 foi-details-col">
        <TextField
          id="transactionnumber"
          label="Transaction Number"
          inputProps={{
            "aria-labelledby": "transactionnumber-label"
          }}
          InputLabelProps={{ shrink: true }}
          variant="outlined"
          name="transactionNumber"
          type="text"
          value={formData?.transactionNumber}
          onChange={handleTextChanges}
          fullWidth
          disabled={transactionNumberFieldDisabled()}
        />
      </div>
    )

    const receiptUploadFieldDisabled = () => {
      if (formData?.applicationFeeStatus == 'na-ige') return true;
      return false;
    }
    let attachment: any = [];
    let multipleFiles = true
    let mimeTypes = ['.pdf', '.doc', '.docx', '.jpeg', '.jpg', '.png', '.tiff', '.tif', '.xls', '.xlsx', '.csv']
    let maxFileSize = 100;
    let totalFileSize = 100;
    let attchmentFileNameList: any[] = []
    let existingDocuments;
    let maxNumberOfFiles = 10
    let modalFor;
    let handleTagChange;
    let tagValue;
    let tagList; 
    let isMinistryCoordinator;
    let uploadFor="attachment";
    let totalUploadedRecordSize;
    let totalRecordUploadLimit;
  
    const receiptUploadField = (
      <div className="col-lg-12 foi-details-col">
        {formData?.paymentSource != 'init' && rerenderFileUpload && <FileUpload
          attachment={attachment}
          attchmentFileNameList={attchmentFileNameList}
          multipleFiles={multipleFiles}
          mimeTypes={mimeTypes}
          maxFileSize={maxFileSize}
          totalFileSize={totalFileSize}
          updateFilesCb={updateFilesCb}
          modalFor={modalFor}
          uploadFor={uploadFor}
          tagList={tagList}
          handleTagChange={handleTagChange}
          tagValue={tagValue}
          maxNumberOfFiles={receiptUploadFieldDisabled() ? 0 : maxNumberOfFiles}
          isMinistryCoordinator={isMinistryCoordinator}
          existingDocuments={existingDocuments}
          totalUploadedRecordSize={totalUploadedRecordSize}
          totalRecordUploadLimit={totalRecordUploadLimit}
        />}
      </div>
    )

    const getReceiptFromOnlinePayment = () => {
      const selectedBodies = requestDetails?.selectedMinistries.map((ministry: any) => {
        return {
          publicBody: ministry.code,
          ministry: [{name: ministry.name}]
        }
      })

      let data = {
        selectedPublicBodies: selectedBodies,
        header: {
            firstName: requestDetails?.firstName,
            lastName: requestDetails?.lastName,
            dateSubmitted: requestDetails?.receivedDate
        },
        paymentInfo: {
          totalAmount: formData?.amountPaid,
          transactionNumber: formData?.transactionNumber,
          transactionOrderId: formData?.orderId,
          cardType: formData?.paymentSource == 'creditcardonline' ? 'CC' : ''
        }
      }
      let callback = (res: any) => {
          let blob = new Blob([res], {type: "application/pdf"});
          let blobURL = URL.createObjectURL(blob);
          window.open(blobURL);
      }
      generateReceiptFromOnlinePayment(data, requestId, formData?.paymentId, dispatch, callback, (err: any) => {
        console.log('Error: ', err)
      })
    }

    const getReceiptFile = (filename?: string, rawfilepath?: string) => {
      if (filename) {
        const filepath = rawfilepath?.split('/').slice(4).join('/')
        getFOIS3DocumentPreSignedUrl(filepath, undefined, dispatch, (err: any, res: any) => {
          if (!err) {
            getFileFromS3({filepath: res}, (_err: any, response: any) => {
              let blob = new Blob([response.data], {type: "application/pdf"});
              let blobURL = URL.createObjectURL(blob);
              window.open(blobURL);
            });
          }
        }, 'attachments', 'Misc');
      } else {
        getReceiptFromOnlinePayment();
      }
    }

    const uploadedReceiptsField = formData?.receipts.map((receipt: any) => {
      if (receipt.isactive) {
        return (
          <div className="col-lg-12 foi-details-col application-fee-receipt">
            <u
              className="receipt-link"
              onClick={() => {
                getReceiptFile(receipt?.receiptfilename, receipt?.receiptfilepath)}
              }
            >{receipt.receiptfilename ? receipt.receiptfilename : 'view online payment receipt'}</u>
            <i
              className="fa fa-times-circle receipt-delete"
              onClick={() => setFormData((values: any) => ({...values, ['receipts']: [...formData?.receipts.filter((r: any) => r.receiptfilename != receipt.receiptfilename), {...receipt, isactive: false}]}))}
            >
            </i>
          </div>
        )}
    })
    if (uploadedReceiptsField.length == 0) {
      uploadedReceiptsField.push(
        <div className="col-lg-12 foi-details-col">
            <u
              onClick={() => {
                getReceiptFile()}
              }
            >{'view online payment receipt'}</u>
          </div>
      )
    }

    const disableRefundFields = () => {
      let isDisabled = formData?.amountPaid == 0 || formData?.amountPaid == null || formData?.amountPaid == '' || formData?.amountPaid % 10 != 0
      if (formData?.applicationFeeStatus == 'na-ige') {
        isDisabled = false
      }
      return isDisabled;
    }

    const refundAmountFieldError = () => {
      let refundDateBlank = formData?.refundDate == '' || formData?.refundDate == null
      if (!refundDateBlank && formData?.refundAmount == 0) return true;
      if (formData?.refundAmount % 10 != 0 || formData?.refundAmount > formData?.amountPaid) return true
      return false;
    }

    const [refundAmountHelperText, setRefundAmountHelperText] = useState('')

    React.useEffect(() => {
      if (formData?.refundAmount % 10 != 0) {
        setRefundAmountHelperText('You can only enter as increments of 10')
      } else if (formData?.refundAmount > formData?.amountPaid) {
        setRefundAmountHelperText('Refund amount cannot be greater than amount paid')
      } else {
        setRefundAmountHelperText('')
      }
    }, [formData?.refundAmount])

    const refundAmountField = (
      <div className="col-lg-6 foi-details-col">
        <TextField
          id="refundamount"
          label="Refund Amount"
          inputProps={{
            "aria-labelledby": "refundamount-label",
            step: 0.01,
            min: 0
          }}
          InputProps={{
            startAdornment: <InputAdornment position="start">$</InputAdornment>
          }}
          InputLabelProps={{ shrink: true }}
          variant="outlined"
          name="refundAmount"
          type="number"
          value={formData?.refundAmount}
          onChange={handleRefundAmountChanges}
          onBlur={(e) => {
            e.target.value = parseFloat(e.target.value).toFixed(2);
          }}
          fullWidth
          error={refundAmountFieldError()}
          helperText={refundAmountHelperText}
          disabled={disableRefundFields()}
        />
      </div>
    )

    const refundDateFieldError = () => {
      if (formData?.refundAmount > 0) {
        if (formData?.refundDate == '' || formData?.refundDate == null) return true
      }
      return false;
    }

    const refundDateField = (
      <div className="col-lg-6 foi-details-col">
        <TextField
          id="refundDate"
          label="Refund Date"
          type="date"
          value={formData?.refundDate?.split(' ')[0] || ''}
          name="refundDate"
          onChange={handleTextChanges}
          inputProps={{ "aria-labelledby": "refundDate-label"}}
          InputLabelProps={{
          shrink: true,
          }}
          error={refundDateFieldError()}
          InputProps={{inputProps: { max: formatDate(new Date())} }}
          variant="outlined"
          fullWidth
          disabled={disableRefundFields()}
        />
      </div>
    )

    return (
      <>
        <div className='request-accordian'>
          <Accordion defaultExpanded={true}>
            <AccordionSummary className="accordionSummary" expandIcon={<ExpandMoreIcon />} id="payment-details">
              <Typography className="heading">PAYMENT DETAILS</Typography>
            </AccordionSummary>
            <AccordionDetails>
              {!isMinistry && 
              <div className="row foi-details-row">
                {applicationFeeStatusField}
                {amountPaidField}
                {paymentSourceField}
                {paymentDateField}
                {orderIdField}
                {transactionNumberField}
                {receiptUploadField}
                {formData?.receipts.length > 0 || formData?.paymentSource == 'creditcardonline' ? uploadedReceiptsField : <></>}
              </div>}
              <div className="cfrform-floatRight cfrform-totals">
                <CustomizedTooltip content={tooltipTotals} position={""} />
                <p className="hideContent" id="popup-6">Information6</p>
              </div>
            </AccordionDetails>
          </Accordion>
        </div>
        <div className='request-accordian'>
          <Accordion defaultExpanded={true}>
            <AccordionSummary className="accordionSummary" expandIcon={<ExpandMoreIcon />} id="refund-details">
              <Typography className="heading">REFUND DETAILS</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <div className="row foi-details-row">
                {refundAmountField}
                {refundDateField}
              </div>
              <div className="row foi-details-row">
                <div className="col-lg-12 foi-details-col">
                  <TextField
                    id="reasonforrefund"
                    label="Reason for Refund Request"
                    multiline
                    rows={4}
                    name="reasonForRefund"
                    value={formData?.reasonForRefund}
                    variant="outlined"
                    InputLabelProps={{ shrink: true, }}
                    onChange={handleTextChanges}
                    fullWidth
                    disabled={disableRefundFields()} 
                  />
                </div>
              </div>
            </AccordionDetails>
          </Accordion>
        </div>
      </>
    );
  }