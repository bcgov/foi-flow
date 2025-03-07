import React from "react";
import { ActionProvider } from "./ActionContext";
import SearchComponent from "./SearchComponent";
import DataGridKeywordSearch from "./DataGridKeywordSearch";

const KeywordSearch = React.memo(({ userDetail }) => {
  return (
    <ActionProvider>
      <SearchComponent userDetail={userDetail} />
      <DataGridKeywordSearch userDetail={userDetail} />
    </ActionProvider>
  );
});

export default KeywordSearch;
