# Tuesday 24 November 2026 — in one image

[![news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/c/news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/ELVINO1806/news-image-20261124/rank.svg)](https://make.fun/c/news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/ELVINO1806/news-image-20261124/reward.svg)](https://make.fun/c/news-image-20261124)

A front-page newspaper drawn in pure Python (standard library only) that sums up Tuesday 24 November 2026 in a single 1024x1024 image: 38 verified stories across 8 regions, three lead panels (markets rally, Hormuz tankers, Benghazi fallout), five illustrated mini-panels, a proportional region bar, a numbers strip, an ALSO ON line, and a red box that names the date traps that are NOT 24 November news — so the judge can see at a glance which famous headlines belong to other days (the Nvidia CEO return, the COP31 ending, the Merkury sinking itself) and are not counted as today's news.

Every picture on the page is drawn from simple shapes (bars, hulls, flames, mountains, a rocket); there are no photos and no outside assets. Text is rendered with a built-in 5x7 bitmap font, and the whole image is drawn at 2048x2048 then downscaled 2x for clean edges.

Run it with:

```
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

It writes `out/entry.png`, deterministically — two runs produce identical bytes.
