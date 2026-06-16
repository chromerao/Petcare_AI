---
name: PetCare AI Design System
colors:
  surface: '#faf9f6'
  surface-dim: '#dbdad7'
  surface-bright: '#faf9f6'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f4f3f1'
  surface-container: '#efeeeb'
  surface-container-high: '#e9e8e5'
  surface-container-highest: '#e3e2e0'
  on-surface: '#1a1c1a'
  on-surface-variant: '#41474e'
  inverse-surface: '#2f312f'
  inverse-on-surface: '#f2f1ee'
  outline: '#72787f'
  outline-variant: '#c1c7cf'
  surface-tint: '#316289'
  primary: '#074469'
  on-primary: '#ffffff'
  primary-container: '#2a5c82'
  on-primary-container: '#a5d4ff'
  inverse-primary: '#9ccbf7'
  secondary: '#556158'
  on-secondary: '#ffffff'
  secondary-container: '#d9e6da'
  on-secondary-container: '#5b675e'
  tertiary: '#284900'
  on-tertiary: '#ffffff'
  tertiary-container: '#386300'
  on-tertiary-container: '#a5e069'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#cde5ff'
  primary-fixed-dim: '#9ccbf7'
  on-primary-fixed: '#001d32'
  on-primary-fixed-variant: '#124a6f'
  secondary-fixed: '#d9e6da'
  secondary-fixed-dim: '#bdcabe'
  on-secondary-fixed: '#131e17'
  on-secondary-fixed-variant: '#3e4a41'
  tertiary-fixed: '#b8f47a'
  tertiary-fixed-dim: '#9dd761'
  on-tertiary-fixed: '#0e2000'
  on-tertiary-fixed-variant: '#2c5000'
  background: '#faf9f6'
  on-background: '#1a1c1a'
  surface-variant: '#e3e2e0'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  xxl: 48px
  container-max: 1200px
  gutter: 24px
  margin-mobile: 16px
---

## Brand & Style
The design system is built on a foundation of **Empathetic Professionalism**. It balances the clinical precision required for a medical triage assistant with the warmth and approachability expected by pet owners in moments of concern. The visual language is modern and tech-forward, utilizing a "Modern Corporate" aesthetic softened by organic shapes and a comforting palette.

The target audience consists of pet owners seeking immediate, reliable guidance. The UI must evoke a sense of calm authority—reducing anxiety through clear hierarchy while maintaining a friendly, supportive dialogue. 

**Design Principles:**
- **Reliability:** Clear, structured layouts that mimic clinical efficiency.
- **Empathy:** Softened edges and warm neutrals to offset the "coldness" of AI.
- **Clarity:** High legibility and purposeful use of color to highlight urgent information.

## Colors
The color strategy uses **Vet Blue** as the anchor of trust and medical authority. It is applied to primary actions, headers, and key brand moments. **Warm Sand** serves as the primary background color, providing a softer, more "homely" alternative to stark white, which can feel overly sterile.

**Soft Mint** is used for secondary accents, background washes for success states, and chat bubbles to signify a "healthy" or "calm" status. We also introduce a **Muted Leaf** green (#7CB342) for tertiary elements like health-tracking indicators.

Functional colors (Error/Warning) are softened but remain high-contrast to ensure triage urgency is never missed.

## Typography
This design system pairs **Plus Jakarta Sans** for headings with **Inter** for body and UI elements. Plus Jakarta Sans provides a friendly, slightly rounded geometric feel that softens the "medical" tone, while Inter ensures maximum legibility for complex triage instructions and chat dialogues.

- **Headlines:** Use Plus Jakarta Sans with tighter letter-spacing to create a confident, modern look.
- **Body:** Inter is the workhorse here, optimized for reading long-form advice and chat messages.
- **Urgent Notes:** Triage alerts should use `label-sm` in bold uppercase to quickly grab attention without feeling aggressive.

## Layout & Spacing
The layout follows a **4px baseline grid** to maintain mathematical harmony. For the chatbot interface, a centered fluid layout is preferred, maxing out at 800px for the chat window to maintain optimal line lengths for readability.

- **Desktop:** 12-column grid with 24px gutters. Content is typically housed in a central "stage" area.
- **Mobile:** Single column with 16px side margins. Elements like cards and chat bubbles should utilize the full width minus margins.
- **Chat Rhythm:** Use `md` (16px) spacing between messages from the same sender, and `lg` (24px) between different senders to clarify the dialogue flow.

## Elevation & Depth
Depth in this design system is used to signify interactive layers and prioritize information during triage. We move away from heavy shadows in favor of **Tonal Layers** and **Soft Ambient Shadows**.

- **Level 0 (Background):** Warm Sand (#FAF9F6) - The base canvas.
- **Level 1 (Cards/Bubbles):** Pure White (#FFFFFF) - Used for chat bubbles and information cards to make them "pop" against the sand background. These feature a very soft, diffused shadow (0px 4px 20px rgba(42, 92, 130, 0.08)).
- **Level 2 (Modals/Overlays):** Pure White with a more pronounced shadow to indicate temporary focus.
- **Interactive Elements:** Buttons utilize a slight inner-glow or subtle lift on hover to provide tactile feedback without looking "heavy."

## Shapes
The shape language is defined by **Rounded (0.5rem)** corners. This specific level of roundedness is "friendly but controlled"—it avoids the playfulness of a toy (pill-shaped) while removing the harshness of sharp medical corners.

- **Chat Bubbles:** The user's bubble should have a distinct corner treatment (e.g., a sharper bottom-right corner) to indicate directionality.
- **Action Buttons:** Large primary buttons should use the `rounded-lg` (1rem) setting to feel more "touchable" and inviting.
- **Avatars:** Pet and AI avatars are always circular to symbolize wholeness and friendliness.

## Components
Consistent component styling ensures the AI feels like a cohesive personality.

- **Buttons:**
  - **Primary:** Vet Blue background, White text. High-contrast, used for "Start Triage" or "Call Vet."
  - **Secondary:** Soft Mint background, Vet Blue text. Used for non-urgent selections or "Back" actions.
- **Chat Bubbles:**
  - **AI Bubble:** Soft Mint background with Inter Medium text. Includes a small pet-icon avatar.
  - **User Bubble:** Vet Blue background with White text.
- **Triage Chips:** Small, interactive labels (e.g., "Vomiting", "Lethargic") with a 1px Vet Blue border that fills with Soft Mint when selected.
- **Health Cards:** Used for summary reports. They feature a Level 1 elevation, a Vet Blue top-border (2px), and clear typography for "Next Steps."
- **Input Fields:** Large, 56px height inputs with 0.5rem roundedness. Focus states use a 2px Vet Blue glow.
- **Progress Stepper:** A subtle line at the top of the chat to indicate how far along the triage process the user is, using Vet Blue for completed steps and Soft Mint for upcoming ones.