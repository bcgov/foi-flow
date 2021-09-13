import React from "react";
import ReactDOM from "react-dom";
import App from "./components/App";
import StoreService from "./services/StoreService";
import './styles.scss';

// disable react-dev-tools for this project
if (typeof window.__REACT_DEVTOOLS_GLOBAL_HOOK__ === "object") {
  for (let [key, value] of Object.entries(window.__REACT_DEVTOOLS_GLOBAL_HOOK__)) {
    window.__REACT_DEVTOOLS_GLOBAL_HOOK__[key] = typeof value == "function" ? ()=>{} : null;
  }
}

const store = StoreService.configureStore();
const history = StoreService.history;

ReactDOM.render(<App {...{ store, history }} />, document.getElementById("app"));