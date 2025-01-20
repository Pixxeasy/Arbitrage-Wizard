import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import {ChakraProvider} from "@chakra-ui/react";
import {Provider} from "react-redux";
import store from "./store/store.tsx";

createRoot(document.getElementById('root')!).render(
  <StrictMode>
      <ChakraProvider>
          <Provider store={store}>
              <App />
          </Provider>
      </ChakraProvider>
  </StrictMode>,
)
