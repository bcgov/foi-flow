import React, { useState, useMemo } from 'react';
import { useDispatch, useSelector } from "react-redux";
import TextField from '@mui/material/TextField';
import InputAdornment from "@mui/material/InputAdornment";
import MenuItem from '@mui/material/MenuItem';
import './index.scss'
import { errorToast } from "../../../../helper/FOI/helper";
import { toast } from "react-toastify";
import type { params, Template } from './types';
import { fetchApplicantCorrespondence, saveEmailCorrespondence, fetchApplicantCorrespondenceTemplates } from "../../../../apiManager/services/FOI/foiCorrespondenceServices";
import _ from 'lodash';
import IconButton from '@material-ui/core/IconButton';
import Grid from "@material-ui/core/Grid";
import Paper from "@mui/material/Paper";
import SearchIcon from "@material-ui/icons/Search";
import InputBase from "@mui/material/InputBase";
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import { getFullnameList } from '../../../../helper/FOI/helper'
import CommentStructure from '../Comments/CommentStructure'
import AttachmentModal from '../Attachments/AttachmentModal';
import { getOSSHeaderDetails, saveFilesinS3, getFileFromS3 } from "../../../../apiManager/services/FOI/foiOSSServices";
import { dueDateCalculation } from '../../FOIRequest/BottomButtonGroup/utils';
import { PAYMENT_EXPIRY_DAYS } from "../../../../constants/FOI/constants";
import { PreviewModal } from './PreviewModal';
import { OSS_S3_BUCKET_FULL_PATH } from "../../../../constants/constants";
import Loading from "../../../../containers/Loading";
import {setFOICorrespondenceLoader} from "../../../../actions/FOI/foiRequestActions";

export const ContactApplicant = ({
  requestNumber,
  ministryId,
  ministryCode,
  requestId,
  applicantCorrespondence,
  applicantCorrespondenceTemplates,
}: any) => {

  const dispatch = useDispatch();
  const isCFRFormApproved: boolean = useSelector((state: any) => state.foiRequests.foiRequestCFRForm.status === 'approved');
  const isEstimatePaid: boolean = useSelector((state: any) => state.foiRequests.foiRequestCFRForm.feedata.estimatepaymentmethod !== '');
  const isLoading: boolean = useSelector((state: any) => state.foiRequests.isCorrespondenceLoading);
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
  const [templates, setTemplates] = useState<any[]>([{ value: "", label: "", templateid: null, text: "", disabled: true }]);

  React.useEffect(() => {
    let templateList: any = [
      { value: "", label: "", templateid: null, text: "", disabled: true },
      { value: "", label: "None", templateid: null, text: "", disabled: false }
    ];

    applicantCorrespondenceTemplates.forEach((item: any) => {
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
                disabled: !isCFRFormApproved || (item.name === 'PAYONLINE' && isEstimatePaid)
              }
              templateList.push(templateItem);
              setTemplates(templateList);
            });
          });
        }
      });
    });
  }, [isCFRFormApproved, isEstimatePaid]);

  const formHistory: Array<any> = useSelector((state: any) => state.foiRequests.foiRequestCFRFormHistory);
  const approvedForm = formHistory?.find(form => form?.status?.toLowerCase() === 'approved');
  const existingCorrespondence = applicantCorrespondence?.find((correspondence: any) => correspondence?.id === approvedForm?.cfrfeeid)
  const previewButtonValue = existingCorrespondence ? "Preview & Resend Email" : "Preview & Send Email";

  const [messages, setMessages] = useState(applicantCorrespondence);
  const [disablePreview, setDisablePreview] = useState(false);

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
  const [currentTemplate, setCurrentTemplate] = useState(0)

  const handleTemplateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCurrentTemplate(+e.target.value)
    setEditorValue(templates[+e.target.value].text || "")
  }

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((file, i) => i !== index))
  }

  const onFilterChange = (filterValue: string) => {
    let _filteredMessages = filterValue === "" ? applicantCorrespondence : applicantCorrespondence.filter((c: any) => c.text.toLowerCase().indexOf(filterValue.toLowerCase()) > -1)
    setMessages(_filteredMessages)
  }

  const saveAttachments = async () => {
    const fileInfoList = files?.map((file: any) => {
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
        const _file = files.find((file: any) => file.filename === header.filename);
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

  const save = async (emailContent: string) => {
    setDisablePreview(true);
    setPreviewModal(false);
    const attachments = await saveAttachments();
    let callback = (_res: string) => {
      setEditorValue("")
      setCurrentTemplate(0)
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
    const type = (templateId && [1, 2].includes(templateId)) ? "CFRFee" : "";
    let data = {
      templateid: currentTemplate ? templates[currentTemplate as keyof typeof templates].templateid : null,
      correspondencemessagejson: JSON.stringify({
        "emailhtml": editorValue,
        "id": approvedForm?.cfrfeeid,
        "type": type
      }),
      foiministryrequest_id: ministryId,
      attachments: attachments,
      attributes: [{ "paymentExpiryDate": dueDateCalculation(new Date(), PAYMENT_EXPIRY_DAYS) }]
    };
    saveEmailCorrespondence(
      data,
      requestId,
      ministryId,
      dispatch,
      callback,
      (errorMessage: string) => {
        errorToast(errorMessage)
        dispatch(setFOICorrespondenceLoader(false));
      },
    );
    setFOICorrespondenceLoader(false);
    setDisablePreview(false);
  };

  const [showEditor, setShowEditor] = useState(false)

  const [previewModal, setPreviewModal] = useState(false);
  const handlePreviewClose = () => {
    setPreviewModal(false);
  }

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
                id="foicommentfilter"
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
                  disabled={template.disabled}
                >
                  {template.label}
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
            isMinistryCoordinator={false}
            uploadFor={"email"}
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
            <PreviewModal
              modalOpen={previewModal}
              handleClose={handlePreviewClose}
              handleSave={save}
              innerhtml={editorValue}
              attachments={files}
              templateInfo={templates[currentTemplate]}
            />
            <button
              className="btn addCorrespondence"
              data-variant="contained"
              onClick={() => setPreviewModal(true)}
              color="primary"
              disabled={(files?.length <= 0 || currentTemplate <= 1 || disablePreview)}
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
      <div style={{ marginTop: '20px' }}>
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
              ministryId={ministryId}
            />
          </div>
        ))}
      </div>
    </div>
  ) : (
    <Loading />
  );
};
