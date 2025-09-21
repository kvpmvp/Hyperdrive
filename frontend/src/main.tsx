// src/main.tsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./styles/App.css";
import ErrorBoundary from "./components/ErrorBoundary";
import { WalletProvider } from "@txnlab/use-wallet-react";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <ErrorBoundary>
      <WalletProvider supportedWallets={["pera", "defly"]}>
        <App />
      </WalletProvider>
    </ErrorBoundary>
  </React.StrictMode>
);
