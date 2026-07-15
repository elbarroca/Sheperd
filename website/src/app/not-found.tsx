import Link from "next/link";

export default function NotFoundPage(): React.JSX.Element {
  return (
    <main className="notice-page not-found" id="main-content">
      <p className="eyebrow">Preview route</p>
      <h1>Record not found.</h1>
      <p className="notice-intro">
        The requested Preview page is not part of the current review set.
      </p>
      <Link className="text-link" href="/">
        Return to the Preview
      </Link>
    </main>
  );
}
