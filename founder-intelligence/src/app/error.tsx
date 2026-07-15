"use client";

export default function ErrorPage({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <section className="error-state" role="alert">
      <p className="eyebrow">Workspace stopped safely</p>
      <h1>The requested view could not be rendered.</h1>
      <p>No data or execution state changed.</p>
      <button type="button" onClick={reset}>Try this view again</button>
    </section>
  );
}
