import { readdir, readFile } from "node:fs/promises";
import { extname, join, resolve } from "node:path";
import { gzipSync } from "node:zlib";

const INITIAL_JAVASCRIPT_BUDGET_BYTES = 150_000;

async function walk(directory: string): Promise<string[]> {
  const entries = await readdir(directory, { withFileTypes: true });
  const paths = await Promise.all(
    entries.map(async (entry) => {
      const path = join(directory, entry.name);
      return entry.isDirectory() ? walk(path) : [path];
    }),
  );

  return paths.flat();
}

async function main(): Promise<void> {
  const root = resolve(process.cwd(), "src");
  const files = await walk(root);
  const componentFiles = files.filter((path) => extname(path) === ".tsx");

  for (const path of componentFiles) {
    const source = await readFile(path, "utf8");
    const usesMotion = /from ["']motion\/react(?:-m|-mini)?["']/.test(source);

    if (!usesMotion) {
      continue;
    }

    if (!source.startsWith('"use client"')) {
      throw new Error(`Motion component is not a client module: ${path}`);
    }

    if (
      (source.includes("<m.") || source.includes("<motion.")) &&
      !source.includes("useReducedMotion")
    ) {
      throw new Error(`Motion component lacks reduced-motion handling: ${path}`);
    }
  }

  const css = await readFile(resolve(process.cwd(), "src/styles/globals.css"), "utf8");
  const forbiddenCss = [/@keyframes\b/, /animation(?:-name)?:/];

  for (const pattern of forbiddenCss) {
    if (pattern.test(css)) {
      throw new Error(`CSS contains unapproved authored motion: ${pattern}`);
    }
  }

  const packageSource = await readFile(resolve(process.cwd(), "package.json"), "utf8");
  const packageJson = JSON.parse(packageSource) as {
    readonly dependencies?: Readonly<Record<string, string>>;
  };
  const dependencies = Object.keys(packageJson.dependencies ?? {});
  const animationDependencies = dependencies.filter(
    (dependency) =>
      /motion|framer|gsap|anime|lenis|scrollworld|higgsfield|xfield/i.test(
        dependency,
      ),
  );

  if (animationDependencies.length !== 1 || animationDependencies[0] !== "motion") {
    throw new Error(
      `Expected motion as the only animation dependency; found ${animationDependencies.join(", ") || "none"}.`,
    );
  }

  const allComponentSource = (
    await Promise.all(componentFiles.map((path) => readFile(path, "utf8")))
  ).join("\n");
  const forbiddenRuntimePatterns = [
    /requestAnimationFrame\s*\(/,
    /addEventListener\s*\(\s*["']scroll["']/,
    /<video\b[^>]*autoplay/i,
    /<canvas\b/i,
    /scrollworld|higgsfield|xfield/i,
  ];

  for (const pattern of forbiddenRuntimePatterns) {
    if (pattern.test(allComponentSource)) {
      throw new Error(`Source contains prohibited motion runtime pattern: ${pattern}`);
    }
  }

  const filesWithInlineMotionValues = (
    await Promise.all(
      componentFiles.map(async (path) => {
        const source = await readFile(path, "utf8");
        if (!/from ["']motion\/react(?:-m|-mini)?["']/.test(source)) {
          return [];
        }

        return /(?:duration|ease|stiffness|damping|mass)\s*:\s*(?:\d|\[)/.test(
          source,
        )
          ? [path]
          : [];
      }),
    )
  ).flat();

  if (filesWithInlineMotionValues.length > 0) {
    throw new Error(
      `Motion component bypasses documented tokens: ${filesWithInlineMotionValues.join(", ")}`,
    );
  }

  const pageHtml = await readFile(
    resolve(process.cwd(), ".next/server/app/index.html"),
    "utf8",
  ).catch(() => {
    throw new Error(
      "Optimized build output is missing. Run validate:motion after next build.",
    );
  });
  const scriptTags = pageHtml.match(/<script\b[^>]*\bsrc="[^"]+"[^>]*>/g) ?? [];
  const modernScriptSources = scriptTags
    .filter((tag) => !/\bnomodule\b/i.test(tag))
    .map((tag) => tag.match(/\bsrc="([^"]+)"/)?.[1])
    .filter((source): source is string => Boolean(source));
  const initialJavaScriptGzipBytes = (
    await Promise.all(
      modernScriptSources.map(async (source) => {
        if (!source.startsWith("/_next/")) {
          throw new Error(`Unexpected initial script source: ${source}`);
        }

        const scriptPath = resolve(
          process.cwd(),
          ".next",
          source.slice("/_next/".length),
        );
        return gzipSync(await readFile(scriptPath)).byteLength;
      }),
    )
  ).reduce((total, bytes) => total + bytes, 0);

  if (initialJavaScriptGzipBytes > INITIAL_JAVASCRIPT_BUDGET_BYTES) {
    throw new Error(
      `Initial JavaScript is ${initialJavaScriptGzipBytes} gzip bytes; budget is ${INITIAL_JAVASCRIPT_BUDGET_BYTES}.`,
    );
  }

  process.stdout.write(
    `Motion gate passed. Initial JavaScript: ${initialJavaScriptGzipBytes} gzip bytes.\n`,
  );
}

main().catch((error: unknown) => {
  const message = error instanceof Error ? error.message : String(error);
  process.stderr.write(`${message}\n`);
  process.exitCode = 1;
});
