import type { GetServerSideProps } from "next";

import { getSitemapXml } from "@/lib/seo";

export const getServerSideProps: GetServerSideProps = async ({ res }) => {
  res.setHeader("Content-Type", "application/xml; charset=utf-8");
  res.end(getSitemapXml());

  return { props: {} };
};

export default function SitemapXmlPage() {
  return null;
}
