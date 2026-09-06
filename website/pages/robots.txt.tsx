import type { GetServerSideProps } from "next";

import { getRobotsTxt } from "@/lib/seo";

export const getServerSideProps: GetServerSideProps = async ({ res }) => {
  res.setHeader("Content-Type", "text/plain; charset=utf-8");
  res.end(getRobotsTxt());

  return { props: {} };
};

export default function RobotsTxtPage() {
  return null;
}
