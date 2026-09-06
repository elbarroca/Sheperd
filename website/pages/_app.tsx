import type { AppProps } from "next/app";

import { PilotDialogProvider } from "@/components/pilot-dialog";
import { SmoothScroll } from "@/components/smooth-scroll";

import "lenis/dist/lenis.css";
import "@/styles/globals.css";
import "@/styles/motion.css";

export default function App({ Component, pageProps }: AppProps) {
  return (
    <div className="marketing-site">
      <PilotDialogProvider>
        <SmoothScroll />
        <Component {...pageProps} />
      </PilotDialogProvider>
    </div>
  );
}
