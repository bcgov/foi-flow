import { useRef, useEffect } from "react";
export const ShadowHtmlComponent = ({ html }) => {
  const containerRef = useRef(null);
  const shadowRootRef = useRef(null);

  useEffect(() => {
    if (containerRef.current && !shadowRootRef.current) {
      shadowRootRef.current = containerRef.current.attachShadow({
        mode: "open",
      });
    }

    if (shadowRootRef.current) {
      shadowRootRef.current.innerHTML = html;
    }
  }, [html]);

  return <div ref={containerRef}></div>;
};
