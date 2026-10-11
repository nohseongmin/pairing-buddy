# Pairing Buddy

A five-question preference test that recommends food and a matching drink. The prototype is a single static `index.html` page without build tools.

## Questions and results

The first four answers select one of sixteen foods. The fifth selects one of two drink pairings.

| Question | Option A | Option B |
|---|---|---|
| Flavor | Spicy, S | Mild, M |
| Richness | Rich, R | Light, L |
| Broth | With broth, W | Dry, D |
| Portion | Hearty, H | Small, B |
| Drink | Stronger, X | Refreshing, Y |

The first four letters form the food key. For example, SRDH selects spicy fried chicken. The lowercase x pairing uses soju, sake, or wine; y uses beer, highballs, or makgeolli.

| Code | Food | Code | Food |
|---|---|---|---|
| SRWH | Pork backbone stew | MRWH | Beef hot pot |
| SRWB | Tteokbokki in broth | MRWB | Garlic shrimp |
| SRDH | Spicy fried chicken | MRDH | Grilled pork belly |
| SRDB | Spicy chicken feet | MRDB | Assorted Korean pancakes |
| SLWH | Spicy seafood soup | MLWH | Clear cod soup |
| SLWB | Spicy mussel soup | MLWB | Fish cake soup |
| SLDH | Stir-fried octopus | MLDH | White fish sashimi |
| SLDB | Seasoned sea snails | MLDB | Dried pollock |

Results include food, a type name, drink pairing, a nonalcoholic option, map searches, and two alternatives that change one preference.

## Map searches

The prototype opens [Google Maps search URLs](https://developers.google.com/maps/documentation/urls/get-started#search-action) in a new tab. It does not use an API key or store a restaurant database.

`AREAS` contains the default areas around Inha University's rear entrance and Juan Station. `FOOD_Q` and `DRINK_Q` separate search terms from display names. Searches without an area let Google Maps handle location context.

## Sharing

The result code is added to the URL fragment, for example `index.html#SRDHX`. Opening that link shows the result directly. The copy-result action includes the URL.

## Running and deployment

```bash
python -m http.server 8099
```

Use the local server to avoid local-file restrictions on images and the clipboard. Main pushes deploy the repository root to GitHub Pages through `.github/workflows/deploy.yml`, without a build.

### Browser regression checks

With the local server running from the repository root, open these pages:

- [tests/hash-navigation.html](tests/hash-navigation.html) checks that choosing an alternative updates the share URL, renders the result once, and keeps focus and scroll position.
- [tests/quiz-scroll.html](tests/quiz-scroll.html) checks that restarting on a short screen returns to the first question, clears the answers, and disables the result button.

Each page runs its checks on load and displays `통과했습니다.` on success or `실패했습니다:` followed by the failed check. Open both pages to check both behaviors.

## Editing content

| Constant | Purpose |
|---|---|
| QUESTIONS | Five questions and A/B text; keep the answer codes. |
| DRINK | Six drinks, image names, and photo credits in c. |
| FOOD | Sixteen food keys and their x/y pairings. |
| AREAS, FOOD_Q, DRINK_Q | Map areas and search terms. |

Keep all sixteen FOOD keys so every combination has a result. Update FOOD_Q when changing a food key.

The questions share the available height. On smaller screens, only the question area scrolls while progress and the result button remain visible. Description lines hide below 660 pixels of height.

## Photos

Replace the matching files in `images/`: `sool-makgeolli.jpg`, `sool-sake.jpg`, `sool-ipa.jpg`, `sool-highball.jpg`, `sool-soju.jpg`, and `sool-wine.jpg`. Missing images fall back to icons. Foods use icons rather than photos.

`pair-makgeolli.jpg`, `anju-jeon.jpg`, and `find-*.jpg` belong to the earlier swipe/discovery version and are not displayed by this version.

Update [CREDITS.md](CREDITS.md) and DRINK's c entries when replacing photos. Photo credits appear in result cards.

## License

The code may be freely used. Photos retain their original licenses; see [CREDITS.md](CREDITS.md).

Product names and pairing scores are demonstration data.
