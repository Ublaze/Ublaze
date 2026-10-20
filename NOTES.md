# GitHub Profile Maintenance Notes

Working copy of [github.com/Ublaze/Ublaze](https://github.com/Ublaze/Ublaze), the GitHub profile README repo.
Edit `README.md` directly, commit, push. Live profile: https://github.com/Ublaze

## Design (Oct 2026)

Plain GitHub markdown. No images, banners, badges, stats cards, view counters or emoji.
It renders natively in light and dark mode and needs no build step.

Rules:
- Understated and professional. No themes or metaphors. The earlier "Ledger" SVG design
  (stamp, vouchers, Schedule A-D) was retired as too gimmicky; it's in git history before this commit.
- State each fact once.
- Feature only serious tools. Hobby repos (Quran-FlipBoard-TV, YTune) stay public but are not featured.
- Client work stays anonymised: describe the kind of work, never the client.

To add a repo: add a row to the Open source table and pin it on the profile.

## Facts source

LinkedIn PDF reviewed 2026-09 (~/Downloads/Linked_Profile.pdf):
Sage X3 Certified Financial Application Consultant (WWSX3FC200); BTEC HND Computing Gold Medal (Edexcel);
Zillione 2012-2017; RFR Group Dubai 2017-present; delivery across UAE / Sri Lanka / Maldives / Fiji.

## Pending (manual)

- Pin: VHD2Wasabi, Caffeinator, Windows11-Optimizer, github-readme-generator, github-showcase.
- Avatar: a real photo or plain initials (GitHub has no API for avatars).
- Display name / bio / location / company: `gh auth refresh -h github.com -s user`, then
  `gh api -X PATCH user -f name="Uwais Salam" -f location="Dubai, UAE" -f company="RFR Group"`.

## Previewing

`gh api markdown -f mode=gfm -F text=@README.md` into an HTML page with github-markdown-css,
then screenshot it with headless Chrome (`--force-dark-mode` for dark).
