import React, { useState, useMemo } from 'react';
import { useDispatch, useSelector } from "react-redux";
import TextField from '@mui/material/TextField';
import InputAdornment from "@mui/material/InputAdornment";
import MenuItem from '@mui/material/MenuItem';
import './index.scss'
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Box from '@mui/material/Box';
import Chip from '@mui/material/Chip';
import { errorToast, isMinistryLogin } from "../../../../helper/FOI/helper";
import type { params, CFRFormData } from './types';
import { calculateFees } from './util';
import foiFees from '../../../../constants/FOI/foiFees.json';
import { fetchApplicantCorrespondence, saveEmailCorrespondence } from "../../../../apiManager/services/FOI/foiCorrespondenceServices";
import { fetchCFRForm } from "../../../../apiManager/services/FOI/foiCFRFormServices";
import _ from 'lodash';
import { toast } from "react-toastify";
import { StateEnum } from '../../../../constants/FOI/statusEnum';
import { returnToQueue } from '../../../FOI/FOIRequest/BottomButtonGroup/utils';
import CustomizedTooltip from '../Tooltip/MuiTooltip/Tooltip';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import CloseIcon from '@material-ui/icons/Close';
import IconButton from '@material-ui/core/IconButton';
import Grid from "@material-ui/core/Grid";
import Paper from "@mui/material/Paper";
import SearchIcon from "@material-ui/icons/Search";
import InputBase from "@mui/material/InputBase";
import { SxProps } from '@mui/material';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import { getFullnameList } from '../../../../helper/FOI/helper'
import CommentStructure from '../Comments/CommentStructure'
import AttachmentModal from '../Attachments/AttachmentModal';
import { MimeTypeList, MaxFileSizeInMB } from "../../../../constants/FOI/enum";
import { getOSSHeaderDetails, saveFilesinS3, getFileFromS3 } from "../../../../apiManager/services/FOI/foiOSSServices";
import {dueDateCalculation} from '../../FOIRequest/BottomButtonGroup/utils';
import { PAYMENT_EXPIRY_DAYS} from "../../../../constants/FOI/constants";

