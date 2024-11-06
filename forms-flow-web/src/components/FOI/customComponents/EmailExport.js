import React, { useContext, useState, useRef } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

import 'react-quill/dist/quill.snow.css';
import draftToHtml from 'draftjs-to-html';

import { getOSSHeaderDetails, getFileFromS3 } from "../../../apiManager/services/FOI/foiOSSServices";
import { saveAs } from "file-saver";
import { downloadZip } from "client-zip";
import { useDispatch } from "react-redux";
import * as html2pdf from 'html-to-pdf-js';
import { toast } from "react-toastify";
import {useSelector } from "react-redux";
import {formatDate, formatDateInPst } from "../../../helper/FOI/helper";
const EmailExport = ({handleExport, content}) => {

  const dispatch = useDispatch();
  const user = useSelector((reduxState) => reduxState.user.userDetail);

  const download = async () => {
    const attachments = await handleExport();
    let fileInfoList = attachments.map(attachment => {
      return  {
        filename: attachment.filename,
        s3sourceuri: attachment.url
      }
    })
        let blobs = [];
        try {
          const response = await getOSSHeaderDetails(fileInfoList, dispatch);
          for (let header of response.data) {
            await getFileFromS3(header, (_err, res) => {
              let blob = new Blob([res.data], {type: "application/octet-stream"});
              blobs.push({name: header.filename, lastModified: res.headers['last-modified'], input: blob})
            });
          }
        } catch (error) {
          console.log(error)
        }
        html2pdf().from(content).outputPdf('blob').then(async (blob) => {
          blobs.push({name: "Email Body.pdf", lastModified: new Date(), input: blob})
          const zipfile = await downloadZip(blobs).blob()
          toast.success("Message has been exported successfully", {
            position: "top-right",
            autoClose: 3000,
            hideProgressBar: true,
            closeOnClick: true,
            pauseOnHover: true,
            draggable: true,
            progress: undefined,
          }); 
          saveAs(zipfile, user?.preferred_username + " | " + formatDateInPst(new Date(), "yyyy MMM dd | hh:mm aa") + ".zip");
        });
  }

  return (
    <>
    <button 
        className="btn-bottom btn-save" 
        onClick={() => {
          download();
      }}
        >
          Export as PDF
        </button>
    </>
  )

}

export default EmailExport