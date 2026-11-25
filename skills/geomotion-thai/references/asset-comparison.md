# Asset comparison

Compare [actual reference crops vs rendered models](Asset_Comparison.jpg) and [complete rendered catalog](Icon_Catalog.jpg). All right-hand images were rendered from the bundled procedural models, not concept images.

| Object | Shared features | Actual differences / status |
|---|---|---|
| Aircraft | White fuselage, swept wings, two engines, dark windows, oblique view | Orange tail added; proportions and cockpit simplified, wing/engine detail reduced, no airline branding. Usable stylized symbol; not a photoreal replica. |
| Train | Orange/white body, dark glazing, roof units, multiple cars, distinct wheels and rails | Boxier cab, shorter train, simplified wheel/undercarriage; supports +Y-forward path motion. Stylized approximation. |
| Container ship | Navy/red hull, white bridge, colored container stacks, separate wake | Fewer containers, angular hull, bridge placement simplified, procedural wake without fluid simulation. Stylized approximation. |
| Dam/reservoir | Pale concrete structure, curved segments, blue water/spillways | Low-detail segmented wall; no realistic hydraulic/structural detail. Icon scale, not engineering data. |
| City | White and glass buildings, varied heights, gold floor accents | Five abstract buildings; no photoreal landmark reconstruction or dense street/house network. Generic city marker. |
| Tracks | Separate parallel rails and sleepers | Simplified symbolic gauge; demo curve is not a real railway alignment. |
| Car/factory/tree/mountain/pin | Original geometry following the shared palette | These are topic-supporting extensions, not exact traced reference objects. No separate reference crop exists for all of them. |

Acceptance here covers reusable stylized silhouettes/layers, not reference-identical realism. Preserve this distinction on delivery. New model substitutions need a fresh comparison render. The library includes `.blend`, transparent PNGs and source generator, so shape/proportion/material refinements remain editable.

Four separate arrowhead PNGs (triangle, chevron, diamond, double) are rendered resources; route configuration selects the same generator. They are geometric infographic variants, not a reconstruction of every reference arrow's material or curvature.
