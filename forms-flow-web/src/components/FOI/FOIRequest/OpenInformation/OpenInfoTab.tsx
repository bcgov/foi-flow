import "./openinfo.scss";
import { Typography } from "@material-ui/core";

const OpenInfoTab = ({ tabValue, handleTabSelect, isOIUser }: any) => {
  
  return (
    <div className="openinfotab">
      <div
        className={tabValue === 1 ? "openinfotab-selected" : "openinfotab-select"}
      >
        <Typography
          onClick={() => handleTabSelect(1)}
          id="exemption-tab"
          // disabled={!isOIUser}
        >Exemption</Typography>
      </div>
      <div
        className={tabValue === 2 ? "openinfotab-selected" : "openinfotab-select"}
        >
        <Typography
          onClick={() => handleTabSelect(2)}
          id="openinformation-tab"
          // disabled={!isOIUser}
        >Open Information</Typography>
      </div>
    </div>
  );
};

export default OpenInfoTab;