export const ContactApplicant = ({
  requestNumber,
  requestState,
  ministryId,
  ministryCode,
  requestId,
  userDetail,
  applicantCorrespondence,
}: any) => {

  const dispatch = useDispatch();

  const userGroups = userDetail.groups.map((group: any) => group.slice(1));  
  const fullNameList = getFullnameList()

  const getFullname = (userid: string) => {
    let user = fullNameList.find((u: any) => u.username === userid);
    return user && user.fullname ? user.fullname : userid;
  }

  const getRequestNumber = () => {
    if (requestNumber)
      return `Request #${requestNumber}`;
    return `Request #U-00${requestId}`;
  }

  const handleContinueModal = (_value: any, _fileInfoList: any, files: any) => {
    setModal(false)
    if (files)
      setFiles(files)
  }


  const [openModal, setModal] = useState(false);
  function openAttachmentModal() {
    setModal(true);
  }
  const [files, setFiles] = useState([]);

  // const testTemplate;
  const fileInfoList = [{
    filename: "test.pdf",
    s3sourceuri: "https://citz-foi-prod.objectstore.gov.bc.ca/dev-forms-foirequests/TEMPLATES/EMAILS/fee_estimate_notification.html"
  }]
  React.useEffect(() => {
    fetchCFRForm(
      ministryId,
      dispatch,
    );
    getOSSHeaderDetails(fileInfoList, dispatch, (err: any, res: any) => {
      if (!err) {
        res.map(async (header: any, _index: any) => {
          getFileFromS3(header, async (_err: any, response: any) => {
            const text = await new Response(response.data).text()
          });
        });
      }
    });
  }, []);

  const formHistory: Array<any> = useSelector((state: any) => state.foiRequests.foiRequestCFRFormHistory);
  const approvedForm = formHistory?.find(form => form?.status?.toLowerCase() === 'approved');
  const existingCorrespondence = applicantCorrespondence?.find((correspondence: any) => correspondence?.id === approvedForm?.cfrfeeid)
  const previewButtonValue = existingCorrespondence ? "Preview & Resend Email" : "Preview & Send Email";

  const templates = {
    newestimate: {
      value: 'newestimate',
      label: 'New Estimate',
      templateid: 1,
      text: `<p>Dear {{firstName}} {{lastName}}</p>
      <p>Please see the attached regarding your FOI Request.</p>
      <p>If you would like to pay your estimate online, please click on this link:</p>
      <p><a href="{{cfrfee.feedata.paymenturl}}">Pay Online</a></p>
      <p><br></p>
      <p>Thank you,</p>
      <p>{{assignedToFirstName}} {{assignedToLastName}}</p>
      <p>{{assignedGroup}}</p>`
    },
    outstandingfee: {
      value: 'outstandingfee',
      label: 'Outstanding Fee',
      templateid: 2,
      text: `<div>
            <h4 style="color: #003366; display: block; text-align:center; font-family: 'BC Sans'; font-weight:bold">Freedom of Information and Protection for Privacy Act (FOIPPA)<br> Request for Records - Balance Due</h4>
            </div>

            <p>Dear {{firstName}} {{lastName}}</p>
            <p>Please see the attached regarding your FOI Request.</p>
            <p>If you would like to pay your remaining balance online, please click on this link: </p>
            <p>
              <a href="{{cfrfee.feedata.paymenturl}}">
                Pay Online
              </a>
            </p>
            <br>
            <p>Thank you,</p>
            <p>{{assignedToFirstName}} {{assignedToLastName}}</p>
            <p>{{assignedGroup}}</p>`
    },
    none: {
      value: 'none',
      label: 'None',
      templateid: null,
      text: ``
    }
  }

  const [messages, setMessages] = useState(applicantCorrespondence);

  React.useEffect(() => {
    setMessages(applicantCorrespondence);
  }, [applicantCorrespondence])

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
  const [currentTemplate, setCurrentTemplate] = useState('')

  const handleTemplateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCurrentTemplate(e.target.value)
    setEditorValue(templates[e.target.value as keyof typeof templates].text)
  }

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((file, i) => i !== index))
  }

  const saveAttachments = async () => {
    const fileInfoList = files?.map((file: any) => {
      return {
          ministrycode: ministryCode,
          requestnumber: requestNumber ? requestNumber : `U-00${requestId}`,
          filestatustransition: 'email-attachment',
          filename: file.filename? file.filename : file.name,
      }
    });
    let attachments: any = [];
    try {
      const response = await getOSSHeaderDetails(fileInfoList, dispatch);
      for (let header of response.data) {
        const _file = files.find((file: any) => file.filename === header.filename);
        await saveFilesinS3(header, _file, dispatch, (_err: any, _res: any) => {
          if (_res === 200) {
            attachments.push({filename: header.filename, url: header.filepath})
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

  const save = async () => {
    const attachments = await saveAttachments();
    let callback = (_res: string) => {
      setEditorValue("")
      setFiles([])
      setShowEditor(false)
      toast.success("Message has been sent to applicant successfully", {
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
    const type = (templateId && [1,2].includes(templateId)) ? "CFRFee": "";
    let data = {
      templateid: currentTemplate ? templates[currentTemplate as keyof typeof templates].templateid : null,
      correspondencemessagejson: JSON.stringify ({"emailhtml": editorValue,
                                  "id": approvedForm?.cfrfeeid,
                                  "type": type
                                  }),
      foiministryrequest_id: ministryId,
      attachments: attachments,
      attributes: [{"paymentExpiryDate": dueDateCalculation(new Date(), PAYMENT_EXPIRY_DAYS)}]
    };
    saveEmailCorrespondence(
      data,
      requestId,
      ministryId,
      dispatch,
      callback,
      (errorMessage: string) => {
        errorToast(errorMessage)
      },
    );
  };

  const [showEditor, setShowEditor] = useState(false)

  return (
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
        <Grid item xs={3}>
          <button
            className="btn addCorrespondence"
            data-variant="contained"
            onClick={() => setShowEditor(true)}
            color="primary"
          >
            + Add New Correspondence
          </button>
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
          // sx={{ display: "inline-block"}}
        >
          <Paper
            component={Grid}
            sx={{
              border: "1px solid #38598A",
              color: "#38598A",
              maxWidth:"100%"
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
              // sx={{
              //   borderRight: "2px solid #38598A",
              //   backgroundColor: "rgba(56,89,138,0.1)",
              // }}
            >
              <label className="hideContent">Search Correspondence</label>
              <InputBase
                id="foicommentfilter"
                placeholder="Search Correspondence ..."
                defaultValue={""}
                // onChange={(e: any)=>{oncommentfilterkeychange(e.target.value.trim())}}
                sx={{
                  color: "#38598A",
                }}
                startAdornment={
                  <InputAdornment position="start">
                    <IconButton
                      className="search-icon"
                      // sx={{ color: "#38598A" }}
                    >
                      <span className="hideContent">Search Correspondence ...</span>
                      <SearchIcon />
                    </IconButton>
                  </InputAdornment>
                }
                fullWidth
              />
            </Grid>
          </Paper>
        </Grid>
      </Grid>
      {!showEditor || <div>
        <Grid
          container
          direction="row"
          justify="flex-start"
          alignItems="flex-start"
          spacing={1}
        >
          <Grid item xs={9}>
          </Grid>
          <Grid item xs={3}>
            <TextField
              className="email-template-dropdown"
              id="emailtemplate"
              label={currentTemplate === '' ? "Select Template" : ""}
              inputProps={{ "aria-labelledby": "emailtemplate-label"}}
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
              {Object.keys(templates).map((option) => (
              <MenuItem
                key={templates[option as keyof typeof templates].value}
                value={templates[option as keyof typeof templates].value}
                // disabled={option.disabled}
              >
                {templates[option as keyof typeof templates].label}
              </MenuItem>
              ))}
            </TextField>
          </Grid>
        </Grid>
        <div className="correspondence-editor">
          <ReactQuill
            theme="snow"
            value={editorValue}
            onChange={setEditorValue}
            modules={quillModules}
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
          <AttachmentModal
            modalFor={"add"}
            openModal={openModal}
            handleModal={handleContinueModal}
            multipleFiles={true}
            requestNumber={requestNumber}
            requestId={requestId}
            attachmentsArray={files}
            existingDocuments={files}
            attachment={{}}
            handleRename={undefined}
          />
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
          </span>
          <div className="previewEmail">
            <button
              className="btn addCorrespondence"
              data-variant="contained"
              onClick={(e) => {
                save()
              }}
              color="primary"
            >
              {previewButtonValue}
            </button>
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
      <div style={{marginTop: '20px'}}>
        {messages.map((message: any, index: any) => (
          <div key={index} className="commentsection"
            data-msgid={index}
            style={{ display: 'block' }}
          >
            <CommentStructure
              i={message}
              reply={false}
              parentId={null}
              isreplysection={false}
              totalcommentCount={1}
              currentIndex={index}
              hasAnotherUserComment={false}
              fullName={getFullname(message.createdby)}
              isEmail={true}
            />
          </div>
        ))}
      </div>

    </div>
  );
}
