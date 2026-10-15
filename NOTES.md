# GitHub Profile Maintenance Notes

Working copy of [github.com/Ublaze/Ublaze](https://github.com/Ublaze/Ublaze), the GitHub profile README repo.
Edit here, commit, push. Live profile: https://github.com/Ublaze

## Concept: "The Ledger" (Oct 2026 redesign)

The profile is a set of pages from an accounting ledger, which suits an ERP and finance-systems consultant
and stands apart from the usual dark-dashboard dev profile.

| Page | Asset | Ledger idea |
| --- | --- | --- |
| Folio 01 | `hero-*` | Name + journal of career entries, **Balance C/F** = the only place stats appear |
| Schedule A | `practice-*` | Chart of Accounts: the four capabilities as account codes 1000–4000 |
| Schedule B | `head-builds-*` + `v-<repo>-*` | Public repos as numbered vouchers (ticket stubs) |
| Schedule C | `head-private-*` + markdown table | Anonymised client engagements |
| Schedule D | `toolbox-*` | Trial Balance: tools grouped by account, with a total |
| Avatar | `avatar-{light,dark}.{svg,png}` | "U" monogram, red margin, gold double rule |

## Regenerating

    python build_assets.py

**Never hand-edit `assets/*.svg`.** All copy (journal rows, accounts, tools, project vouchers), tokens and
layout live in `build_assets.py`. The README is hand-written but mirrors `PROJECTS` / `TOOLS`. When you add a
voucher, add it to `PROJECTS`, rebuild, and add the `<a><picture>` pair in README (two per line).

## Brand system

- **Type:** Fraunces (display opsz 144 for the name only; opsz 48 for headings and figures), Fraunces Italic
  (margin notes), IBM Plex Sans (body), IBM Plex Mono (labels, refs, codes). Sources are in `fonts/` (OFL).
  Each SVG embeds a per-file **subset** as base64 WOFF, which is why it renders identically on every OS.
- **Colour tokens** (`THEMES` in the script):
  - Light: paper `#F7F4EC`, ink `#1B1F24`, rule `#D9D2C0`, red `#A3362A`, gold `#B08A3E`
  - Dark: paper `#12161C`, ink `#ECE6D8`, rule `#2E3640`, red `#D9705F`, gold `#D7A94B`
- **Ledger grammar:** a red double margin line on the left; a single ink rule under headers; faint rules between
  rows; a gold **double rule** only under totals. Red appears only in the margin and the POSTED stamp.
- **Light/dark:** every asset ships as a `-light` / `-dark` pair, switched with
  `<picture><source media="(prefers-color-scheme: dark)">`.

## Gotchas

- Fraunces at opsz 144 draws `+` and other thin strokes as hairlines (about 0.4px at 44px), so figures must use
  the `serif` face (opsz 48), not `display`.
- Plex Mono's `✓` looks like a radical sign `√`, so use words (cert., award) instead.
- Keep the smallest text at 14px or larger in the 1280-wide pages, and 13px or larger in the 600-wide vouchers. GitHub shows them at roughly 0.65×.
- The "meta NOT subset" warning from fontTools is harmless.
- Headless Chrome won't go below ~500px wide, so phone-width screenshots look clipped. That's a capture artifact.

## Design decisions

- No GitHub stats, streak or trophy cards. Public activity contradicts the "work is mostly private" story, and
  the trophy service is paywalled.
- Each fact is stated once. Earlier versions repeated stats and the tagline and looked AI-generated.
- No glows, gradient text, terminal windows or pills. That was the previous generic look.

## Facts source

LinkedIn PDF reviewed 2026-09 (~/Downloads/Linked_Profile.pdf):
Sage X3 Certified Financial Application Consultant (WWSX3FC200); BTEC HND Computing Gold Medal, batch top
(Edexcel); Zillione 2012–2017; RFR Group Dubai 2017–present; delivery across UAE / Sri Lanka / Maldives / Fiji.

## Pending (manual)

- Profile picture: upload `assets/avatar-dark.png` (or `-light`). GitHub has no API for avatars.
- Display name still "Ublaze": `gh auth refresh -h github.com -s user` then
  `gh api -X PATCH user -f name="Uwais Salam"`.
- Legacy `avatar-profile-brand.*` kept for reference; delete once the new avatar is live.

## Previewing

`start assets\hero-light.svg`, or render the README through `gh api markdown -f mode=gfm -F text=@README.md`
into an HTML page with github-markdown-css and screenshot it with headless Chrome (`--force-dark-mode` for dark).
