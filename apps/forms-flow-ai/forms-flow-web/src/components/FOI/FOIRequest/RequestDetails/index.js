import React, { useState } from "react";
import { ActionProvider } from "./ActionContext";
import RequestDetailsBox from "."

const RequestDetails = React.memo(
  ({
    requestDetails,
  }) => {

    return (
      <ActionProvider>
        <RequestDetailsBox 
          requestDetails={requestDetails} 
        />
      </ActionProvider>
    );
  }
);

export default RequestDetails;