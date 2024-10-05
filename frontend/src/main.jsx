import * as React from "react";
import { ChakraProvider } from "@chakra-ui/react";
import * as ReactDOM from "react-dom/client";
import App from "./App";
import { ToastContainer, toast, Zoom, Slide } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const rootElement = document.getElementById("root");
ReactDOM.createRoot(rootElement).render(
  //<React.StrictMode>
  <ChakraProvider
    toastOptions={{
      defaultOptions: {
        isClosable: "true",
        duration: 3000,
        position: "top-right",
        colorScheme: "whatsapp",
      },
    }}
  >
    <App />
    <ToastContainer
      position="top-right"
      newestOnTop
      autoClose={3000}
      theme="colored"
      transition={Slide}
    />
  </ChakraProvider>
  // <App />
  //</React.StrictMode>,
);
