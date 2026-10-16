# video-contributions

Footage filmed by Ank Kumar, released under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

Published at <https://ank-kumar.github.io/video-contributions/>

## Release 1

One cut: 48 seconds from three dives on the Great Barrier Reef,
13 October 2016. Shot on a GoPro, colour corrected to restore the
red that water absorbs at depth.

Served from `/docs` on `main`.

## Release 2

Catalogue the full library. Clips are grouped and tagged at trip
level, not clip level. Files move to the Internet Archive, and to
Wikimedia Commons where the footage is encyclopaedically useful;
this repo keeps the index and the manifest, not the media.

Note for the inventory pipeline: re-encoding rewrites
`com.apple.quicktime.creationdate`. Any clip that has been edited,
compressed or speed-corrected will report the edit date, not the
capture date. Reconcile across all available tags and flag
disagreements rather than trusting a single field.

## Open items

Recorded 16 Oct 2026. The page is live and working; none of these block a
visitor from watching and reusing the clips.

### Archive item defects

- `img-1464_202610` — no derivative and no thumbnail. The card shows Archive's
  temple placeholder. Needs re-deriving.
- `img-3770_202610` — no derivative (thumbnail is fine). Needs re-deriving.
- `img-1458_202610` contains `IMG_3776.MP4`, not IMG_1458. The real IMG_1458
  clip has never been uploaded. `img-3776_202610` holds the same original
  (identical byte count) and is unpublished.
- `IMG_1455` uploaded twice (`img-1455_20261015_1505`, `img-1455_20261016`).
  Both originals are 0.33 seconds. Neither is published. Delete one or both.
- `Ank_K_1594480756` is titled "Catherham" — misspelt at source.
- Every `img-*` item description on Archive is raw pasted HTML
  (`<p class="p1" style=...`), which renders as literal markup on the item page.
- Archive item dates read 2016-10-12; the site says 13 October 2016.

### Hosting

- The 48-second reel is the only file served from this repo (~11 MB). Upload it
  to Archive, change that record's `source` from `github` to `archive`, set
  `id`/`file`/`derivative`, rebuild, delete `docs/vids/`.

### Player

- Escape does not close the player while focus is inside the Archive iframe.
  Cross-origin: keystrokes go to Archive's document, not ours. The fix is to
  drop the iframe and play the derivative in a native `<video>`, which also
  unifies the local and Archive code paths. BLOCKED on the two re-derives above.
- Clicking the scrim does not close theater mode; only the buttons do.
- The theater panel is `min(50vw,900px)` — narrower than the card grid behind it
  on wide displays.

### Catalogue

- 8 of a ~20 target. Thirteen more uploads, including the reel.
- Uploads are hand-driven. Four of seven items carried a defect. `videos.json`
  already holds the metadata; the uploads should be driven from it so Archive
  and the site cannot disagree.
- `filmed` is empty for the Caterham and Hawker Hunter records. The Caterham
  Archive title reads "15 Jan 201" — year truncated at source.
- Filter chips by place and subject, once the catalogue is large enough to need them.

### Housekeeping

- Dead CSS left from the removed featured block: `.sub`, `figcaption`, `.film`.
- Re-request indexing in Search Console after any schema change. The schema now
  carries 8 VideoObjects; Google last recorded 1.
