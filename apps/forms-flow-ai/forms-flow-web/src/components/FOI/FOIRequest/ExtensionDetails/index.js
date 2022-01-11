import React, { useState } from "react";
import { useParams } from "react-router-dom";
import { ActionProvider } from "./ActionContext";
import ExtensionDetailsBox from "./ExtensionDetailsBox"
import { StateEnum } from "../../../../constants/FOI/statusEnum";
const ExtensionDetails = React.memo(
  ({
    requestDetails,
  }) => {

    const { requestState } = useParams();

    const statusesToNotAppearIn = [
      StateEnum.unopened.name.toLowerCase(),
      StateEnum.onhold.name.toLowerCase(),
      StateEnum.closed.name.toLowerCase(),
    ];

    if (!requestState || requestState.toLowerCase() in statusesToNotAppearIn) {
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