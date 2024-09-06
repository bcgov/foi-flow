import React, { useState, useMemo, useRef, useCallback, useEffect } from 'react';
import { useDispatch, useSelector } from "react-redux";
import TextField from '@mui/material/TextField';
import InputAdornment from "@mui/material/InputAdornment";
import MenuItem from '@mui/material/MenuItem';
import './index.scss'
import { errorToast, getFullnameList } from "../../../../helper/FOI/helper";
import { toast } from "react-toastify";
import type { Template } from './types';
import { fetchApplicantCorrespondence, saveEmailCorrespondence, saveDraftCorrespondence, 
  editDraftCorrespondence, deleteDraftCorrespondence, deleteResponseCorrespondence, saveCorrespondenceResponse, 
  editCorrespondenceResponse} from "../../../../apiManager/services/FOI/foiCorrespondenceServices";
import _ from 'lodash';
import IconButton from '@material-ui/core/IconButton';
import Grid from "@material-ui/core/Grid";
import Paper from "@mui/material/Paper";
import SearchIcon from "@material-ui/icons/Search";
import InputBase from "@mui/material/InputBase";
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import CommunicationStructure from './CommunicationStructure'
import AttachmentModal from '../Attachments/AttachmentModal';
import { getOSSHeaderDetails, saveFilesinS3, getFileFromS3 } from "../../../../apiManager/services/FOI/foiOSSServices";
import { dueDateCalculation } from '../../FOIRequest/BottomButtonGroup/utils';
import { PAYMENT_EXPIRY_DAYS } from "../../../../constants/FOI/constants";
import { PreviewModal } from './PreviewModal';
import { OSS_S3_BUCKET_FULL_PATH } from "../../../../constants/constants";
import Loading from "../../../../containers/Loading";
import {setFOICorrespondenceLoader} from "../../../../actions/FOI/foiRequestActions";
import { applyVariables, getTemplateVariables, getTemplateVariablesAsync, isFeeTemplateDisabled, getExtensionType } from './util';
import { StateEnum } from '../../../../constants/FOI/statusEnum';
import CustomizedTooltip from '../Tooltip/MuiTooltip/Tooltip';
import { CorrespondenceEmail } from '../../../FOI/customComponents';
import { Stack } from '@mui/material';
import { ClickableChip } from '../../Dashboard/utils';
import { List, ListItem, ListItemText } from '@material-ui/core';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import CloseIcon from '@material-ui/icons/Close';

