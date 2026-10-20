#!/usr/bin/env python3
"""
publish_clips.py — the deployment process for adding Archive.org-hosted
clips to video-contributions.

Upload to Archive.org is still manual (ia upload, or the web uploader,
max 5 at a time). Everything AFTER that — preview clip, thumbnail,
videos.json entry, the <article> card, the JSON-LD VideoObject, and the
vfilter counts — is driven from one input file by this script, so the
site, the schema and the manifest can't drift apart again.

Usage:
    python3 scripts/publish_clips.py pending-clips.json

pending-clips.json is a list of objects:
[
  {
    "id": "<archive.org identifier>",
    "source": "<absolute path to the local source file>",
    "archive_filename": "<filename as uploaded to archive.org>",
    "title": "...",
    "blurb": "...",
    "filmed": "YYYY-MM-DD"
  },
  ...
]

Run it from the repo root (same directory as videos.json).
It is safe to re-run: any id already present in videos.json is skipped.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VIDEOS_JSON = REPO / "videos.json"
INDEX_HTML = REPO / "docs" / "index.html"
PREVIEWS_DIR = REPO / "docs" / "previews"


def ffprobe_json(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json",
         "-show_format", "-show_streams", str(path)],
        capture_output=True, text=True, check=True,
    )
    return json.loads(out.stdout)


def probe_clip(path):
    data = ffprobe_json(path)
    duration = float(data["format"]["duration"])
    vstream = next(s for s in data["streams"] if s["codec_type"] == "video")
    w, h = int(vstream["width"]), int(vstream["height"])
    rotate = 0
    tags = vstream.get("tags", {})
    if "rotate" in tags:
        rotate = int(tags["rotate"]) % 360
    side_data = vstream.get("side_data_list", [])
    for sd in side_data:
        if "rotation" in sd:
            rotate = int(sd["rotation"]) % 360
    if rotate in (90, 270):
        w, h = h, w
    orientation = "portrait" if h > w else "landscape"
    return duration, orientation


def iso_duration(seconds):
    total = round(seconds)
    m, s = divmod(total, 60)
    h, m = divmod(m, 60)
    parts = ["PT"]
    if h:
        parts.append(f"{h}H")
    if m:
        parts.append(f"{m}M")
    if s or (not h and not m):
        parts.append(f"{s}S")
    return "".join(parts)


def mmss(seconds):
    total = round(seconds)
    m, s = divmod(total, 60)
    return f"{m}:{s:02d}"


def make_preview_assets(clip_id, source, orientation):
    PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    mp4_out = PREVIEWS_DIR / f"{clip_id}.mp4"
    jpg_out = PREVIEWS_DIR / f"{clip_id}.jpg"
    if orientation == "landscape":
        scale = "480:270"
        thumb_scale = "640:360"
    else:
        scale = "270:480"
        thumb_scale = "360:640"

    subprocess.run(
        ["ffmpeg", "-y", "-ss", "2", "-t", "2.5", "-i", str(source),
         "-vf", f"scale={scale}", "-an",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "28",
         "-movflags", "+faststart", str(mp4_out)],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["ffmpeg", "-y", "-ss", "2", "-i", str(source),
         "-frames:v", "1", "-vf", f"scale={thumb_scale}", str(jpg_out)],
        check=True, capture_output=True,
    )
    return mp4_out, jpg_out


def load_videos():
    with open(VIDEOS_JSON, encoding="utf-8") as f:
        return json.load(f)


def save_videos(videos):
    with open(VIDEOS_JSON, "w", encoding="utf-8") as f:
        json.dump(videos, f, indent=2, ensure_ascii=False)
        f.write("\n")


def video_object_block(name, desc, duration_iso, thumb, content_url,
                        embed_url, date_created, trailing_comma):
    comma = "," if trailing_comma else ""
    name_j = json.dumps(name)
    desc_j = json.dumps(desc)
    return f'''      {{
        "@type": "VideoObject",
        "name": {name_j},
        "description": {desc_j},
        "duration": "{duration_iso}",
        "uploadDate": "2026-10-20T16:00:00+05:30",
        "thumbnailUrl": [
          "https://ank-kumar.github.io/video-contributions/previews/{thumb}.jpg"
        ],
        "creator": {{
          "@type": "Person",
          "name": "Ank Kumar",
          "url": "https://ank-kumar.github.io/"
        }},
        "copyrightHolder": {{
          "@type": "Person",
          "name": "Ank Kumar",
          "url": "https://ank-kumar.github.io/"
        }},
        "license": "https://creativecommons.org/licenses/by-sa/4.0/",
        "isFamilyFriendly": true,
        "inLanguage": "en",
        "contentUrl": "{content_url}",
        "embedUrl": "{embed_url}",
        "dateCreated": "{date_created}"
      }}{comma}'''


def article_block(orientation, archive_id, title, blurb, dur_text):
    ar = "16/9" if orientation == "landscape" else "9/16"
    title_e = title.replace("&", "&amp;").replace("<", "&lt;")
    blurb_e = blurb.replace("&", "&amp;").replace("<", "&lt;")
    return f'''      <article class="archive-clip" data-orientation="{orientation}" data-archive-id="{archive_id}">
        <div class="archive-thumb" style="--ar:{ar}">
          <img src="previews/{archive_id}.jpg" alt="" loading="lazy">
          <video class="hover-preview" muted loop playsinline preload="none" aria-hidden="true" tabindex="-1">
            <source src="previews/{archive_id}.mp4" type="video/mp4">
          </video>
        </div>
        <h3>{title_e}</h3>
        <p>{blurb_e} — {dur_text}</p>
        <button type="button" class="watch-clip" aria-expanded="false">Play here</button>
        <div class="archive-player" aria-live="polite"></div>
      </article>'''


def insert_video_objects(html, new_blocks):
    anchor_pat = re.compile(
        r'(      \{\n        "@type": "VideoObject",.*?\n      \}\n)(    \]\n  \}\n</script>)',
        re.S,
    )
    m = anchor_pat.search(html)
    if not m:
        raise RuntimeError("Could not find end of JSON-LD @graph array")
    last_obj = m.group(1)
    fixed_last_obj = last_obj.rstrip("\n")
    if fixed_last_obj.rstrip().endswith("}"):
        fixed_last_obj = fixed_last_obj.rstrip()
        if not fixed_last_obj.endswith(","):
            fixed_last_obj += ","
    fixed_last_obj += "\n"
    replacement = fixed_last_obj + "\n".join(new_blocks) + "\n" + m.group(2)
    return html[:m.start()] + replacement + html[m.end():]


def insert_articles(html, new_articles):
    close_pat = re.compile(r'(      </article>\n)(    </div>\n  </section>)')
    m = close_pat.search(html)
    if not m:
        raise RuntimeError("Could not find end of .archive-clips list")
    insert_point = m.end(1)
    block = "\n".join(new_articles) + "\n"
    return html[:insert_point] + block + html[insert_point:]


def update_vfilter_counts(html, videos):
    # Ground truth is what's actually ON THE PAGE (the <article data-orientation=...>
    # cards), NOT videos.json — the manifest can hold more entries than are published
    # (catalogue items pending, defects, etc.), so counting videos.json would overstate
    # the filter chips. Count the rendered cards instead.
    orientations = re.findall(r'<article class="archive-clip" data-orientation="(\w+)"', html)
    total = len(orientations)
    landscape = orientations.count("landscape")
    portrait = orientations.count("portrait")
    html = re.sub(r'(data-filter="all" aria-pressed="true">All )\d+(</button>)',
                   rf'\g<1>{total}\g<2>', html)
    html = re.sub(r'(data-filter="landscape" aria-pressed="false">Landscape )\d+(</button>)',
                   rf'\g<1>{landscape}\g<2>', html)
    html = re.sub(r'(data-filter="portrait" aria-pressed="false">Portrait )\d+(</button>)',
                   rf'\g<1>{portrait}\g<2>', html)
    return html


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    pending_path = Path(sys.argv[1])
    with open(pending_path, encoding="utf-8") as f:
        pending = json.load(f)

    videos = load_videos()
    existing_ids = {v["id"] for v in videos}

    with open(INDEX_HTML, encoding="utf-8") as f:
        html = f.read()

    new_video_blocks = []
    new_article_blocks = []
    added = []

    for clip in pending:
        cid = clip["id"]
        if cid in existing_ids:
            print(f"skip {cid}: already in videos.json")
            continue

        source = Path(clip["source"])
        if not source.exists():
            print(f"SKIP {cid}: source not found at {source}")
            continue

        duration, orientation = probe_clip(source)
        make_preview_assets(cid, source, orientation)

        content_url = f"https://archive.org/download/{cid}/{clip['archive_filename']}"
        embed_url = f"https://archive.org/embed/{cid}"

        entry = {
            "source": "archive",
            "id": cid,
            "file": clip["archive_filename"],
            "seconds": round(duration, 2),
            "title": clip["title"],
            "blurb": clip["blurb"],
            "filmed": clip["filmed"],
            "poster": "",
            "derivative": "",
            "orientation": orientation,
        }
        videos.append(entry)
        existing_ids.add(cid)

        new_video_blocks.append(video_object_block(
            clip["title"], clip["blurb"], iso_duration(duration), cid,
            content_url, embed_url, clip["filmed"], trailing_comma=True))
        new_article_blocks.append(article_block(
            orientation, cid, clip["title"], clip["blurb"], mmss(duration)))
        added.append(cid)
        print(f"prepared {cid} ({orientation}, {mmss(duration)})")

    if not added:
        print("Nothing to add.")
        return

    last_block = new_video_blocks[-1]
    if last_block.rstrip().endswith(","):
        new_video_blocks[-1] = last_block.rstrip()[:-1]

    html = insert_video_objects(html, new_video_blocks)
    html = insert_articles(html, new_article_blocks)
    html = update_vfilter_counts(html, videos)

    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    save_videos(videos)

    print(f"\nAdded {len(added)} clip(s): {', '.join(added)}")
    print("Review docs/index.html and videos.json before committing.")


if __name__ == "__main__":
    main()
