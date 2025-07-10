import React from "react";
import { ActionProvider } from "./ActionContext";
import SearchComponent from "./SearchComponent";
import EventQueue from "./EventQueue"

const EventQueueSearch = React.memo(({ userDetail, eventQueueTableInfo }) => {
  return (
    <ActionProvider>
      <SearchComponent userDetail={userDetail} />
      <EventQueue userDetail={userDetail} eventQueueTableInfo={eventQueueTableInfo} />
    </ActionProvider>
  );
});

export default EventQueueSearch