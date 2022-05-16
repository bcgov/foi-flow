import React from "react";
import "./tooltip.scss";
import Popup from 'reactjs-popup';


const Tooltip = ({
  content, position
}) => {
  const defaultContent = {
    "title": "Tooltip title",
    "content": "Tooltip content"
  };

  const _content = (content && content["title"] && content["content"]) ? content : defaultContent;
  const _position = position ? position : "bottom left";

  return (
    <Popup className="tooltip" trigger={<img src="/assets/Images/infoicon.svg" width="30px" alt="Infomation" />} position={_position}>
      <div className="tooltipTitle">{_content["title"]}</div>
      <div className="tooltipContent">{_content["content"]}</div>
    </Popup>
  );
};

export default Tooltip;
