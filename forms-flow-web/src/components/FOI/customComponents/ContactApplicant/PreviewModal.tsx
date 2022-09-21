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
import Frame from 'react-frame-component';
import type { previewParams } from './types';
import { getOSSHeaderDetails, getFileFromS3 } from "../../../../apiManager/services/FOI/foiOSSServices";
import { renderTemplate } from './util';

export const PreviewModal = React.memo(({
  modalOpen,
  handleClose,
  handleSave,
  innerhtml,
  attachments
}: previewParams) => {

  const dispatch = useDispatch();

  //gets the request detail from the store
  const requestDetails: any = useSelector((state: any) => state.foiRequests.foiRequestDetail);

  //get template - it's better to pass as prop than download from s3 - need integrate with parent component
  const [template, setTemplate] = useState("");
  const fileInfoList = [{
    filename: "fee_estimate_notification.html",
    s3sourceuri: "https://citz-foi-prod.objectstore.gov.bc.ca/dev-forms-foirequests/TEMPLATES/EMAILS/fee_estimate_notification.html"
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

  const templateVariables = [
    {name: "{{firstName}}", value: requestDetails.firstName},
    {name: "{{lastName}}", value: requestDetails.lastName},
    {name: "{{assignedToFirstName}}", value: requestDetails.assignedToFirstName},
    {name: "{{assignedToLastName}}", value: requestDetails.assignedToLastName},
    {name: "{{assignedGroup}}", value: requestDetails.assignedGroup},
  ];

  const handleSend = () => {
    handleSave(innerhtml);
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
            <Frame initialContent={ renderTemplate(template, innerhtml, templateVariables) } className="preview-frame" sandbox="allow-same-origin" >
            </Frame>
            {/* <iframe srcDoc={newTemplate} className="preview-frame" /> */}

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
        <button className="btn-bottom btn-save" onClick={handleSend}>
          Send Email
        </button>
        <button className="btn-bottom btn-cancel" onClick={handleClose}>
          Cancel
        </button>
      </DialogActions>
    </Dialog>
  </div>

  )
})
