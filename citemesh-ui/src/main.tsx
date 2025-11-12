import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import App from './App.tsx'
import Login from './pages/Login.tsx'
import Dashboard from './pages/Dashboard.tsx'
import Search from './pages/Search.tsx'
import ScholarSearch from './pages/ScholarSearch.tsx'
import Library from './pages/Library.tsx'
import Network from './pages/Network.tsx'
import Chat from './pages/Chat.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/search" element={<Search />} />
        <Route path="/scholar-search" element={<ScholarSearch />} />
        <Route path="/library" element={<Library />} />
        <Route path="/network" element={<Network />} />
        <Route path="/chat" element={<Chat />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
