import { createContext, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { setEventQueueParams } from "../../../../actions/FOI/foiRequestActions";

export const ActionContext = createContext();
ActionContext.displayName = "EventQueueContext";

export const ActionProvider = ({ children }) => {
  const dispatch = useDispatch();

  const eventQueueParams = useSelector((state) => state.foiRequests.eventQueueParams);

  const [eventSearchParams, setEventSearchParams] = useState({
    dateRangeType: "",
    fromDate: "",
    toDate: "",
  });

  const [showEventQueueTable, setShowEventQueueTable] = useState(false);

  const handleUpdateSearchFilter = (filterParams) => {
    setEventSearchParams(filterParams);

    setShowEventQueueTable(true);

    dispatch(setEventQueueParams({
      ...eventQueueParams,
      rowsState: { ...eventQueueParams.rowsState, page: 0 },
      dateFilter: {
        dateRangeType: filterParams.dateRangeType,
        fromDate: filterParams.fromDate,
        toDate: filterParams.toDate,
      }
    }));
  };

  return (
    <ActionContext.Provider
      value={{
        handleUpdateSearchFilter,
        eventSearchParams,
        showEventQueueTable,
        setShowEventQueueTable
      }}
    >
      {children}
    </ActionContext.Provider>
  );
};
