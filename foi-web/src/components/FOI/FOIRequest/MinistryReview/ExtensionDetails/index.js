import React from "react";
import { ActionProvider } from "./ActionContext";
import ExtensionDetailsBox from "./ExtensionDetailsBox"
import { StateEnum } from "../../../../../constants/FOI/statusEnum";

const ExtensionDetails = React.memo(
  ({
    requestDetails,
    requestState
  }) => {

    const statusesToNotAppearIn = [
      StateEnum.unopened.name.toLowerCase(),
      StateEnum.intakeinprogress.name.toLowerCase(),
      StateEnum.redirect.name.toLowerCase(),
    ];

    if (!requestState || !!statusesToNotAppearIn.find(status => status === requestState.toLowerCase())) {
      return null;
    }

    return (
      <ActionProvider
        requestDetails={requestDetails}
      >
        <ExtensionDetailsBox 
        />
      </ActionProvider>
    );
  }
);

export default ExtensionDetails;