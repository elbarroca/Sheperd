import type { AppProps } from "next/app";

import { PilotDialogProvider } from "@/components/pilot-dialog";

import "@/styles/globals.css";
import "@/styles/motion.css";

export default function App({ Component, pageProps }: AppProps) {
  return (
    <div className="marketing-site">
      <PilotDialogProvider>
        <Component {...pageProps} />
      </PilotDialogProvider>
    </div>
  );
}
