import React from "react";
import { ActionProvider } from "./ActionContext";
import SearchComponent from "./SearchComponent";
import DataGridAdvancedSearch from "./DataGridAdvancedSearch";

const AdvancedSearch = React.memo(({ userDetail }) => {
  return (
    <ActionProvider>
      <SearchComponent userDetail={userDetail} />
      <DataGridAdvancedSearch userDetail={userDetail} />
    </ActionProvider>
  );
});

export default AdvancedSearch;
