import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { Weather } from './Weather'



createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Weather />
  </StrictMode>,
)
