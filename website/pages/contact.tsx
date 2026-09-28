import type { GetServerSideProps } from "next";

export const getServerSideProps: GetServerSideProps = async () => ({
  redirect: { destination: "/#contact", permanent: true },
});

export default function ContactRedirectPage(): null {
  return null;
}
