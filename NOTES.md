# GitHub Profile Maintenance Notes

Working copy of [github.com/Ublaze/Ublaze](https://github.com/Ublaze/Ublaze) — the GitHub profile README repo.
Edit here, commit, push. Live profile: https://github.com/Ublaze

## Structure

- `README.md` — profile page source
- `assets/profile-hero.svg` — top banner (1280x420)
- `assets/what-i-do.svg` — 2x2 capability grid (1280x470)
- `assets/achievements.svg` — 6-tile highlights card (1280x420)
- `assets/avatar-profile-brand.*` — brand avatar (also meant for GitHub profile picture, set manually)

## Brand system

- Background gradient: `#0B1220` → `#0F1D33` → `#0A2540`
- Card fill `#0D1828`, border `#23415F`
- Gold accent `#D7A94B`, blue accent `#0F6CBD`, sky text `#7DD3FC`
- Headings `#F8FAFC`, body `#94A3B8`, muted `#64748B`
- Font stack: Segoe UI / Arial; terminal card uses Consolas
- Badges: shields.io `for-the-badge`, uniform navy `0F172A`, white logos

## Design decisions (why things are the way they are)

- No GitHub stats/streak cards — removed deliberately; low public activity contradicted the "work is mostly private" narrative, and purple tokyonight clashed with the brand.
- No `github-profile-trophy` — public instance is paywalled (HTTP 402).
- Content is stated once per fact — earlier version repeated the tagline/scope 4x and looked AI-generated. Keep it lean.
- Logo slugs for shields: NetSuite, MS Project, Crystal Reports have no simple-icons logo — text-only badges by design.

## Facts source

LinkedIn PDF reviewed 2026-09 (in ~/Downloads/Linked_Profile.pdf). Key facts used:
- Sage X3 Certified Financial Application Consultant (WWSX3FC200)
- BTEC HND Computing Gold Medal, Batch Top (Edexcel)
- ERPs: Sage X3, Sage 300, NetSuite OneWorld, Dynamics NAV; also OpenAir, MS Project Server, Crystal Reports
- RFR Group Dubai (2017–present), Zillione (2012–2017), delivery across UAE/Sri Lanka/Maldives/Fiji
- Public contact email: salamuwais@gmail.com (LinkedIn side still shows ublaze@gmail.com — user to update)

## Known pending items

- GitHub profile picture: user to upload `assets/avatar-profile-brand.png` (no API for avatar).
- GitHub display name still "Ublaze"; `gh api -X PATCH user -f name="Uwais Salam"` needs the `user` OAuth scope (`gh auth refresh -h github.com -s user`).
- github-readme-stats service was 503; if restored, could reconsider a stats card (skip streak card either way).

## Previewing SVGs

Open the SVG file directly in a browser, or:
`start assets/profile-hero.svg` (Windows)
