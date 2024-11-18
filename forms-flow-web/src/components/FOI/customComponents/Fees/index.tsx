import React, { useState } from 'react';
import { useDispatch, useSelector } from "react-redux";
import './index.scss'
import Box from '@mui/material/Box';
import Chip from '@mui/material/Chip';
import { errorToast, isMinistryLogin, readUploadedFileAsBytes } from "../../../../helper/FOI/helper";
import type { params, CFRFormData, ApplicationFeeFormData } from './types';
import foiFees from '../../../../constants/FOI/foiFees.json';
import { fetchCFRForm, saveCFRForm } from "../../../../apiManager/services/FOI/foiCFRFormServices";
import _ from 'lodash';
import { toast } from "react-toastify";
import { StateEnum } from '../../../../constants/FOI/statusEnum';
import { CFRFormHistoryModal } from './CFRFormHistoryModal';
import { ApplicationFeeTab } from './Tabs/ApplicationFeeTab';
import { StateChangeDialog } from './StateChangeDialog';
import { HorizontalTabs } from './HorizontalTabs';
import { CFRFormTab } from './Tabs/CFRFormTab';
import { BottomButtonGroup } from './BottomButtonGroup';
import { CFRFormStatus } from './CFRFormStatus';
import { FeesSubtabValues } from './types';
import { fetchApplicationFeeForm, saveApplicationFeeForm } from '../../../../apiManager/services/FOI/foiApplicationFeeFormServices';
import { completeMultiPartUpload, postFOIS3DocumentPreSignedUrl, saveFilesinS3 } from '../../../../apiManager/services/FOI/foiOSSServices';
import FOI_COMPONENT_CONSTANTS from '../../../../constants/FOI/foiComponentConstants';
import { StatusChangeDialog } from './StatusChangeDialog';

