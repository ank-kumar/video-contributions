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

## Known gaps

- The 48-second Great Barrier Reef cut (`docs/vids/reef-2016-great-barrier-reef.mp4`)
  is still served from this repo. Every other clip streams from Archive.org and
  costs no bandwidth until played. To close this: upload the cut to Archive,
  change that record's `source` from `github` to `archive` in `videos.json`,
  set its identifier and file, rebuild, then delete `docs/vids/`.
  Until then the repo carries ~11 MB of media it should not.
- `img-3776_202610` and `img-1458_202610` hold the same original
  (`IMG_3776.MP4`, identical byte count). Only `img-1458_202610` is published,
  because it is the one with a working derivative. The real `IMG_1458` clip was
  never uploaded.
- `IMG_1455` uploaded twice, both 0.33 seconds in the original file. Not published.
- Archive item `Ank_K_1594480756` is titled "Catherham" — misspelt at source.
