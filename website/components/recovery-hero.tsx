"use client";

import { Pause, Play } from "@phosphor-icons/react";
import Image from "next/image";
import { useEffect, useRef, useState, useSyncExternalStore } from "react";

import { PilotLink } from "./pilot-link";

const REDUCED_MOTION_QUERY = "(prefers-reduced-motion: reduce)";
const MINIMUM_VISIBLE_RATIO = 0.05;

function subscribeToMotionPreference(onChange: () => void): () => void {
  const preference = window.matchMedia(REDUCED_MOTION_QUERY);
  preference.addEventListener("change", onChange);
  return () => preference.removeEventListener("change", onChange);
}

function prefersReducedMotion(): boolean {
  return window.matchMedia(REDUCED_MOTION_QUERY).matches;
}

function subscribeToVisibility(onChange: () => void): () => void {
  document.addEventListener("visibilitychange", onChange);
  return () => document.removeEventListener("visibilitychange", onChange);
}

function pageIsVisible(): boolean {
  return document.visibilityState === "visible";
}

function serverIsVisible(): boolean {
  return false;
}

export function RecoveryHero() {
  const sceneRef = useRef<HTMLDivElement>(null);
  const [isInView, setIsInView] = useState(false);
  const reducedMotion = useSyncExternalStore(subscribeToMotionPreference, prefersReducedMotion, serverIsVisible);
  const pageVisible = useSyncExternalStore(subscribeToVisibility, pageIsVisible, serverIsVisible);
  const [paused, setPaused] = useState(false);
  const isRunning = isInView && pageVisible && !reducedMotion && !paused;
  const motionLabel = reducedMotion ? "Motion off" : paused ? "Resume animation" : "Pause animation";

  useEffect(() => {
    const scene = sceneRef.current;
    if (!scene) return;

    const observer = new IntersectionObserver(
      ([entry]) => setIsInView(Boolean(entry && entry.intersectionRatio >= MINIMUM_VISIBLE_RATIO)),
      { threshold: MINIMUM_VISIBLE_RATIO },
    );
    observer.observe(scene);
    return () => observer.disconnect();
  }, []);

  return (
    <section className="recovery-hero" aria-labelledby="hero-title">
      <div className="hero-copy">
        <p className="eyebrow">For importer finance + logistics teams</p>
        <h1 id="hero-title">
          <span>Recover the D&amp;D money</span>
          <span>hiding in your invoices.</span>
        </h1>
        <p className="hero-summary">
          SheperD reviews detention and demurrage charges against shipment
          records and governing terms to identify case-specific recovery
          opportunities.
        </p>
        <div className="hero-actions">
          <PilotLink className="button">Request a pilot</PilotLink>
          <a className="button button-outline" href="#process">See the recovery path</a>
        </div>
        <p className="hero-boundary">
          Case-specific review <span aria-hidden="true">·</span> No guaranteed recovery
        </p>
      </div>
      <div ref={sceneRef} className="hero-scene" data-testid="hero-scene" data-motion={isRunning ? "running" : "paused"}>
        <Image
          src="/media/recovery-terminal.png"
          alt="Rows of shipping containers in an atmospheric terminal scene."
          fill
          preload
          fetchPriority="high"
          sizes="(max-width: 767px) 100vw, (max-width: 1600px) calc(100vw - 64px), 1536px"
          quality={90}
          className="hero-image"
        />
        <div className="hero-fog" aria-hidden="true" />
        <div className="hero-light" aria-hidden="true" />
        <div className="hero-scrim" aria-hidden="true" />
        <button
          type="button"
          className="motion-toggle"
          disabled={Boolean(reducedMotion)}
          onClick={() => setPaused((current) => !current)}
        >
          {paused || reducedMotion ? <Play size={13} weight="fill" aria-hidden="true" /> : <Pause size={13} weight="fill" aria-hidden="true" />}
          <span>{motionLabel}</span>
        </button>
      </div>
    </section>
  );
}