export const Fees = ({
    requestNumber,
    requestState,
    requestDetails,
    ministryId,
    requestId,
    userDetail,
    setCFRUnsaved,
    handleStateChange
  }: params) => {

    const dispatch = useDispatch();

    const userGroups = userDetail.groups.map(group => group.slice(1));
    const isMinistry = isMinistryLogin(userGroups);
    const formHistory: Array<any> = useSelector((state: any) => state.foiRequests.foiRequestCFRFormHistory);

    //DATA FOR CFR FORM
    React.useEffect(() => {
      if (ministryId) {
        fetchCFRForm(
          ministryId,
          dispatch,
        );
      }
    }, [ministryId]);

    const initialCFRState: any = useSelector((state: any) => state.foiRequests.foiRequestCFRForm);

    const blankCFRForm: CFRFormData = {
      cfrfeeid: null,
      formStatus: "init",
      estimatedTotalDue: 0,
      actualTotalDue: 0,
      amountPaid: 0,
      estimatePaymentMethod: "init",
      balancePaymentMethod: "init",
      balanceRemaining:0,
      feewaiverAmount:0,
      refundAmount:0,
      estimates: {
        locating: 0,
        producing: 0,
        ministryPreparing: 0,
        iaoPreparing: 0,
        electronicPages: 0,
        hardcopyPages: 0,
      },
      actual: {
        locating: 0,
        producing: 0,
        ministryPreparing: 0,
        iaoPreparing: 0,
        electronicPages: 0,
        hardcopyPages: 0,
      },
      suggestions: '',
      reason:"init"
    };

    const [initialCFRFormData, setInitialCFRFormData] = useState(blankCFRForm);
    const [CFRFormData, setCFRFormData] = useState(initialCFRFormData);
    
    React.useEffect(() => {
      let formattedData = {
        cfrfeeid: initialCFRState.cfrfeeid,
        formStatus: initialCFRState.status === null ? 'init' : initialCFRState.status,
        estimatedTotalDue: initialCFRState.feedata?.estimatedtotaldue || 0,
        actualTotalDue: initialCFRState.feedata?.actualtotaldue || 0,
        estimatePaymentMethod: initialCFRState.feedata?.estimatepaymentmethod || 'init',
        balancePaymentMethod: initialCFRState.feedata?.balancepaymentmethod || 'init',
        amountPaid: initialCFRState.feedata?.amountpaid,
        balanceRemaining: initialCFRState.feedata?.balanceremaining,
        feewaiverAmount: initialCFRState.feedata?.feewaiveramount || 0,
        refundAmount: initialCFRState.feedata?.refundamount,
        estimates: {
          locating: initialCFRState.feedata?.estimatedlocatinghrs,
          producing: initialCFRState.feedata?.estimatedproducinghrs,
          iaoPreparing: initialCFRState.feedata?.estimatediaopreparinghrs,
          ministryPreparing: initialCFRState.feedata?.estimatedministrypreparinghrs,
          electronicPages: initialCFRState.feedata?.estimatedelectronicpages,
          hardcopyPages: initialCFRState.feedata?.estimatedhardcopypages,
        },
        actual: {
          locating: initialCFRState.feedata?.actuallocatinghrs,
          producing: initialCFRState.feedata?.actualproducinghrs,
          iaoPreparing: initialCFRState.feedata?.actualiaopreparinghrs,
          ministryPreparing: initialCFRState.feedata?.actualministrypreparinghrs,
          electronicPages: initialCFRState.feedata?.actualelectronicpages,
          hardcopyPages: initialCFRState.feedata?.actualhardcopypages,
        },
        suggestions: initialCFRState.overallsuggestions,
        reason: initialCFRState.reason === null ? "init" : initialCFRState.reason
      };
      setCFRFormData(formattedData);
      setInitialCFRFormData(formattedData);
    }, [initialCFRState]);

    React.useEffect(() => {
      if (!_.isEqual(initialCFRFormData, CFRFormData)) {
        setCFRUnsaved(true);
      } else {
        setCFRUnsaved(false);
      }
    }, [initialCFRFormData, CFRFormData]);

    // DATA FOR APPLICATION FEE FORM
    React.useEffect(() => {
      if (ministryId) {
        fetchApplicationFeeForm(
          ministryId,
          requestId,
          dispatch,
        );
      } else {
        fetchApplicationFeeForm(
          null,
          requestId,
          dispatch,
        );
      }
    }, [requestId, ministryId]);

    const initialApplicationFeeState: any = useSelector((state: any) => state.foiRequests.foiRequestApplicationFeeForm);

    const blankApplicationFeeForm: ApplicationFeeFormData = {
      applicationfeeid: null,
      applicationFeeStatus: 'init',
      amountPaid: 0,
      paymentSource: 'init',
      paymentDate: '',
      orderId: '',
      transactionNumber: '',
      receiptfilename: '',
      receiptfilepath: '',
      reasonForRefund: '',
      paymentId: null
    };

    const [initialApplicationFeeFormData, setInitialApplicationFeeFormData] = useState(blankApplicationFeeForm);
    const [applicationFeeFormData, setApplicationFeeFormData] = useState(initialApplicationFeeFormData);
    React.useEffect(() => {
      let formattedData = {
        applicationfeeid: initialApplicationFeeState.applicationfeeid,
        applicationFeeStatus: initialApplicationFeeState.applicationfeestatus,
        amountPaid: initialApplicationFeeState.amountpaid,
        paymentSource: initialApplicationFeeState.paymentsource,
        paymentDate: initialApplicationFeeState.paymentdate,
        orderId: initialApplicationFeeState.orderid,
        transactionNumber: initialApplicationFeeState.transactionnumber,
        receiptfilename: initialApplicationFeeState.receiptfilename,
        receiptfilepath: initialApplicationFeeState.receiptfilepath,
        reasonForRefund: initialApplicationFeeState.reasonforrefund,
        paymentId: initialApplicationFeeState.paymentid
      };
      setApplicationFeeFormData(formattedData);
      setInitialApplicationFeeFormData(formattedData);
    }, [initialApplicationFeeState]);

    // For receipt file upload
    const [receiptFileUpload, setReceiptFileUpload] = useState<any>()

    const handleReceiptFileUpload = (_files: File) => {
      setReceiptFileUpload(_files);
    }

    const updateFilesCb = (_files: any, _errorMessage: any) => {
      handleReceiptFileUpload(_files);
    };
  
    //Validations
    const validateField = (value: number, step: number) => {
      return (value % step) !== 0;
    }
  
    const validateEstimatePaymentMethod = () => {
      return initialCFRFormData?.amountPaid === 0 && CFRFormData?.amountPaid > 0 && CFRFormData?.estimatePaymentMethod === 'init'
    }
  
    const validateBalancePaymentMethod = () => {
      return initialCFRFormData?.amountPaid !== 0 &&
      CFRFormData?.amountPaid !== 0 &&
      CFRFormData?.amountPaid > initialCFRFormData?.amountPaid &&
      CFRFormData?.balancePaymentMethod === 'init'
    }

    const validateApplicationFeeAmountPaid = () => {
      return applicationFeeFormData?.amountPaid % 10 == 0 ? true : false;
    }
  
    const validateFields = () => {
      if (applicationFeeFormData?.paymentSource != 'creditcardonline' && applicationFeeFormData?.paymentSource != 'init') {
        if (applicationFeeFormData?.paymentDate == null || applicationFeeFormData?.paymentDate == '') return false;
        if (applicationFeeFormData?.amountPaid == 0) return false;
      }
      if (validateBalancePaymentMethod() || validateEstimatePaymentMethod()) {
        return false;
      }
      let field: keyof typeof CFRFormData.estimates;
      for (field in CFRFormData.estimates) {
        if (validateField(CFRFormData.estimates[field], foiFees[field].unit)) {
          return false;
        }
      }
      let afield: keyof typeof CFRFormData.actual
      for (afield in CFRFormData.actual) {
        if (validateField(CFRFormData.actual[afield], foiFees[afield].unit)) {
          return false;
        }
      }

      if (!validateApplicationFeeAmountPaid()) {
        return false;
      }

      return !_.isEqual(initialCFRFormData, CFRFormData) || !_.isEqual(initialApplicationFeeFormData, applicationFeeFormData);
    }

    //Change handlers
    const handleTextChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
      const name : string = e.target.name;
      const value : string = e.target.value;
  
      setCFRFormData(values => ({...values, [name]: value}));
    };

    const calculateBalanceRemaining = () => {
      let balanceRemaining = 0;
      if (CFRFormData?.actualTotalDue)
        balanceRemaining = (CFRFormData.actualTotalDue - CFRFormData.amountPaid - CFRFormData.feewaiverAmount);
      else
        balanceRemaining = (CFRFormData.estimatedTotalDue - CFRFormData.amountPaid - CFRFormData.feewaiverAmount)
      return !Number.isNaN(balanceRemaining) || balanceRemaining  ? balanceRemaining : 0;
    }

    const cfrStatusDisabled = () => {
      if(requestState === StateEnum.peerreview.name){
        return true;
      }
      if (formHistory.length > 0 && [StateEnum.feeassessed.name, StateEnum.onhold.name, StateEnum.callforrecords.name].includes(requestState)) {
        if (isMinistry) {
          return ['review', 'approved'].includes(initialCFRFormData.formStatus) || isNewCFRForm;
        } else {
          return initialCFRFormData.formStatus !== 'review';
        }
      }
      if (CFRFormData.balanceRemaining > 0 &&  [StateEnum.feeassessed.name, StateEnum.onhold.name].includes(requestState)) {
        if (isMinistry) {
          return !['clarification', 'init'].includes(initialCFRFormData.formStatus);
        } else {
          return initialCFRFormData.formStatus === 'clarification';
        }
      }
      return true;
    }

    // Saving data
    const saveReceiptAndApplicationFeeData = (value: any, fileInfoList: any, files: any) => {
      if (value) {
        if (files.length !== 0) {
          postFOIS3DocumentPreSignedUrl(ministryId, fileInfoList.map((file: any) => ({...file, multipart: true})), 'attachments', 'Misc', dispatch, async (err: any, res: any) => {
            let _documents: any = [];
            if (!err) {
              let completed = 0;
              let failed = [];
              const toastID = toast.loading("Uploading files (" + completed + "/" + fileInfoList.length + ")")
              for (let header of res) {
                const _file = files.find((file: any) => file.filename === header.filename);
                const _fileInfo = fileInfoList.find((fileInfo: any) => fileInfo.filename === header.filename);
                const documentDetails = {documentpath: header.filepathdb, filename: header.filename, category: _fileInfo.filestatustransition};
                let bytes = await readUploadedFileAsBytes(_file)              
                // const CHUNK_SIZE = OSS_S3_CHUNK_SIZE;
                const CHUNK_SIZE = 104857600;
                const totalChunks = Math.ceil(bytes.byteLength / CHUNK_SIZE);
                let parts = [];
                for (let chunk = 0; chunk < totalChunks; chunk++) {
                  let CHUNK = bytes.slice(chunk * CHUNK_SIZE, (chunk + 1) * CHUNK_SIZE);
                  let response = await saveFilesinS3({filepath: header.filepaths[chunk]}, CHUNK, dispatch, (_err: any, _res: any) => {
                    if (_err) {
                      failed.push(header.filename);
                    }
                  })
                  if (response?.status === 200) {
                    parts.push({PartNumber: chunk + 1, ETag: response.headers.etag})
                  } else {
                    failed.push(header.filename);
                  }
                }
                await completeMultiPartUpload({uploadid: header.uploadid, filepath: header.filepathdb, parts: parts}, ministryId, 'attachments', 'Misc', dispatch, (_err: any, _res: any) => {                
                  if (!_err && _res.ResponseMetadata.HTTPStatusCode === 200) {
                    completed++;
                    toast.update(toastID, {
                      render: "Uploading files (" + completed + "/" + fileInfoList.length + ")",
                      isLoading: true,
                    })
                    _documents.push(documentDetails);
                  } else {
                    failed.push(header.filename);
                  }
                })
              }
              var toastOptions = {
                render: failed.length > 0 ?
                  "The following " + failed.length + " file uploads failed\n- " + failed.join("\n- ")  :
                  fileInfoList.length + ' Files successfully saved',
                type: failed.length > 0 ? "error" : "success",
              }
              let options: any = {
                ...toastOptions,
                className: "file-upload-toast",
                isLoading: false,
                autoClose: 3000,
                hideProgressBar: true,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
                closeButton: true
              }
              toast.update(toastID, options);
              // setAttachmentLoading(false)
            }
            if (_documents.length > 0) {
              // save application fee data 
              let applicationFeeCallback = (_res: string) => {
                setInitialApplicationFeeFormData(applicationFeeFormData)
                toast.success("Application Fee form has been saved successfully.", {
                  position: "top-right",
                  autoClose: 3000,
                  hideProgressBar: true,
                  closeOnClick: true,
                  pauseOnHover: true,
                  draggable: true,
                  progress: undefined,
                });
                fetchApplicationFeeForm(
                  ministryId,
                  requestId,
                  dispatch,
                )
              };
              let applicationFeeData;
              // Save Application Fee form only if there are changes
              if (!_.isEqual(initialApplicationFeeFormData, applicationFeeFormData)) {
                applicationFeeData = {
                  applicationfeeid: applicationFeeFormData?.applicationfeeid,
                  applicationfeestatus: applicationFeeFormData?.applicationFeeStatus,
                  amountpaid: applicationFeeFormData?.amountPaid,
                  paymentsource: applicationFeeFormData?.paymentSource,
                  paymentdate: applicationFeeFormData?.paymentDate,
                  orderid: applicationFeeFormData?.orderId,
                  transactionnumber: applicationFeeFormData?.transactionNumber,
                  reasonforrefund: applicationFeeFormData?.reasonForRefund,
                  receiptfilename: _documents[0].filename,
                  receiptfilepath: _documents[0].documentpath
                }
                saveApplicationFeeForm(
                  applicationFeeData,
                  ministryId,
                  requestId,
                  dispatch,
                  applicationFeeCallback,
                  (errorMessage: string) => {
                    errorToast(errorMessage)
                  },
                )
              }
              if (applicationFeeFormData?.applicationFeeStatus == 'appfeeowing') {
                handleStateChange('App Fee Owing');
              }
            }
          })
        }             
      }
    }

    const saveApplicationFeeTab = () => {
      setStatusChangeModalOpen(false);
      // FIRST save receipt file if present
      if (receiptFileUpload && receiptFileUpload.length > 0) {
        // Example: dev-forms-foirequest-e/Misc/EDU-2024-09161111/appfeereceipt/bdc62f7e-1d29-42a7-852d-7fc81acc1cc0.pdf
        let fileInfo = {
          ministrycode: "Misc",
          requestnumber: requestNumber ? requestNumber : `U-00${requestId}`,
          filestatustransition: 'appfeereceipt',
          filename: receiptFileUpload?.[0].name,
          filesize: receiptFileUpload?.[0].size,
        };
        saveReceiptAndApplicationFeeData(true, [fileInfo], receiptFileUpload);
      } else {
        let applicationFeeCallback = (_res: string) => {
          setInitialApplicationFeeFormData(applicationFeeFormData)
          toast.success("Application Fee form has been saved successfully.", {
            position: "top-right",
            autoClose: 3000,
            hideProgressBar: true,
            closeOnClick: true,
            pauseOnHover: true,
            draggable: true,
            progress: undefined,
          });
          fetchApplicationFeeForm(
            ministryId,
            requestId,
            dispatch,
          )
        };
        let applicationFeeData;
        applicationFeeData = {
          applicationfeeid: applicationFeeFormData?.applicationfeeid,
          applicationfeestatus: applicationFeeFormData?.applicationFeeStatus,
          amountpaid: applicationFeeFormData?.amountPaid,
          paymentsource: applicationFeeFormData?.paymentSource,
          paymentdate: applicationFeeFormData?.paymentDate,
          orderid: applicationFeeFormData?.orderId,
          transactionnumber: applicationFeeFormData?.transactionNumber,
          reasonforrefund: applicationFeeFormData?.reasonForRefund,
          receiptfilename: applicationFeeFormData?.receiptfilename,
          receiptfilepath: applicationFeeFormData?.receiptfilepath
        }
        saveApplicationFeeForm(
          applicationFeeData,
          ministryId,
          requestId,
          dispatch,
          applicationFeeCallback,
          (errorMessage: string) => {
            errorToast(errorMessage)
          },
        )
        if (applicationFeeFormData?.applicationFeeStatus == 'appfeeowing') {
          handleStateChange('App Fee Owing');
        }
      }
    }
  
    const saveCFRFormTab = () => {
      let cfrCallback = (_res: string) => {
        setIsNewCFRForm(false)
        setInitialCFRFormData(CFRFormData)
        toast.success("CFR Fee form has been saved successfully.", {
          position: "top-right",
          autoClose: 3000,
          hideProgressBar: true,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
          progress: undefined,
        });
        fetchCFRForm(
          ministryId,
          dispatch,
        );
      };
      let data;
      if (isMinistry) {
        data = {
          feedata:{
            amountpaid: CFRFormData.amountPaid,
            estimatedtotaldue: CFRFormData.estimatedTotalDue,
            actualtotaldue: CFRFormData.actualTotalDue,
            ...CFRFormData.estimatePaymentMethod !== 'init' && {estimatepaymentmethod: CFRFormData.estimatePaymentMethod},
            ...CFRFormData.balancePaymentMethod !== 'init' && {balancepaymentmethod: CFRFormData.balancePaymentMethod},
            balanceremaining: calculateBalanceRemaining(),
            feewaiveramount: CFRFormData.feewaiverAmount,
            refundamount: CFRFormData.refundAmount,
            estimatedlocatinghrs: CFRFormData.estimates.locating,
            actuallocatinghrs: CFRFormData.actual.locating,
            estimatedproducinghrs: CFRFormData.estimates.producing,
            actualproducinghrs: CFRFormData.actual.producing,
            estimatediaopreparinghrs: CFRFormData.estimates.iaoPreparing,
            estimatedministrypreparinghrs: CFRFormData.estimates.ministryPreparing,
            actualiaopreparinghrs: CFRFormData.actual.iaoPreparing,
            actualministrypreparinghrs: CFRFormData.actual.ministryPreparing,
            estimatedelectronicpages: CFRFormData.estimates.electronicPages,
            actualelectronicpages: CFRFormData.actual.electronicPages,
            estimatedhardcopypages: CFRFormData.estimates.hardcopyPages,
            actualhardcopypages: CFRFormData.actual.hardcopyPages,
          },
          overallsuggestions: CFRFormData.suggestions,
          status: CFRFormData.formStatus === 'init' ? '' : CFRFormData.formStatus,
          cfrfeeid: CFRFormData.cfrfeeid,
          reason: CFRFormData.reason === "init" ? '' : CFRFormData.reason
        }
      } else {
        data = {
          feedata:{
            amountpaid: CFRFormData.amountPaid,
            estimatediaopreparinghrs: CFRFormData.estimates.iaoPreparing,
            actualiaopreparinghrs: CFRFormData.actual.iaoPreparing,
            estimatedtotaldue: CFRFormData.estimatedTotalDue,
            actualtotaldue: CFRFormData.actualTotalDue,
            ...CFRFormData.estimatePaymentMethod !== 'init' && {estimatepaymentmethod: CFRFormData.estimatePaymentMethod},
            ...CFRFormData.balancePaymentMethod !== 'init' && {balancepaymentmethod: CFRFormData.balancePaymentMethod},
            balanceremaining: calculateBalanceRemaining(),
            feewaiveramount: CFRFormData.feewaiverAmount,
            refundamount: CFRFormData.refundAmount,
          },
          status: CFRFormData.formStatus,
          reason: CFRFormData.reason === "init" ? '' : CFRFormData.reason
        }
      }
      saveCFRForm(
        data,
        ministryId,
        requestId,
        isMinistry,
        dispatch,
        cfrCallback,
        (errorMessage: string) => {
          errorToast(errorMessage)
        },
      )
    }

    const save = () => {
      if (selectedSubtab == FeesSubtabValues.APPLICATIONFEE) {
        //Show modal if ige or app fee owing status is selected
        if (applicationFeeFormData?.applicationFeeStatus == 'na-ige') {
          setStatusChangeModalMessage('Are you sure you want to set the Application Fee Status to N/A - IGE?');
          setStatusChangeModalOpen(true);
        } else if (applicationFeeFormData?.applicationFeeStatus == 'appfeeowing') {
          setStatusChangeModalMessage(`Are you sure you want to update the Application Fee Status to App Fee Owing? 
            The request status will also be changed to App Fee Owing and you will be prompted to confirm the state change again.`);
          setStatusChangeModalOpen(true);
        }
        else {
          saveApplicationFeeTab();
        }
      }
      if (selectedSubtab == FeesSubtabValues.CFRFORM) {
        saveCFRFormTab();
      }
    };
  
    const [modalOpen, setModalOpen] = useState(false);
    const [modalMessage, setModalMessage] = useState(<></>);
    const handleSave = () => {
      setModalOpen(false);
      save();
    };
    const handleClose = () => {
      setCFRFormData(values => ({...values, formStatus: initialCFRFormData.formStatus}));
      setModalOpen(false);
    };
    const handleStatusChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      handleTextChanges(e);
      if (e.target.value === 'review') {
        setModalMessage(<>By changing the CFR Form Status to <b>"In Review with IAO"</b> you
        will be sending the form to the IAO user and locking your ability to edit the form.
        Are you sure you would like to continue?</>);
      } else if (e.target.value === 'approved') {
        setModalMessage(<>Are you sure you want to change the status to <b>"Approved"</b>? Once approved, a CFR form is uneditable. Any changes will require a new CFR form to be created.</>);
      } else if (e.target.value === 'clarification') {
        setModalMessage(<>By changing the CFR Form Status to <b>"Needs Clarification with Ministry" </b> you
        will be sending the form to the Ministry user and locking your ability to edit the form.
        Are you sure you would like to continue?</>);
      }
      setModalOpen(true);
    };
  
    const [createModalOpen, setCreateModalOpen] = useState(false);
    const handleCreateClose = () => {
      setCreateModalOpen(false);
    };

    const [historyModalOpen, setHistoryModal] = useState(false);
    const handleHistoryClose = () => {
      setHistoryModal(false);
    }

    const [statusChangeModalOpen, setStatusChangeModalOpen] = useState(false);
    const [statusChangeModalMessage, setStatusChangeModalMessage] = useState('');
    const handleStatusChangeModalClose = () => {
      setStatusChangeModalOpen(false);
    }
  
    const disableNewCfrFormBtn = () => {
      return(CFRFormData?.formStatus !== 'approved' || requestState === StateEnum.peerreview.name || (requestState !== StateEnum.callforrecords.name &&
        requestState !== StateEnum.feeassessed.name && requestState !== StateEnum.onhold.name) || (requestState === StateEnum.onhold.name && CFRFormData?.actualTotalDue > 0));
    }
  
    const [isNewCFRForm, setIsNewCFRForm] = useState(false)
    const newCFRForm = () => {
      setCreateModalOpen(false)
      blankCFRForm.amountPaid= initialCFRState?.feedata?.amountpaid;
      blankCFRForm.estimatePaymentMethod = initialCFRState?.feedata?.estimatepaymentmethod || 'init';
      blankCFRForm.balancePaymentMethod= initialCFRState?.feedata?.balancepaymentmethod || 'init';
      blankCFRForm.feewaiverAmount = initialCFRState?.feedata?.feewaiveramount;
      blankCFRForm.refundAmount = initialCFRState?.feedata?.refundamount;
      setInitialCFRFormData(blankCFRForm);
      setCFRFormData(blankCFRForm);
      setIsNewCFRForm(true)
    }
  
    // Tab 
    let defaultTab = !isMinistry ? FeesSubtabValues.APPLICATIONFEE : FeesSubtabValues.CFRFORM;
    const [selectedSubtab, setSelectedSubtab] = useState(defaultTab)

    const handleSubtabChange = (_newSubtab: FeesSubtabValues) => {
      setSelectedSubtab(_newSubtab);
    }

    const showApplicationFeeTab = () => {
      if (!isMinistry) return true
      return false
    }

    const showCFRTab = () => {
      return (requestState !== StateEnum.intakeinprogress.name &&
      requestState !== StateEnum.unopened.name &&
      requestState !== StateEnum.open.name &&
      requestDetails?.requestType ===
        FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_GENERAL)
    }

    return (
      <div className="foi-review-container">
        <Box
          component="form"
          sx={{
            '& .MuiTextField-root': { my: 1, mx: 0 },
          }}
          autoComplete="off"
        >
          <div className="foi-request-form">
            <div style={{marginTop: 20}}></div>
              <div className="container foi-review-request-container cfrform-container">
                <div className="foi-request-review-header-row1">
                  <div className="foi-request-review-header-col1">
                    <div className="foi-request-number-header">
                      <h3 className="foi-review-request-text">{requestNumber}</h3>
                    </div>
                    <Chip
                      label={initialCFRFormData.formStatus === 'approved' ? "Version " + formHistory.length : "Version " + (formHistory.length + 1) + " Draft" }
                      sx={{ backgroundColor: '#096DD1', color: '#fff', height: 19}}
                    />
                  </div>
                  {selectedSubtab == FeesSubtabValues.CFRFORM && <CFRFormStatus 
                    formData={CFRFormData}
                    handleStatusChange={handleStatusChange}
                    cfrStatusDisabled={cfrStatusDisabled}
                    isNewCFRForm={isNewCFRForm}
                    handleTextChanges={handleTextChanges}
                    formHistory={formHistory}
                    isMinistry={isMinistry}
                    requestState={requestState}
                    StateEnum={StateEnum}
                  />}
                </div>
                {/* CFR Form History */}
                {selectedSubtab == FeesSubtabValues.CFRFORM ? <div className="cfr-history-button">
                  <CFRFormHistoryModal
                    modalOpen={historyModalOpen}
                    handleClose={handleHistoryClose}
                    formHistory={formHistory}
                    isMinistry={isMinistry}
                  />
                  <button
                    type="button"
                    className="btn btn-link btn-cfr-history"
                    disabled={formHistory.length < 1}
                    onClick={() => setHistoryModal(true)}
                  >
                    CFR Form History
                  </button>
                </div> : 
                // placeholder for layout
                <div className="cfr-history-button">
                  <div className="btn btn-link btn-cfr-history" style={{height: "2em"}}></div>
                </div>
                }
                <HorizontalTabs 
                  selectedSubtab={selectedSubtab} 
                  handleSubtabChange={handleSubtabChange}
                  showApplicationFeeTab={showApplicationFeeTab()}
                  showCFRTab={showCFRTab()}
                />
                {selectedSubtab == FeesSubtabValues.APPLICATIONFEE && !isMinistry && 
                <ApplicationFeeTab 
                  requestNumber={requestNumber}
                  requestState={requestState}
                  requestDetails={requestDetails}
                  ministryId={ministryId}
                  requestId={requestId}
                  userDetail={userDetail}
                  setCFRUnsaved={setCFRUnsaved}
                  formData={applicationFeeFormData}
                  setFormData={setApplicationFeeFormData}
                  handleTextChanges={handleTextChanges}
                  updateFilesCb={updateFilesCb}
                />}
                {selectedSubtab == FeesSubtabValues.CFRFORM && 
                <>
                <CFRFormTab
                  requestState={requestState}
                  ministryId={ministryId}
                  isMinistry={isMinistry}
                  requestNumber={requestNumber}
                  userDetail={userDetail}
                  requestId={requestId}
                  formData={CFRFormData}
                  initialFormData={initialCFRFormData}
                  setFormData={setCFRFormData}
                  initialCFRFormData={initialCFRFormData}
                  calculateBalanceRemaining={calculateBalanceRemaining}
                  validateField={validateField}
                  validateEstimatePaymentMethod={validateEstimatePaymentMethod}
                  validateBalancePaymentMethod={validateBalancePaymentMethod}
                  setCFRUnsaved={setCFRUnsaved}
                  handleTextChanges={handleTextChanges}
                />
              </>
                }
                <BottomButtonGroup 
                  save={save}
                  validateFields={validateFields}
                  requestState={requestState}
                  StateEnum={StateEnum}
                  formData={CFRFormData}
                  isNewCFRForm={isNewCFRForm}
                  isMinistry={isMinistry}
                  setCreateModalOpen={setCreateModalOpen}
                  disableNewCfrFormBtn={disableNewCfrFormBtn}
                />
              </div>
          </div>
        </Box>
        <StateChangeDialog   
          modalOpen={modalOpen}
          handleClose={handleClose}
          handleSave={handleSave}
          modalMessage={modalMessage}
          createModalOpen={createModalOpen}
          handleCreateClose={handleCreateClose}
          newCFRForm={newCFRForm}
        />
        <StatusChangeDialog 
          modalOpen={statusChangeModalOpen}
          handleClose={handleStatusChangeModalClose}
          handleSave={saveApplicationFeeTab}
          modalMessage={statusChangeModalMessage}
        />
    </div>
    );
  }