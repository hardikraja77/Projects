import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import Routes1 from './Routes1'



createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Routes1 />
  </StrictMode>,
)
