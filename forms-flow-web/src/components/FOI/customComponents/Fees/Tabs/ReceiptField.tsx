import Popover from "@material-ui/core/Popover";
import MenuList from "@material-ui/core/MenuList";
import IconButton from "@material-ui/core/IconButton";
import MoreHorizIcon from "@material-ui/icons/MoreHoriz";
import MenuItem from "@mui/material/MenuItem";
import { useState } from "react";

export const ReceiptField = ({
  receipt,
  getReceiptFile,
  formData,
  setFormData,
}: any) => {
  const [popoverOpen, setPopoverOpen] = useState(false);
  const [anchorPosition, setAnchorPosition] = useState<any>(null);

  const ActionsPopover = () => {
    return (
      <Popover
        anchorReference="anchorPosition"
        anchorPosition={
          anchorPosition && {
            top: anchorPosition.top,
            left: anchorPosition.left,
          }
        }
        open={popoverOpen}
        anchorOrigin={{
          vertical: "top",
          horizontal: "left",
        }}
        transformOrigin={{
          vertical: "top",
          horizontal: "left",
        }}
        onClose={() => setPopoverOpen(false)}
      >
        <MenuList>
          <MenuItem
            onClick={() => {
              getReceiptFile(
                receipt?.receiptfilename,
                receipt?.receiptfilepath,
                true
              );
              setPopoverOpen(false);
            }}
          >
            Download
          </MenuItem>

          <MenuItem
            onClick={() => {
              getReceiptFile(
                receipt?.receiptfilename,
                receipt?.receiptfilepath,
                false
              );
              setPopoverOpen(false);
            }}
          >
            Open in new tab
          </MenuItem>

          <MenuItem
            onClick={() => {
              setFormData((values: any) => ({
                ...values,
                ["receipts"]: [
                  ...formData?.receipts.filter(
                    (r: any) => r.receiptfilename != receipt.receiptfilename
                  ),
                  { ...receipt, isactive: false },
                ],
              }));
              setPopoverOpen(false);
            }}
          >
            Delete
          </MenuItem>
        </MenuList>
      </Popover>
    );
  };

  return receipt.isactive ? (
    <>
      <div className="col-lg-12 foi-details-col application-fee-receipt">
        <u
          className="receipt-link"
          onClick={() => {
            getReceiptFile(receipt?.receiptfilename, receipt?.receiptfilepath);
          }}
        >
          {receipt.receiptfilename
            ? receipt.receiptfilename
            : "view online payment receipt"}
        </u>
        <i>
          <IconButton
            className={"receipt-popover"}
            aria-label="actions"
            id={`ellipse-icon-${receipt.receiptfilename}`}
            key={`ellipse-icon-${receipt.receiptfilename}`}
            color="primary"
            disabled={false}
            onClick={(e) => {
              setPopoverOpen(true);
              setAnchorPosition(e.currentTarget.getBoundingClientRect());
            }}
          >
            <MoreHorizIcon />
          </IconButton>
        </i>
        <ActionsPopover />
      </div>
    </>
  ) : (
    <></>
  );
};
