(async function () {
  // 1) Load the manifest built by your Python script
  const resp = await fetch("./dogs_manifest.json");
  const MANIFEST = await resp.json();

  // 2) Build a case-insensitive lookup: "labrador retriever" -> [urls...]
  const DOGS_BY_KEY = {};
  for (const breed in MANIFEST) {
    const key = breed.toLowerCase().replace(/\s+/g, " ").trim();
    DOGS_BY_KEY[key] = MANIFEST[breed];
  }

  // 3) Keep originals so we can restore tooltip text on mouse-out
  const ORIGINALS = {};
  const data = simplemaps_cityzipmap_mapdata;
  for (const zip in data.state_specific) {
    ORIGINALS[zip] = data.state_specific[zip].description;
  }

  // Helper: parse breed from "Breed, 612" or plain "Breed"
  function parseBreed(desc) {
    const breed = (desc || "").split(",")[0].trim();
    return breed;
  }

  // Helper: normalize to match MANIFEST keys
  function normBreed(b) {
    return (b || "").toLowerCase().replace(/\s+/g, " ").trim();
  }

  // Helper: pick random item
  function pick(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
  }

  // OPTIONAL: if you want each ZIP to keep the same random image for the whole session,
  // uncomment this cache and use it in over_state below.
  // const CHOICE_CACHE = {};

  // 4) On hover, inject HTML (breed + random image) into description and refresh that state
  simplemaps_cityzipmap.hooks.over_state = function (zip) {
    const s = data.state_specific[zip];
    if (!s) return;

    const breed = parseBreed(s.description);
    const imgs = DOGS_BY_KEY[normBreed(breed)];
    if (!imgs || imgs.length === 0) return; // no image for this breed → leave default popup

    // const img = CHOICE_CACHE[zip] || (CHOICE_CACHE[zip] = pick(imgs)); // sticky image
    const img = pick(imgs); // new random image on each hover

    // Build popup HTML
    const html = `
      <div style="min-width:220px;max-width:280px">
        <div style="font-weight:700;margin-bottom:6px">${breed}</div>
        <img src="${img}" alt="${breed}" style="max-width:100%;display:block;border-radius:8px" />
      </div>
    `;

    s.description = html;
    simplemaps_cityzipmap.refresh_state(zip);
  };

  // 5) On mouse out, restore the original text description
  simplemaps_cityzipmap.hooks.out_state = function (zip) {
    const s = data.state_specific[zip];
    if (!s) return;
    s.description = ORIGINALS[zip];
    simplemaps_cityzipmap.refresh_state(zip);
  };
})();
