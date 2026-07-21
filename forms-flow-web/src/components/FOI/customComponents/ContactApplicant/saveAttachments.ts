import {
  getOSSHeaderDetails,
  saveFilesinS3,
} from "../../../../apiManager/services/FOI/foiOSSServices";

export interface SaveAttachmentsCtx {
  ministryCode: string;
  requestNumber?: string;
  requestId: number | string;
  dispatch: any;
}

export async function saveAttachmentsPure(
  attachmentfiles: any[],
  ctx: SaveAttachmentsCtx
): Promise<Array<{ filename: string; url: string }>> {
  const onlyFiles = attachmentfiles.filter((file: any) => file instanceof File);
  const fileInfoList = onlyFiles.map((file: any) => ({
    ministrycode: ctx.ministryCode,
    requestnumber: ctx.requestNumber ? ctx.requestNumber : `U-00${ctx.requestId}`,
    filestatustransition: "email-attachment",
    filename: file.filename ? file.filename : file.name,
  }));

  const attachments: Array<{ filename: string; url: string }> = [];
  if (onlyFiles.length === 0) {
    return attachments;
  }
  try {
    const response = await getOSSHeaderDetails(fileInfoList, ctx.dispatch);
    const headers: any[] = Array.isArray(response?.data) ? response.data : [];
    // Fail safe: if the OSS service returned a different number of headers
    // than files, we cannot trust index-based pairing (would mis-wire or
    // pass undefined to saveFilesinS3). Abort the whole batch and log —
    // the caller sees an empty attachments list rather than a silent
    // cross-request leak.
    if (headers.length !== onlyFiles.length) {
      // eslint-disable-next-line no-console
      console.error(
        `saveAttachmentsPure: OSS returned ${headers.length} headers for ${onlyFiles.length} files; aborting upload to prevent mis-pairing.`
      );
      return attachments;
    }
    for (let i = 0; i < headers.length; i++) {
      const header = headers[i];
      const _file = onlyFiles[i]; // index-based pairing — filenames may collide
      await saveFilesinS3(header, _file, ctx.dispatch, (_err: any, _res: any) => {
        if (_res === 200) {
          attachments.push({ filename: header.filename, url: header.filepath });
        }
      });
    }
  } catch (error) {
    // eslint-disable-next-line no-console
    console.log(error);
  }
  return attachments;
}
