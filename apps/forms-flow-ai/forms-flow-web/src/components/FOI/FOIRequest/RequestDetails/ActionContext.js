import React, { createContext, useEffect, useState } from "react";
import { useDispatch } from "react-redux";
export const ActionContext = createContext();
export const ActionProvider = ({
  children,
}) => {
  const dispatch = useDispatch();

  const [modalOpen, setModalOpen] = useState()

  return (
    <ActionContext.Provider
      value={{
        setModalOpen: setModalOpen,
      }}
    >
      {children}
    </ActionContext.Provider>
  );
};