export const ContactApplicant = ({
  requestNumber,
  requestState,
  ministryId,
  ministryCode,
  applicantCorrespondence,
  applicantCorrespondenceTemplates,
  requestId,
}: any) => {

  const dispatch = useDispatch();
  const currentCFRForm: any = useSelector((state: any) => state.foiRequests.foiRequestCFRForm);
  const isLoading: boolean = useSelector((state: any) => state.foiRequests.isCorrespondenceLoading);
  const responsePackagePdfStitchStatus = useSelector((state: any) => state.foiRequests.foiPDFStitchStatusForResponsePackage);
  const check: any = useSelector((state: any) => state.foiRequests);
  const cfrFeeData = useSelector((state: any) => state.foiRequests.foiRequestCFRFormHistory);
  const fullNameList = getFullnameList()
  const [modalFor, setModalFor] = useState("add")

  const getFullname = (userid: string) => {
    let user = fullNameList.find((u: any) => u.username === userid);
    return user && user.fullname ? user.fullname : userid;
  }

  const getRequestNumber = () => {
    if (requestNumber)
      return `Request #${requestNumber}`;
    return `Request #U-00${requestId}`;
  }

  const handleContinueModal = (_value: any, _fileInfoList: any, _files: any) => {
    setModal(false)
    if (_files)
      setFiles(_files)    
  }

  const [openModal, setModal] = useState(false);
  const [communicationUploadModalOpen, setCommunicationUploadModalOpen] = useState(false);
  
  const [openConfirmationModal, setOpenConfirmationModal] = useState(false);
  const [confirmationFor, setConfirmationFor] = useState("");
  const [confirmationTitle, setConfirmationTitle] = useState("");
  const [confirmationMessage, setConfirmationMessage] = useState("");
  const [selectedCorrespondence, setSelectedCorrespondence] = useState <any> ({});
  const [currentResponseDate, setCurrentResponseDate] = useState <any> ("");
  const [extension, setExtension] = useState("");

  const openAttachmentModal = () => { 
    setUploadFor("email");
    setModal(true);
  }

  const openResponseModal = () => {
    setFiles([]);
    setEditorValue("")
    setCurrentTemplate(0)
    setUploadFor("response");
    setModalFor("add");
    setModal(true);  
    setShowEditor(false);  
  }

  const addCorrespondence = () => {
    changeCorrespondenceFilter("drafts")
    setShowEditor(true);
    setModal(false);
    setEditMode(false);
    setFiles([]);
    setEditorValue("");
    setSelectedCorrespondence({});
    setSelectedEmails([]);
    setCurrentTemplate(0);
    
  }

  const  cancelCorrespondence = () => {
    if (currentTemplate> 0) {
      setOpenConfirmationModal(true);
      setConfirmationFor("cancel-correspondence");
      setConfirmationTitle("Cancel")
      setConfirmationMessage("Any unsaved changes will be lost.Are you sure you want to proceed? ");
    } else {
      setShowEditor(false);
    }
  }
  
  const  clearcorrespondence = () => {
    setShowEditor(false);
    setModal(false);
    setEditMode(false);
    setFiles([]);
    setEditorValue("");
    setSelectedCorrespondence({});
    setCorrespondenceId(null);
    setSelectedEmails([]);
    setCurrentTemplate(0);
  }

  const handleConfirmationClose = () => {     
    setConfirmationFor("");
    setConfirmationMessage("");
    setSelectedCorrespondence({});
    setOpenConfirmationModal(false);
  }

  const handleConfirmationContinue = () => { 
    setConfirmationFor("");
    setConfirmationMessage("");
    setOpenConfirmationModal(false);
    if (confirmationFor === "delete-draft") {
      deleteDraftAction();
    } else if (confirmationFor === "cancel-correspondence") {
      clearcorrespondence();
    } else if (confirmationFor === "delete-response") {
      deleteResponseAction();
    }
  }

  const formHistory: Array<any> = useSelector((state: any) => state.foiRequests.foiRequestCFRFormHistory);
  const approvedForm = formHistory?.find(form => form?.status?.toLowerCase() === 'approved');
  const existingCorrespondence = applicantCorrespondence?.find((correspondence: any) => correspondence?.id === approvedForm?.cfrfeeid)
  //const previewButtonValue = existingCorrespondence ? "Preview & Resend" : "Preview & Send";
  const previewButtonValue = "Preview & Send";
  const [editMode, setEditMode] = useState(false);
  const draftButtonValue = editMode ? "Save Draft Edits" : "Save Draft";

  const requestDetails: any = useSelector((state: any) => state.foiRequests.foiRequestDetail);
  const requestExtensions: any = useSelector((state: any) => state.foiRequests.foiRequestExtesions);
  
  const [files, setFiles] = useState([]);
  const [templates, setTemplates] = useState<any[]>([{ value: "", label: "", templateid: null, text: "", disabled: true, created_at:"" }]);

  const isEnabledTemplate = (item: any) => {
   if (['PAYONLINE', 'PAYOUTSTANDING'].includes(item.name)) { 
      return !isFeeTemplateDisabled(currentCFRForm, item); 
   } else if (['EXTENSIONS-PB'].includes(item.name)) {
      return getExtensionType(requestDetails, requestExtensions) === "PB";
   } else if (['OIPCAPPLICANTCONSENTEXTENSION'].includes(item.name)) {
    const isApplicantConsent = getExtensionType(requestDetails, requestExtensions) === "OIPCAPPLICANTCONSENTEXTENSION"
      return isApplicantConsent;
   } else if(['OIPCFIRSTTIMEEXTENSION'].includes(item.name)){
    const isFirstTimeExtension = getExtensionType(requestDetails, requestExtensions) === "OIPCFIRSTTIMEEXTENSION"
      return isFirstTimeExtension;
   } else if(['OIPCSUBSEQUENTTIMEEXTENSION'].includes(item.name)){
    const isSubsequentTimeExtension = getExtensionType(requestDetails, requestExtensions) === "OIPCSUBSEQUENTTIMEEXTENSION"
      return isSubsequentTimeExtension;
   } else if(['GENERICCOVEREMAILTEMPLATE'].includes(item.name)){
      return true;
   } else if(['ACKNOWLEDGEMENTLETTER'].includes(item.name)){
    if (requestDetails.currentState === "Intake in Progress" || requestDetails.currentState === "Open") {
      return true;
    }
   }
  }

  const isduplicate = (item: string) => {
    for(const element of templates) {
      if (element.value === item) {
          return true;
          }
      }
      return false;
  }

  useEffect(() => { 
    // Add templates being used in drafts to the list
    const listOfDraftTemplates: number[] = [];
    applicantCorrespondence.forEach((draftCorrespondence: any) => {
      if (draftCorrespondence.templateid && !listOfDraftTemplates.includes(draftCorrespondence.templateid)) {
        listOfDraftTemplates.push(draftCorrespondence.templateid);
      }
    })
    applicantCorrespondenceTemplates.forEach((item: any) => {
      setTemplates([{ value: "", label: "", templateid: null, text: "", disabled: true, created_at:"" }]);
      if (isEnabledTemplate(item) || listOfDraftTemplates.includes(item.templateid)) {
      const rootpath = OSS_S3_BUCKET_FULL_PATH
      const fileInfoList = [{
        filename: item.name,
        s3sourceuri: rootpath + item.documenturipath
      }]

      getOSSHeaderDetails(fileInfoList, dispatch, (err: any, res: any) => {
        if (!err) {
          res.map(async (header: any, _index: any) => {
            getFileFromS3(header, async (_err: any, response: any) => {
              let templateItem: Template = {
                value: item.name,
                label: item.description,
                templateid: item.templateid,
                text: await new Response(response.data).text(),
                disabled: false,
                created_at: item.created_at
              }
              if (!isduplicate(item.name)) {
              //setTemplates((oldArray) => [...oldArray, templateItem]); 
              setTemplates((oldArray) => {
                // Check if the templateItem already exists in the array
                const exists = oldArray.some(item => item.templateid === templateItem.templateid);
                if (!exists) {
                  return [...oldArray, templateItem];
                }
                return oldArray;
              }); 
              }
            });            
          });
        }
      });
    }
    });
  }, [applicantCorrespondence, applicantCorrespondenceTemplates, requestExtensions, dispatch]);


  const [correspondences, setCorrespondences] = useState(applicantCorrespondence);
  const [uploadFor, setUploadFor] = useState("email");

  const [disablePreview, setDisablePreview] = useState(false);
  const [correspondenceFilter, setCorrespondenceFilter] = useState("log");
  const changeCorrespondenceFilter = (filter: string) => {
    if (filter === correspondenceFilter) return;
    setCorrespondenceFilter(filter.toLowerCase());
    if(filter !== 'drafts'){
      setShowEditor(false);
    }
  }

  useEffect(() => {
    let filteredCorrespondences = applicantCorrespondence.filter((message: any) => {
      if (correspondenceFilter === "log") {
        return [ "correspondence","response"].includes(message.category);
      } else if (correspondenceFilter === "templates") {
        return message.category === "template";
      } else if (correspondenceFilter === "drafts") {
        return message.category === "draft";
      }
    })
    setCorrespondences(filteredCorrespondences);
  }, [correspondenceFilter, applicantCorrespondence])

  const quillModules = useMemo(() => {
    return {
      toolbar: {
        container: "#correspondence-editor-ql-toolbar",
        handlers: {
          link: openAttachmentModal,
        }
      }
    };
  }, []);

  const [editorValue, setEditorValue] = useState("")
  const [currentTemplate, setCurrentTemplate] = useState(0)
  const [selectedEmails, setSelectedEmails] = useState([]);
  // Create a ref to store the Quill instance
  const quillRef = useRef(null);

  // Callback function to handle the reference to the Quill editor
  const handleRef = useCallback((ref) => {
    // If the ref is not null, set up the Quill instance
    if (ref) {
      const quill = ref.getEditor();

      // Enable spellcheck for the Quill editor
      quill.root.setAttribute('spellcheck', true);

      // Store the Quill ref in the current variable
      quillRef.current = ref;
    }
  }, []);

  const handleTemplateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCurrentTemplate(+e.target.value)
    
    const callback = (templateVariables: any) => {
      const finalTemplate = applyVariables(templates[+e.target.value].text || "", templateVariables);
      setEditorValue(finalTemplate)
    }
    getTemplateVariablesAsync(requestDetails, requestExtensions, responsePackagePdfStitchStatus, cfrFeeData, templates[+e.target.value], callback);
  }

  //When templates are selected from list
  const handleTemplateSelection = (index: number) => {
    setCurrentTemplate(index);
    
    const callback = (templateVariables: any) => {
      const finalTemplate = applyVariables(templates[index].text || "", templateVariables);
      setEditorValue(finalTemplate);
      changeCorrespondenceFilter("log");
      setShowEditor(true);
    }
    getTemplateVariablesAsync(requestDetails,requestExtensions, responsePackagePdfStitchStatus, cfrFeeData, templates[index], callback);
  }

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((file, i) => i !== index))
  }

  const onFilterChange = (filterValue: string) => {
    
    const getTemplateName = (templateId: any) => {
      return applicantCorrespondenceTemplates.find((obj: any)=> obj.templateid == templateId)?.description
    }
    if(filterValue === "") {
      setCorrespondences(applicantCorrespondence);
    } else{
      let _filteredMessages = applicantCorrespondence.filter((corr: any) => {
        // Filter through template names, and for responses include "applicant response"
        const templateName = getTemplateName(corr.templateid)
        if(templateName && templateName.toLowerCase().indexOf(filterValue.toLowerCase()) >= 0) {
          return corr;
        } 
        if(corr.category == "response" && "applicant response".indexOf(filterValue.toLowerCase()) >= 0) {
          return corr;
        }
      })
      setCorrespondences(_filteredMessages);
      
    }
 }

  const saveAttachments = async (attachmentfiles: any) => {
    const fileInfoList = attachmentfiles?.map((file: any) => {
      return {
        ministrycode: ministryCode,
        requestnumber: requestNumber ? requestNumber : `U-00${requestId}`,
        filestatustransition: 'email-attachment',
        filename: file.filename ? file.filename : file.name,
      }
    });
    let attachments: any = [];
    try {
      const response = await getOSSHeaderDetails(fileInfoList, dispatch);
      for (let header of response.data) {
        const _file = attachmentfiles.find((file: any) => file.filename === header.filename);
        await saveFilesinS3(header, _file, dispatch, (_err: any, _res: any) => {
          if (_res === 200) {
            attachments.push({ filename: header.filename, url: header.filepath })
            console.log("success")
          }
          else {
            console.log("failure")
          }
        })
      }
    } catch (error) {
      console.log(error)
    }
    return attachments
  }

  const save = async (emailContent: string, skiptoast=false) => {
    setDisablePreview(true);
    setPreviewModal(false);
    const attachments = await saveAttachments(files);
    let callback = (_res: string) => {
      clearcorrespondence();
      if (!skiptoast) {
        toast.success("Message has been sent to applicant successfully", {
        position: "top-right",
        autoClose: 3000,
        hideProgressBar: true,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
      });
    }
      dispatch(fetchApplicantCorrespondence(requestId, ministryId));
    }
    const templateId = currentTemplate ? templates[currentTemplate as keyof typeof templates].templateid : null;
    const type = (templateId && [1, 2].includes(templateId)) ? "CFRFee" : "";
    let israwrequest = selectedCorrespondence.israwrequest || false;
    let data = {
      templateid: currentTemplate ? templates[currentTemplate as keyof typeof templates].templateid : null,
      correspondenceid:correspondenceId,
      correspondencemessagejson: JSON.stringify({
        "emailhtml": emailContent,
        "id": approvedForm?.cfrfeeid,
        "type": type
      }),
      emails: selectedEmails,
      foiministryrequest_id: ministryId,
      attachments: attachments,
      attributes: [{ 
        "paymentExpiryDate": dueDateCalculation(new Date(), PAYMENT_EXPIRY_DAYS),
        "axisRequestId": requestNumber
      }],
      assignedGroupEmail: requestDetails.assignedGroupEmail,
      israwrequest: israwrequest
    };
    saveEmailCorrespondence(
      data,
      requestId,
      ministryId,
      dispatch,
      callback,
      (errorMessage: string) => {
        errorToast(errorMessage);
        clearcorrespondence();
        dispatch(setFOICorrespondenceLoader(false));
      },
    );
    setFOICorrespondenceLoader(false);
    setDisablePreview(false);
  };

  

  const saveDraft = async () => {
    setDisablePreview(true);
    setPreviewModal(false);
    const attachments = await saveAttachments(files);
    let callback = (_res: string) => {
      changeCorrespondenceFilter("drafts");
      clearcorrespondence();      
      toast.success("Message has been saved to draft successfully", {
        position: "top-right",
        autoClose: 3000,
        hideProgressBar: true,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
      });
      dispatch(fetchApplicantCorrespondence(requestId, ministryId));
    }
    const templateId = currentTemplate ? templates[currentTemplate as keyof typeof templates].templateid : null;
    const type = (templateId && [1, 2].includes(templateId)) ? "CFRFee" : "";
    let israwrequest = selectedCorrespondence?.israwrequest ||
      requestDetails.requeststatuslabel == StateEnum.appfeeowing.label ||
      requestDetails.requeststatuslabel == StateEnum.intakeinprogress.label ||
      requestDetails.requeststatuslabel == StateEnum.unopened.label
    let data = {
      templateid: currentTemplate ? templates[currentTemplate as keyof typeof templates].templateid : null,
      correspondencemessagejson: JSON.stringify({
        "emailhtml": editorValue,
        "id": approvedForm?.cfrfeeid,
        "type": type
      }),
      foiministryrequest_id: ministryId,
      attachments: attachments,
      emails: selectedEmails,
      israwrequest: israwrequest
    };
    saveDraftCorrespondence(
      data,
      requestId,
      ministryId,
      dispatch,
      callback,
      (errorMessage: string) => {
        clearcorrespondence();
        changeCorrespondenceFilter("drafts");
        dispatch(fetchApplicantCorrespondence(requestId, ministryId));
      },
    );
    setFOICorrespondenceLoader(false);
    setDisablePreview(false);
    return attachments;
  };

  const saveExport = async () => {
    setDisablePreview(true);
    setPreviewModal(false);
    const attachments = await saveAttachments(files);
    let callback = (_res: string) => {
      clearcorrespondence();
      changeCorrespondenceFilter("log");      
      dispatch(fetchApplicantCorrespondence(requestId, ministryId));
    }
    const templateId = currentTemplate ? templates[currentTemplate as keyof typeof templates].templateid : null;
    const type = (templateId && [1, 2].includes(templateId)) ? "CFRFee" : "";
    let israwrequest = selectedCorrespondence.israwrequest || false;
    let data = {
      templateid: currentTemplate ? templates[currentTemplate as keyof typeof templates].templateid : null,
      correspondenceid:correspondenceId,
      correspondencemessagejson: JSON.stringify({
        "emailhtml": editorValue,
        "id": approvedForm?.cfrfeeid,
        "type": type
      }),
      foiministryrequest_id: ministryId,
      attachments: attachments,
      emails: [],
      attributes: [{ 
        "paymentExpiryDate": dueDateCalculation(new Date(), PAYMENT_EXPIRY_DAYS),
        "axisRequestId": requestNumber
      }],
      israwrequest: israwrequest
    };
    saveEmailCorrespondence(
      data,
      requestId,
      ministryId,
      dispatch,
      callback,
      (errorMessage: string) => {
        errorToast(errorMessage);
        clearcorrespondence();
        dispatch(setFOICorrespondenceLoader(false));
      },
    );
    setFOICorrespondenceLoader(false);
    setDisablePreview(false);
    return attachments;
  };


  const saveResponse = async (_value: any, _fileInfoList: any, _files: any) => {
    if (_files) {
      setFiles(_files);
      setDisablePreview(true);
      setPreviewModal(false);
      const responseattachments = await saveAttachments(_files);
      let callback = (_res: string) => {
        const toastID = toast.loading("Saving response...")
        toast.update(toastID, {
          type: "success",
          render: "Response successfully saved.",
          position: "top-right",
          isLoading: false,
          autoClose: 3000,
          hideProgressBar: true,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
          progress: undefined,
        });
        clearcorrespondence();
        changeCorrespondenceFilter("log");
        dispatch(fetchApplicantCorrespondence(requestId, ministryId));
      }
      let israwrequest = ministryId ? false : true;
      let data = {
        attachments: responseattachments,
        israwrequest: israwrequest
      };
      saveCorrespondenceResponse(
        data,
        ministryId,
        requestId,
        dispatch,
        callback,
        (errorMessage: string) => {
          const toastID = toast.loading("Saving response...")
          toast.update(toastID, {
            type: errorMessage ? "error" : "success",
            render: errorMessage ? "Response upload failed" : "Response successfully saved.",
            position: "top-right",
            isLoading: false,
            autoClose: 3000,
            hideProgressBar: true,
            closeOnClick: true,
            pauseOnHover: true,
            draggable: true,
            progress: undefined,
          });
          clearcorrespondence();
          changeCorrespondenceFilter("log");
          dispatch(fetchApplicantCorrespondence(requestId, ministryId));
        },
      );
      setFOICorrespondenceLoader(false);
      setDisablePreview(false);      
    }
    clearcorrespondence();
    changeCorrespondenceFilter("log");
  };



  const [correspondenceId, setCorrespondenceId] = useState(null);

  const editDraft = async (i : any) => {
    setSelectedCorrespondence(i);
    setEditMode(true);
    setShowEditor(true);
    setEditorValue(i.text);
    setSelectedEmails(i.emails);
    if (i.attachments)
      setFiles(i.attachments);
    setCorrespondenceId(i.applicantcorrespondenceid);
    for(let j = 0; j < templates.length; j++) {
      if (templates[j].templateid === i.templateid) {
        setCurrentTemplate(+j);
      } 
    }
  };

  const deleteDraft = (i : any) => {
    setSelectedCorrespondence(i);
    setOpenConfirmationModal(true);
    setConfirmationFor("delete-draft")
    setConfirmationTitle("Delete Draft")
    setConfirmationMessage("Are you sure you want to delete these draft(s)? This can not be undone");
  }


  const deleteDraftAction = async () => {
    if (selectedCorrespondence) {
    setCorrespondenceId(selectedCorrespondence.applicantcorrespondenceid);
    setDisablePreview(true);
    setPreviewModal(false);
    let callback = (_res: string) => {
      clearcorrespondence();
      changeCorrespondenceFilter("drafts");
      toast.success("Draft has been deleted successfully", {
        position: "top-right",
        autoClose: 3000,
        hideProgressBar: true,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
      });
      dispatch(fetchApplicantCorrespondence(requestId, ministryId));
    }
    deleteDraftCorrespondence(selectedCorrespondence.applicantcorrespondenceid, selectedCorrespondence.israwrequest, ministryId,requestId,
      dispatch,
      callback,
      (errorMessage: string) => {
        clearcorrespondence();
        changeCorrespondenceFilter("drafts");
        dispatch(fetchApplicantCorrespondence(requestId, ministryId));
        setFOICorrespondenceLoader(false);
        setDisablePreview(false);
      },
    );
    setFOICorrespondenceLoader(false);
    setDisablePreview(false);
    setEditMode(false);
      
  }
  };

  const deleteResponse = (i : any) => {
    setSelectedCorrespondence(i);
    setOpenConfirmationModal(true);
    setConfirmationFor("delete-response")
    setConfirmationTitle("Delete Response")
    setConfirmationMessage("Are you sure you want to delete this response? This can not be undone");
  }

  const deleteResponseAction = () => {
    if (selectedCorrespondence) {
      setCorrespondenceId(selectedCorrespondence.applicantcorrespondenceid);
      setDisablePreview(true);
      setPreviewModal(false);
      let callback = (_res: string) => {
        setEditorValue("");
        setCurrentTemplate(0);
        setFiles([]);
        setSelectedEmails([]);
        setShowEditor(false)
        setEditMode(false);
        setSelectedCorrespondence({});
        toast.success("Response has been deleted successfully", {
          position: "top-right",
          autoClose: 3000,
          hideProgressBar: true,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
          progress: undefined,
        });
        dispatch(fetchApplicantCorrespondence(requestId, ministryId));
      }
      deleteResponseCorrespondence(selectedCorrespondence.applicantcorrespondenceid,selectedCorrespondence.israwrequest, ministryId,requestId,
        dispatch,
        callback,
        (errorMessage: string) => {
          setEditorValue("");
          setCurrentTemplate(0);
          setFiles([]);
          setSelectedEmails([]);
          setShowEditor(false);
          setEditMode(false);
          setSelectedCorrespondence({});
          dispatch(fetchApplicantCorrespondence(requestId, ministryId));
          setFOICorrespondenceLoader(false);
          setDisablePreview(false);
        },
      );
      setFOICorrespondenceLoader(false);
      setDisablePreview(false);
      setEditMode(false);
    }
  }

  const editCorrespondence = async (i : any) => {
    setDisablePreview(true);
    setPreviewModal(false);
    const attachments = await saveAttachments(files);
    let callback = (_res: string) => {
      clearcorrespondence();
      changeCorrespondenceFilter("drafts");
      toast.success("Message has been saved to draft successfully", {
        position: "top-right",
        autoClose: 3000,
        hideProgressBar: true,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
      })
      dispatch(fetchApplicantCorrespondence(requestId, ministryId));
    }
    const templateId = currentTemplate ? templates[currentTemplate as keyof typeof templates].templateid : null;
    const type = (templateId && [1, 2].includes(templateId)) ? "CFRFee" : "";
    let israwrequest = selectedCorrespondence.israwrequest || false;
    let data = {
      correspondenceid:correspondenceId,
      templateid: currentTemplate ? templates[currentTemplate as keyof typeof templates].templateid : null,
      correspondencemessagejson: JSON.stringify({
        "emailhtml": editorValue,
        "id": approvedForm?.cfrfeeid,
        "type": type
      }),
      foiministryrequest_id: ministryId,
      attachments: attachments,
      emails: selectedEmails,
      israwrequest: israwrequest
    };
    editDraftCorrespondence(
      data,
      requestId,
      ministryId,
      dispatch,
      callback,
      (errorMessage: string) => {
        errorToast(errorMessage);
        clearcorrespondence();
        changeCorrespondenceFilter("drafts");
        dispatch(setFOICorrespondenceLoader(false));
      },
    );
    setFOICorrespondenceLoader(false);
    setDisablePreview(false);
    return attachments;
  };
  const [updateAttachment, setUpdateAttachment] = useState<any>({});

  const handleRename = (_attachment: any, newFilename: string) => {
    setModal(false);
    let correspondenceAttachmentId = selectedCorrespondence.attachments[0].applicantcorrespondenceattachmentid;
    let correspondenceId = selectedCorrespondence.applicantcorrespondenceid;

    if (updateAttachment.filename !== newFilename) {
      editCorrespondenceResponse(
        { filename: newFilename, correspondenceattachmentid: correspondenceAttachmentId, correspondenceid: correspondenceId, israwrequest: selectedCorrespondence.israwrequest }, 
        ministryId, 
        requestId, 
        dispatch,
        () => {
          setSelectedCorrespondence({})
          dispatch(fetchApplicantCorrespondence(requestId, ministryId));
          toast.success("Attachment has been renamed successfully", {
            position: "top-right",
            autoClose: 3000,
            hideProgressBar: true,
            closeOnClick: true,
            pauseOnHover: true,
            draggable: true,
            progress: undefined,
          })
        },
        (errorMessage: string) => {
          errorToast(errorMessage);
          console.log('Error saving new filename: ', errorMessage)}
      );
    }
  }

  const handleChangeResponseDate = (newDate: string) => {
    setModal(false);
    editCorrespondenceResponse(
      {responsedate: newDate, correspondenceid: selectedCorrespondence.applicantcorrespondenceid, israwrequest: selectedCorrespondence.israwrequest}, 
      ministryId, 
      requestId, 
      dispatch, 
      () => {
        setSelectedCorrespondence({})
        setModalFor("add");
        dispatch(fetchApplicantCorrespondence(requestId, ministryId));
        toast.success("Date has been changed successfully", {
          position: "top-right",
          autoClose: 3000,
          hideProgressBar: true,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
          progress: undefined,
        })
      }, 
      (errorMessage: string) => {
        errorToast(errorMessage);
        console.log('Error updating response date: ', errorMessage)}
    )
  }
  const [showEditor, setShowEditor] = useState(false)

  const [previewModal, setPreviewModal] = useState(false);
  const handlePreviewClose = () => {
    setPreviewModal(false);
  }

  const tooltipPreview = {
    "title": previewButtonValue,
    "content": [
      <div className="toolTipContent">
        <p>Please select a template and add an attachment before previewing the email</p>
      </div>]
  };

  
  let correspondenceList;
  correspondenceList = correspondences.map((message: any, index: any) => (
    <div key={index} className="commentsection"
      data-msgid={index}
      style={{ display: 'block' }}
    >
      <CommunicationStructure
        correspondence={message}
        currentIndex={index}
        fullName={getFullname(message.createdby)}
        ministryId={ministryId}
        editDraft={editDraft}
        deleteDraft={deleteDraft}
        deleteResponse={deleteResponse}
        modalFor={modalFor}
        setModalFor={setModalFor}
        setModal={setModal}
        setSelectedCorrespondence={setSelectedCorrespondence}
        setCurrentResponseDate={setCurrentResponseDate}
        setUpdateAttachment={setUpdateAttachment}
        applicantCorrespondenceTemplates={applicantCorrespondenceTemplates}
        templateVariableInfo={{requestDetails, requestExtensions, responsePackagePdfStitchStatus, cfrFeeData}}
      />
    </div>
  ))


  let templatesList;
  const parser = new DOMParser();
  let templateListItems = templates.map((template: any, index: any) => {
    if (template.label !== "") {
    let lastItemInList = false
    if (templates.length === index + 1) lastItemInList = true;
    const htmlEmail = parser.parseFromString(template.text, 'text/html');
    const htmlEmailText = htmlEmail.body.textContent || ''
    let ellipses = htmlEmailText?.length > 300 ? '...' : ''

    return (
      <ListItem  
        onClick={() => {
          if (!showEditor) setShowEditor(true)
          handleTemplateSelection(index)
        }} 
        className={`template-list-item ${lastItemInList ? 'template-list-item-last' : ''}`}
        key={template.value}
      >
        <Grid container spacing={2}>
          <Grid item xs={8}>
            <ListItemText primary={template.label}/>
          </Grid>
          <Grid item xs={4}>
          <ListItemText secondary={template.created_at}/>
          </Grid>
        </Grid>
      </ListItem>
      )
      }
    })
  templatesList = (
    <List>
      {templateListItems}
    </List>)

  return !isLoading ? (
    <div className="contact-applicant-container">
      <Grid
        container
        direction="row"
        justify="flex-start"
        alignItems="flex-start"
        spacing={1}
      >
        <Grid item xs={6}>
          <h1 className="foi-review-request-text foi-ministry-requestheadertext">
            {getRequestNumber()}
          </h1>
        </Grid>
        <Grid item xs={3}>
          {/* <ConditionalComponent condition={hasDocumentsToExport}>
            <button
              className="btn addAttachment foi-export-button"
              variant="contained"
              onClick={downloadAllDocuments}
              color="primary"
            >
              Export All
            </button>
          </ConditionalComponent> */}
        </Grid>
        <Grid container xs={3} direction="row" justifyContent='flex-end'>
          <TextField
            className="btn addCorrespondence"
            color="primary"
            id="add-correspondence"
            label="+ Add New"
            inputProps={{ "aria-labelledby": "correspondence-label" }}
            InputLabelProps={{ shrink: false, style: {color: 'white'} }}
            select
            variant="outlined"
            size="small"
            fullWidth
          >
            <MenuItem
              onClick={() => addCorrespondence()}
              key='messagetoapplicant'
              disabled={false}
              sx={{ display: "flex" }}
            >
              Message to Applicant
            </MenuItem>
            <MenuItem
              onClick={() => openResponseModal()}
              key='attachresponse'
              disabled={false}
              sx={{ display: "flex" }}
            >
              Attach Response
            </MenuItem>
          </TextField>
        </Grid>
      </Grid>
      <Grid
        container
        direction="row"
        justify="flex-start"
        alignItems="flex-start"
        spacing={1}
      >
        <Grid
          item
          container
          alignItems="center"
          xs={12}
          className="search-grid-container"
        >
          <Paper
            component={Grid}
            sx={{
              border: "1px solid #38598A",
              color: "#38598A",
              maxWidth: "100%"
            }}
            alignItems="center"
            justifyContent="center"
            direction="row"
            container
            item
            xs={12}
            elevation={0}
          >
            <Grid
              item
              container
              alignItems="center"
              direction="row"
              xs={true}
              className="search-grid"
            >
              <label className="hideContent">Search Correspondence</label>
              <InputBase
                id="foicorrespondencefilter"
                placeholder="Search Correspondence ..."
                defaultValue={""}
                onChange={(e: any) => { onFilterChange(e.target.value.trim()) }}
                sx={{
                  color: "#38598A",
                }}
                startAdornment={
                  <InputAdornment position="start">
                    <IconButton
                      className="search-icon"
                    >
                      <span className="hideContent">Search Correspondence ...</span>
                      <SearchIcon />
                    </IconButton>
                  </InputAdornment>
                }
                fullWidth
              />
            </Grid>
            <Stack direction="row" sx={{ overflowX: "hidden" }} spacing={1} alignItems="center" justifyContent="center" px={1}>
              <ClickableChip
                id="correspondenceLog"
                key={`correspondence-log`}
                label={"LOG"}
                color="primary"
                size="small"
                onClick={() => changeCorrespondenceFilter("log")}
                clicked={correspondenceFilter === "log"}
              />
              <ClickableChip
                id="correspondenceTemplates"
                key={`correspondence-templates`}
                label={"TEMPLATES"}
                color="primary"
                size="small"
                onClick={() => changeCorrespondenceFilter("templates")}
                clicked={correspondenceFilter === "templates"}
              />
              <ClickableChip
                id="correspondenceDrafts"
                key={`correspondence-drafts`}
                label={"DRAFTS"}
                color="primary"
                size="small"
                onClick={() => changeCorrespondenceFilter("drafts")}
                clicked={correspondenceFilter === "drafts"}
              />
            </Stack>
          </Paper>
        </Grid>
      </Grid>
      {!showEditor || <div>
        <Grid
          container
          direction="row"
          justifyContent="flex-end"
          spacing={1}
        >
          <Grid item xs={'auto'}>
          </Grid>          
          <Grid item xs={3}>
            <TextField
              className="email-template-dropdown"
              id="emailtemplate"
              label={currentTemplate === 0 ? "Select Template" : ""}
              inputProps={{ "aria-labelledby": "emailtemplate-label" }}
              InputLabelProps={{ shrink: false }}
              select
              name="emailtemplate"
              value={currentTemplate}
              onChange={handleTemplateChange}
              placeholder="Select Template"
              variant="outlined"
              margin='normal'
              size="small"
              fullWidth
            >
              {templates.map((template: any, index: any) => (
                <MenuItem
                  key={index}
                  value={index}
                >
                  {template.label}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={'auto'}>
          <CorrespondenceEmail 
            ministryId={ministryId}
            requestId={requestId}
            selectedEmails={selectedEmails}
            setSelectedEmails={setSelectedEmails}
            defaultEmail={requestDetails.email}
          />
          </Grid>
        </Grid>
        <div className="correspondence-editor">
          <div className="closeDraft">
              <IconButton className="title-col3" onClick={()=>setShowEditor(false)}>
                  <i className="dialog-close-button">Close</i>
                  <CloseIcon />
              </IconButton>
           </div>
          <ReactQuill
            theme="snow"
            value={editorValue}
            onChange={setEditorValue}
            modules={quillModules}
            ref={handleRef}
          />
          {files.map((file: any, index: number) => (
            <div className="email-attachment-item" key={file.filename}>
              <u>{file.filename}</u>
              <i
                className="fa fa-times-circle"
                onClick={() => removeFile(index)}
              >
              </i>
            </div>
          ))}          
        </div>
        <div id="correspondence-editor-ql-toolbar" className="ql-toolbar ql-snow">
          <span className="ql-formats">
            <button className="ql-bold" />
            <button className="ql-italic" />
            <button className="ql-underline" />
          </span>
          <span className="ql-formats">
            <button className="ql-list" value="ordered" />
            <button className="ql-list" value="bullet" />
          </span>
          <span className="ql-formats">
            <button className="ql-link" />
            <button className="ql-image" />
          </span>
          <div className="previewEmail">
            <PreviewModal
              modalOpen={previewModal}
              handleClose={handlePreviewClose}
              handleSave={save}
              innerhtml={editorValue}
              handleExport={saveExport}
              attachments={files}
              templateInfo={templates[currentTemplate]}
              enableSend={selectedEmails.length > 0}
            />  
            {/*
            <button
            className="btn addCorrespondence"
            data-variant="contained" 
            onClick={cancelCorrespondence}             
            color="primary"
          >
            Cancel
          </button>     
          */ }    
        <button
          className="btn addCorrespondence"
          data-variant="contained" 
          onClick={ editMode ? editCorrespondence : saveDraft}             
          color="primary"
          disabled={(currentTemplate <= 0)}
        >
          {draftButtonValue}
        </button>
            <button
              className="btn addCorrespondence"
              data-variant="contained"
              onClick={() => setPreviewModal(true)}
              color="primary"
              disabled={(currentTemplate <= 0)}
            >
              {previewButtonValue}
            </button>
            <div className="tooltip-floatRight tooltip-preview">
              <CustomizedTooltip content={tooltipPreview} position={""} />
              <p className="hideContent" id="popup-1">Information1</p>
            </div>
          </div>
        </div>
        <Grid
          container
          direction="row"
          justify="flex-start"
          alignItems="flex-start"
          spacing={1}
        >
          <Grid item xs={10}>
          </Grid>
          <Grid item xs={2}>
          </Grid>
        </Grid>
      </div>}
      <div style={{ marginTop: '20px' }}>
        {(correspondenceFilter === "log" || correspondenceFilter === "drafts") && correspondenceList}
        {correspondenceFilter === "templates" && templatesList}
      </div>
      <AttachmentModal
      modalFor={modalFor}
      openModal={openModal}
      handleModal={uploadFor === "response" ? saveResponse : handleContinueModal}
      multipleFiles={true}
      requestNumber={requestNumber}
      requestId={requestId}
      attachmentsArray={files}
      existingDocuments={files}
      attachment={updateAttachment}//{{}}
      handleRename= {handleRename} //{undefined}
      handleReclassify={undefined}
      handleChangeResponseDate={handleChangeResponseDate}
      isMinistryCoordinator={false}
      uploadFor={uploadFor}
      maxNoFiles={uploadFor === "response" ? 1 : 10}
      bcgovcode={undefined}
      currentResponseDate={currentResponseDate}
    /> 
    <div className="email-change-dialog">
      <Dialog
        open={openConfirmationModal}
        onClose={handleConfirmationClose}
        aria-labelledby="state-change-dialog-title"
        aria-describedby="state-change-dialog-description"
        maxWidth={'md'}
        fullWidth={true}
        // id="state-change-dialog"
      >
        <DialogTitle disableTypography id="state-change-dialog-title">
            <h2 className="state-change-header">{confirmationTitle}</h2>
            <IconButton className="title-col3" onClick={handleConfirmationClose}>
              <i className="dialog-close-button">Close</i>
              <CloseIcon />
            </IconButton>
          </DialogTitle>
        <DialogContent className={'dialog-content-nomargin'}>
          <DialogContentText id="state-change-dialog-description" component={'span'}>
          <span className="confirmation-message">
              {confirmationMessage}
            </span>
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <button
            className={`btn-bottom btn-save btn`}
            onClick={handleConfirmationContinue}
          >
            Continue
          </button>
          <button className="btn-cancel" onClick={handleConfirmationClose}>
            Cancel
          </button>
        </DialogActions>
      </Dialog>
    </div>
    </div>
  ) : (
    <Loading />
  );
};
