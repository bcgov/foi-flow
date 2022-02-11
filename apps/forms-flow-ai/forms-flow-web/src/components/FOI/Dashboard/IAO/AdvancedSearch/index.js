import React from "react";
import { ActionProvider } from "./ActionContext";
import SearchComponent from "./SearchComponent";

const AdvancedSearch = React.memo(() => {
  return (
    <ActionProvider>
      <SearchComponent />
    </ActionProvider>
  );
});

export default AdvancedSearch;
