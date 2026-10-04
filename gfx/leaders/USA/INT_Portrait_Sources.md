# Interwar United States portraits

Generated with the built-in `image_gen` tool on 2026-10-04. Historical photographs guide facial likeness; these are new painted game portraits rather than archival photographs.

## Game assets

All three assets are 156 x 210 pixels, opaque RGBA DDS, assigned by direct texture path in `common/characters/INT - United States.txt`.

| Leader | Asset | Identity reference |
| --- | --- | --- |
| Warren G. Harding | `gfx/leaders/USA/INT_Warren_G_Harding.dds` | [Library of Congress, Harris & Ewing, hec.18296](https://www.loc.gov/pictures/item/2016859359/) |
| Calvin Coolidge | `gfx/leaders/USA/INT_Calvin_Coolidge.dds` | [Library of Congress, cph.3a53302](https://www.loc.gov/pictures/resource/cph.3a53302/) |
| Herbert Hoover | `gfx/leaders/USA/INT_Herbert_Hoover.dds` | [Library of Congress, Underwood & Underwood, cph.3a25105](https://www.loc.gov/pictures/item/96522651/) |

Historical reference downloads and the preview are in `.codex/usa_interwar_portraits/`. The mod's existing Woodrow Wilson portrait provides the painted style reference. The existing Wilson and Roosevelt assignments are unchanged.

## Generation prompts

Each portrait used the following common prompt, followed by its individual subject paragraph. Reference image 1 is the corresponding historical photograph. Reference image 2 is `.codex/usa_interwar_portraits/existing_style.png`.

> Use case: historical-scene. Asset type: Hearts of Iron IV country-leader portrait. Create ONE polished, restrained painted color head-and-shoulders portrait suitable for a 156x210 pixel game panel, vertical aspect ratio 26:35. Input image 1 is a historical identity reference, NOT the final style; input image 2 is a style reference showing the mod's Woodrow Wilson portrait on the LEFT: follow ONLY that left portrait's close framing, muted colors, subtle painted realism, clear face contours and subdued warm gray-beige background; IGNORE the right-hand black-and-white portrait. The new image must contain ONLY the requested single leader. Keep the subject's recognizable face and era-specific hairstyle from the historical reference, with realistic skin and restrained brushwork. Formal dark charcoal suit, white shirt and period necktie. Face and upper torso fill the panel, crop below the chest with no hands visible, top of hair fully visible, sober presidential expression, slight three-quarter turn. Natural side lighting, readable eyes, broad simple shapes that survive thumbnail reduction. Clean full-bleed muted warm gray-beige backdrop. Not a raw colorized photo, not a modern glossy photograph, not a caricature. No vignette black corners, frames, borders, words, signature, logo, watermark, flags, props, badges, decorative UI, collage or multiple faces.

### Warren G. Harding

> Subject: Warren G. Harding as president in 1921–1923, in his mid-to-late fifties: broad square clean-shaven face, heavy dark brows, distinguished silver-gray short hair with a side part, strong jaw and straight broad nose. Keep his distinctive features from image 1. Remove the hand from the reference pose and draw a dignified upright head-and-shoulders bust.

### Calvin Coolidge

> Subject: Calvin Coolidge as president in 1923–1929, in his early-to-mid fifties: narrow clean-shaven face, high forehead, thin lips, long straight nose, receding short light-brown hair combed to the side, composed reserved expression. Faithfully preserve the face proportions in image 1.

### Herbert Hoover

> Subject: Herbert Hoover as president in 1929–1933, in his mid-to-late fifties: broad rounded clean-shaven face, small slightly hooded eyes, strong brow, neatly side-parted graying light-brown hair, fuller cheeks and sober thoughtful expression. Faithfully preserve the face proportions in image 1.
