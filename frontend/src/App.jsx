import { useEffect } from "react";
import "./App.css";
import { BrowserRouter, Route, Routes, useLocation } from "react-router-dom";

import Home from "./Home";
import NotFound from "./NotFound";
import Demo from "./Demo";

function ScrollToTop() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return null;
}

function App() {
  return (
    <>
      <BrowserRouter>
        <ScrollToTop />
        <Routes>
          <Route path="/" Component={Home} />
          <Route path="/demo" Component={Demo} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </>
  );
}

export default App;
