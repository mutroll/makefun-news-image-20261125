[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/mutroll/makefun-news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/mutroll/makefun-news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

# The World in One Day — Wednesday 25 November 2026

A newspaper front page that sums up Wednesday 25 November 2026 in one
image: six stories from around the globe, drawn programmatically.

## The six stories

1. **Space — China:** China launches Shenzhou-24; Muhammad Zeeshan Ali
   becomes the first Pakistani in orbit and the first foreign guest aboard
   the Tiangong space station.
2. **Markets — Japan:** The Nikkei plunges 2.8% in Tokyo as the AI sell-off
   resumes; chipmaker Advantest falls 12%.
3. **Disaster — Philippines:** A magnitude 5.1 earthquake shakes Panay;
   Intensity V in Valderrama, with damage and aftershocks expected.
4. **Politics — Australia:** NSW ICAC urges Corrective Services NSW to fix
   a "misogynistic" workplace culture after Operation Targo.
5. **Society — India:** India launches Nayi Chetna 5.0, a month-long gender
   campaign, on the UN day against violence on women.
6. **Health — England:** England has the widest rich-poor frailty gap of
   31 countries, a King's College London study finds.

All six stories happened or were first reported on Wednesday 25 November
2026. Sources: Reuters, Dow Jones, PHIVOLCS, NSW ICAC, PIB, The Guardian.

## How it works

`main.py` (Python 3.13 standard library only, no network) draws the poster
at 2048x2048 with its own 5x7 bitmap font and simple vector shapes, then
downscales it to a 1024x1024 PNG. It is fully deterministic: two runs
write byte-identical output.

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

## License

MIT — see `LICENSE`.
