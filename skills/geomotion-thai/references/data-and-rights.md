# Data, geographic accuracy and resource rights

## Sources bundled or fetched

| Resource | Source | Use and attribution |
|---|---|---|
| Country polygons | [Natural Earth 1:50m](https://www.naturalearthdata.com/), [repository](https://github.com/nvkelso/natural-earth-vector) | Public domain. Generalized modern boundaries; not a cadastral/engineering source. [Terms](https://www.naturalearthdata.com/about/terms-of-use/). |
| Rivers | Natural Earth `ne_50m_rivers_lake_centerlines` | Generalized river lines, not water-body widths or hydrology measurements. |
| Elevation | [Mapzen Terrain Tiles on AWS](https://registry.opendata.aws/terrain-tiles/), `elevation-tiles-prod/terrarium/z/x/y.png` | Real blended DEM. Decode `R×256+G+B/256−32768` metres. [Encoding](https://github.com/tilezen/joerd/blob/master/docs/formats.md), [attribution](https://github.com/tilezen/joerd/blob/master/docs/attribution.md). Retain full notices bundled under assets/geodata. |
| Modern Thai flag | [flagcdn PNG](https://flagcdn.com/w640/th.png) | Illustration source; verify design/period separately. Demo has 5 stripes red-white-blue-white-red, thickness 1:1:2:1:1. [Thai government flag description](https://www.thailand.go.th/page/flag). The modern tricolour date is supported by [Thai MFA National Flag chapter, p.112](https://image.mfa.go.th/mfa/0/LkQFxO2KRZ/eBook_More_Alike_Than_We_Might_Think_FINAL.pdf). Do not infer historical variants from country code. |
| Kanit Medium/SemiBold | [Google Fonts Kanit](https://github.com/google/fonts/tree/main/ofl/kanit) | SIL Open Font License 1.1; full `assets/fonts/OFL.txt` included. |
| Object models | Original `scripts/models.py` | Original procedural geometry, editable layers. Design approximation; no extracted third-party model/texture. |
| Sound cues | Original `compose.effects()` | Deterministic synthesized whoosh/pop/clacks, not third-party recordings. |
| Visual reference crops | User's two attached reference images | Comparison only; not inserted into production video and not treated as a watermark or geographic dataset. |

Terrain tiles combine multiple providers/regions. The attribution document lists provider terms, including USGS global SRTM/GMTED2010 and NOAA ETOPO1 and country-specific sources. Include the applicable complete attribution notice with any redistributed DEM/cache/project; do not call all elevation tiles “license-free.” The pipeline credits Natural Earth, Mapzen, USGS and NOAA on screen and retains the detailed notice. Review provider-specific requirements for a different region before publication.

## Accuracy protocol

Keep claim-level URLs, date accessed, uncertainty, historical date and units in project source records. Check contemporary versus historical flags and borders. Use official national datasets for administrative or politically sensitive boundaries. Record the dataset's treatment of disputed territory neutrally. Natural Earth geometry alone cannot settle a sovereignty dispute.

A country polygon/point coordinate can support a place marker, but cannot establish a real road/rail/shipping path. Demo routes are explicitly schematic. Use actual OSM/official network geometry with its own attribution when real routing is needed. Do not infer travel times, service frequency or distance from scene-unit curves.

Elevation is transformed into a mesh, not invented shading. Record vertical exaggeration (24× demo) on screen and in metadata. Preserve height relationships; do not claim the visual slopes or model-sized vehicles are to scale. Regional triangulation and generalized boundaries limit small-feature accuracy. City-level flood/engineering analysis needs an appropriate DEM/resolution/vertical datum, local projection and domain verification beyond this animation adapter.

Source downloads use HTTPS and bounded requests. Record SHA256 and exact tile URLs with prepared data. Keep downloaded raw source/cache inputs with the editable source where practical; successful cached preparation can be repeated without redownloading. No map-provider private API, auth token, satellite imagery extraction or unlicensed source-video copying is used.
