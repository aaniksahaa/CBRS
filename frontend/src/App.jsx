import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import Home from './Home'
import { BrowserRouter, HashRouter, Route, Routes } from 'react-router-dom'

import Demo from './Demo'

function App() {
  return (
    <>
      <HashRouter>
        <Routes>
          <Route path="" Component={Home}/>
          <Route path="/demo" Component={Demo}/>
        </Routes>
      </HashRouter>
    </>
  )
}

export default App


