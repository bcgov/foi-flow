import React from "react";
import "./tooltip.scss";
import { styled } from '@mui/material/styles';
import Button from '@mui/material/Button';
import Tooltip, { TooltipProps, tooltipClasses } from '@mui/material/Tooltip';
import ClickAwayListener from '@mui/material/ClickAwayListener';

type TooltipParams = {
  content: {
    title: string;
    content: JSX.Element[];
  };
  position: string;
};

const HtmlTooltip = styled(({ className, ...props }: TooltipProps) => (
  <Tooltip {...props} classes={{ popper: className }} />
))(({ theme }) => ({
  [`& .${tooltipClasses.tooltip}`]: {
    backgroundColor: '#E5EAEF',
    color: 'rgba(0, 0, 0, 0.87)',
    width: 150,
    fontSize: theme.typography.pxToRem(12),
    border: '1px solid #38598A',
  },
}));


const CustomizedTooltip = ({
  content, position
}: TooltipParams) => {
  const defaultContent = {
    "title": "Tooltip title",
    "content": "Tooltip content"
  };

  const _content = (content && content["title"] && content["content"]) ? content : defaultContent;
  const _position: any = position ? position : "right-end";

  const [open, setOpen] = React.useState(false);

  const handleTooltipClose = () => {
    setOpen(false);
  };

  const handleTooltipOpen = () => {
    setOpen(true);
  };

  return (
    <ClickAwayListener onClickAway={handleTooltipClose}>
    <div className="customizedTooltip">
      <HtmlTooltip
        PopperProps={{
          disablePortal: true,
        }}
        onClose={handleTooltipClose}
        open={open}
        disableFocusListener
        disableHoverListener
        disableTouchListener
        placement={_position}
        title={
          <React.Fragment>
            <div className="tooltipTitle">{_content["title"]}</div>
            <div className="tooltipContent">{_content["content"]}</div>
          </React.Fragment>
        }
      >
        <Button onClick={handleTooltipOpen}>
          <img src="/assets/Images/infoicon.svg" style={{transform : position ? 'scaleX(-1)' : "none", cursor: "pointer"}} width="30px" alt="Infomation" />
        </Button>
      </HtmlTooltip>
    </div>
    </ClickAwayListener>
  );
};

export default CustomizedTooltip;
