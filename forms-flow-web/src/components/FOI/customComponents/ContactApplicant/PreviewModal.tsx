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
  const [html, setHtml] = useState("");
  const [newhtml, setNewhtml] = useState("");
  const [htmlArray, setHtmlArray] = useState<string[]>([]);
  const fileInfoList = [{
    filename: "fee_estimate_notification.html",
    s3sourceuri: "https://citz-foi-prod.objectstore.gov.bc.ca/dev-forms-foirequests/TEMPLATES/EMAILS/fee_estimate_notification.html"
  }]
  React.useEffect(() => {
    getOSSHeaderDetails(fileInfoList, dispatch, (err: any, res: any) => {
      if (!err) {
        res.map(async (header: any, _index: any) => {
          getFileFromS3(header, async (_err: any, response: any) => {
            let temphtml = await new Response(response.data).text();
            setHtml( `${temphtml}` );
          });
        });
      }
    });

  }, []);

  React.useEffect(() => {
    setHtmlArray( html.split(`<body style="color:black; font-family: 'BC Sans';">`) );

    let tempHtml = innerhtml.replace("{{firstName}}", requestDetails.firstName)
      .replace("{{lastName}}", requestDetails.lastName)
      .replace("{{assignedToFirstName}}", requestDetails.assignedToFirstName)
      .replace("{{assignedToLastName}}", requestDetails.assignedToLastName)
      .replace("{{assignedGroup}}", requestDetails.assignedGroup);
  
    setNewhtml( `${htmlArray?.length>0?htmlArray[0]:"<html>"} <body style="color:black; font-family: 'BC Sans';"> ${tempHtml} </body></html>` );
  }, [innerhtml]);

  const handleSend = () => {
    handleSave(newhtml);
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
            <Frame initialContent={newhtml} className="preview-frame" >
            </Frame>

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
