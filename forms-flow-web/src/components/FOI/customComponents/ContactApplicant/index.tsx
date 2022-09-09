import React, { useState } from 'react';
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
import { fetchCFRForm, saveCFRForm } from "../../../../apiManager/services/FOI/foiCFRFormServices";
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
import { any } from 'prop-types';

export const ContactApplicant = ({
  requestNumber,
  requestState,
  ministryId,
  requestId,
  userDetail,
}: any) => {

  const dispatch = useDispatch();

  const userGroups = userDetail.groups.map((group: any) => group.slice(1));

  const fullNameList = getFullnameList()

  const getFullname = (userid: string) => {
    let user = fullNameList.find((u: any) => u.username === userid);
    return user && user.fullname ? user.fullname : userid;
  }

  const getRequestNumber = ()=> {
    if (requestNumber)
      return `Request #${requestNumber}`;
    return `Request #U-00${requestId}`;
  }

  const templates = {
    newestimate: {
      value: 'newestimate',
      label: 'New Estimate',
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
      text: `<p>Dear {{firstName}} {{lastName}}</p>
      <p>Please see the attached regarding your FOI Request.</p>
      <p>If you would like to pay your remaining balance online, please click on this link: </p>
      <p><a href="{{cfrfee.feedata.paymenturl}}">Pay Online</a>
      </p>
      <br>
      <p>Thank you,</p>
      <p>{{assignedToFirstName}} {{assignedToLastName}}</p>
      <p>{{assignedGroup}}</p>`
    },
    none: {
      value: 'none',
      label: 'None',
      text: ``
    }
  }

  const messages = [
    {
      userid: 'nichkan@idir',
      date: "2022 Sep 07 | 03:42 PM",
      dateUF: "2022-09-07T22:42:59.830945+00:00",
      text: `<p>Dear {{firstName}} {{lastName}},</p>
      <p>Please see the attached regarding your FOI Request.</p>
      <p>If you would like to pay your remaining balance online, please click on this link: </p>
      <p><a href="http://www.google.com">Pay Online</a>
      </p>
      <br>
      <p>Thank you,</p>
      <p>{{assignedToFirstName}} {{assignedToLastName}}</p>
      <p>{{assignedGroup}}</p>`,
    },
    {
      userid: 'richaqi@idir',
      date: "2022 Sep 07 | 03:42 PM",
      dateUF: "2022-09-07T22:42:59.830945+00:00",
      text: `Some other text`,
    }
  ]

  const [editorValue, setEditorValue] = useState("")
  const [currentTemplate, setCurrentTemplate] = useState('')

  const handleTemplateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCurrentTemplate(e.target.value)
    setEditorValue(templates[e.target.value as keyof typeof templates].text)
  }

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
            modules={{toolbar: {container: "#correspondence-editor-ql-toolbar"}}}
          />
          <div>Attaachment 1</div>
          <div>Attaachment 2</div>
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
                console.log(editorValue);
                setShowEditor(false)
              }}
              color="primary"
            >
              Preview & Send Email
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
        {messages.map((message, index) => (
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
              fullName={getFullname(message.userid)}
              isEmail={true}
            />
          </div>
        ))}
      </div>

    </div>
  );
}
