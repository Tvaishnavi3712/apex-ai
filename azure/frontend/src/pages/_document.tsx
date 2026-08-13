/**
 * Custom Next.js Document.
 *
 * Adds `data-scroll-behavior="smooth"` to <html> so Next 16 knows the smooth
 * scrolling we set in globals.css is intentional and shouldn't apply during
 * route transitions (which would feel laggy). Without this attribute Next
 * logs a warning on every page load:
 *
 *     Detected `scroll-behavior: smooth` on the `<html>` element.
 *     To disable smooth scrolling during route transitions, add
 *     `data-scroll-behavior="smooth"` to your <html> element.
 *
 * See: https://nextjs.org/docs/messages/missing-data-scroll-behavior
 */
import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html lang="en" data-scroll-behavior="smooth">
      <Head />
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
