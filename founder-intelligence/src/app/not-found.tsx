import Link from "next/link";

export default function NotFoundPage() {
  return (
    <section className="error-state">
      <p className="eyebrow">Not in the manifest</p>
      <h1>This intelligence view does not exist.</h1>
      <Link href="/">Return to the founder brief</Link>
    </section>
  );
}
