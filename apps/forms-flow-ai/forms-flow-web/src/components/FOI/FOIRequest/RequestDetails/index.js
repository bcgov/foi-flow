import React, { useState } from "react";
import { ActionProvider } from "./ActionContext";
import RequestDetailsBox from "./RequestDetailsBox"

const RequestDetails = React.memo(
  ({
    requestDetails,
  }) => {

    return (
      <ActionProvider
        requestDetails={requestDetails}
      >
        <RequestDetailsBox 
        />
      </ActionProvider>
    );
  }
);

export default RequestDetails;