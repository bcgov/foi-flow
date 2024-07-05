import React, {useState} from 'react';
import { useDispatch, useSelector } from "react-redux";
import Grid from "@material-ui/core/Grid";
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import type { previewParams } from './types';
import { getOSSHeaderDetails, getFileFromS3 } from "../../../../apiManager/services/FOI/foiOSSServices";
import { renderTemplate, applyVariables, getTemplateVariables } from './util';
import { OSS_S3_BUCKET_FULL_PATH, FOI_FFA_URL } from "../../../../constants/constants";
import { EmailExport } from '../../../FOI/customComponents';


export const PreviewModal = React.memo(({
  modalOpen,
  handleClose,
  handleSave,
  innerhtml,
  handleExport,
  attachments,
  templateInfo,
  enableSend
}: previewParams) => {

  const dispatch = useDispatch();

  //gets the request detail from the store
  const requestDetails: any = useSelector((state: any) => state.foiRequests.foiRequestDetail);
  const requestExtensions: any = useSelector((state: any) => state.foiRequests.foiRequestExtesions);

  //get template
  const rootpath = OSS_S3_BUCKET_FULL_PATH
  const templatePath = "/TEMPLATES/EMAILS/header_footer_template.html";
  const [template, setTemplate] = useState("");
  const fileInfoList = [{
    filename: "header_footer_template.html",
    s3sourceuri: rootpath+templatePath
  }]
  React.useEffect(() => {
    getOSSHeaderDetails(fileInfoList, dispatch, (err: any, res: any) => {
      if (!err) {
        res.map(async (header: any, _index: any) => {
          getFileFromS3(header, async (_err: any, response: any) => {
            let html = await new Response(response.data).text();
            setTemplate( `${html}` );
          });
        });
      }
    });
  }, []);
  requestDetails["ffaurl"] = FOI_FFA_URL;
  const templateVariables = getTemplateVariables(requestDetails, requestExtensions, templateInfo);
  const handleSend = () => {
    handleSave( applyVariables(innerhtml, templateVariables) );
  };

  

  return (

    <div className="state-change-dialog">        
    <Dialog
      open={modalOpen}
      onClose={handleClose}
      aria-labelledby="state-change-dialog-title"
      aria-describedby="state-change-dialog-description"
      maxWidth={'md'}
      fullWidth={true}
    >
      <DialogTitle disableTypography id="state-change-dialog-title">
          <h2 className="state-change-header">Preview Applicant Email</h2>
          <IconButton aria-label= "close" onClick={handleClose}>
            <CloseIcon />
          </IconButton>
        </DialogTitle>
      <DialogContent>
        <DialogContentText id="state-change-dialog-description" component={'span'}>
          <div className="preview-container">
            <iframe srcDoc={ renderTemplate(template, innerhtml, templateVariables) } className="preview-frame" sandbox="allow-same-origin" />
          </div>
          <div className="preview-container">
            {attachments.map((file: any, index: number) => (
              <div key={file.filename}>
                <u>{file.filename}</u>
              </div>
            ))}
          </div>
        </DialogContentText>
      </DialogContent>
      <DialogActions>
      { !enableSend && 
        <EmailExport 
          handleExport={handleExport}
          content={innerhtml}
        />
      }
      { enableSend && 
        <button 
        className="btn-bottom btn-save" 
        disabled={!enableSend}
        onClick={handleSend}
        >
          Send Email
        </button>
      }
        <button className="btn-cancel" onClick={handleClose}>
          Cancel
        </button>
      </DialogActions>
    </Dialog>
  </div>

  )
})
