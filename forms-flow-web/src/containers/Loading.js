import React from "react";

const Loading = React.memo(({ costumStyle }) => (
  <img
    className="loader"
    src="/spinner.gif"
    alt="Loading ..."
    style={costumStyle}
  />
));
export default Loading;

