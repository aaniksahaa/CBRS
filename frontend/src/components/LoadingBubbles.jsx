import React from "react";
import ReactLoading from "react-loading";
import { primary_dark } from "../Config";

const LoadingBubbles = () => {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
      }}
    >
      <ReactLoading
        type={"spinningBubbles"}
        color={primary_dark}
        height={150}
        width={150}
      />
    </div>
  );
};

export default LoadingBubbles;
