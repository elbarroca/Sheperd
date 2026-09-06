"use client";

import Image, { getImageProps } from "next/image";
import { type ReactElement, useEffect, useRef, useState, useSyncExternalStore } from "react";

import { PilotLink } from "./pilot-link";

const REDUCED_MOTION_QUERY = "(prefers-reduced-motion: reduce)";
const MINIMUM_VISIBLE_RATIO = 0.05;
const HERO_IMAGE_ALT = "Rows of shipping containers in an atmospheric terminal scene.";
const { props: mobileImage } = getImageProps({
  src: "/media/recovery-terminal-mobile.png",
  alt: HERO_IMAGE_ALT,
  width: 820,
  height: 820,
  sizes: "820px",
  quality: 90,
});

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

export function RecoveryHero(): ReactElement {
  const sceneRef = useRef<HTMLDivElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isInView, setIsInView] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);
  const [videoReady, setVideoReady] = useState(false);
  const reducedMotion = useSyncExternalStore(subscribeToMotionPreference, prefersReducedMotion, serverIsVisible);
  const pageVisible = useSyncExternalStore(subscribeToVisibility, pageIsVisible, serverIsVisible);
  const isRunning = isInView && pageVisible && !reducedMotion;

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

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;
    if (!isRunning || !imageLoaded) {
      video.pause();
      return;
    }

    let active = true;
    void video.play().catch(() => {
      // Autoplay restrictions or unavailable media leave the original artwork visible.
      if (active) setVideoReady(false);
    });
    return () => {
      active = false;
      video.pause();
    };
  }, [imageLoaded, isRunning]);

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
        <picture>
          <source media="(max-width: 767px)" srcSet={mobileImage.srcSet} sizes={mobileImage.sizes} />
          <Image
            src="/media/recovery-terminal.png"
            alt={HERO_IMAGE_ALT}
            fill
            loading="eager"
            fetchPriority="high"
            sizes="100vw"
            quality={90}
            className="hero-image"
            onLoad={() => setImageLoaded(true)}
          />
        </picture>
        <video
          ref={videoRef}
          className="hero-video"
          data-testid="hero-video"
          data-ready={videoReady ? "true" : "false"}
          aria-hidden="true"
          tabIndex={-1}
          autoPlay={isRunning && imageLoaded}
          loop
          muted
          playsInline
          preload="none"
          onPlaying={() => setVideoReady(true)}
          onError={() => setVideoReady(false)}
        >
          <source src="/media/recovery-terminal-loop.webm" type="video/webm" />
          <source src="/media/recovery-terminal-loop.mp4" type="video/mp4" />
        </video>
        <div className="hero-scrim" aria-hidden="true" />
      </div>
    </section>
  );
}
