import React from "react";
import ReactDOM from "react-dom";
import App from "./components/App";
import StoreService from "./services/StoreService";
import './styles.scss';

const store = StoreService.configureStore();
const history = StoreService.history;

console.log("hello, world!);

ReactDOM.render(<App {...{ store, history }} />, document.getElementById("app"));
