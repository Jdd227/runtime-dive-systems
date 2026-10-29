# RunTime v2: upload this update

This update replaces the first site's design with a simple personal portfolio using your existing RunTime logo. It adds software, photography, designs, blog, gear, privacy, and project-use warning pages.

## Publish using GitHub's website

1. Unzip RunTime-Dive-Systems-v2.zip on your Mac.
2. Open your existing repository: https://github.com/Jdd227/runtime-dive-systems
3. Choose **Add file → Upload files**.
4. Open the extracted RunTime-Dive-Systems-v2 folder. Drag its **contents** onto GitHub: build.py, assets, content, README.md, POST-TEMPLATE.md, and this guide. Drag the folders as well as the files so their relative paths are retained. Do not drag the enclosing RunTime-Dive-Systems-v2 folder itself.
5. Commit to **main** with “Simplify RunTime website and add portfolio sections”.
6. Watch **Actions → Publish RunTime**. A successful run publishes the new version automatically.

This archive deliberately leaves out the already-installed .github publishing workflow and old generated dist directory. Your existing workflow runs build.py and generates a fresh dist folder. You do not need to change Pages or DNS for this redesign. Existing tracked dist files may remain in the repository; the workflow uses fresh generated output.

## Add your own images

Upload public JPG, PNG, or WebP images into assets/photos. Use simple lowercase filenames without spaces. Blog images, portfolio photos, and product images can use the same folder.

### Underwater portfolio

Edit content/gallery.json. Replace [] with entries like:

```json
[
  {
    "file": "assets/photos/octopus.jpg",
    "alt": "Describe what the photograph shows",
    "caption": "Your caption and optional location"
  }
]
```

Each entry appears on Photography and the first three appear on the homepage. Clicking a photo opens the enlarged viewer. Add only photographs you want public and have permission to publish.

### Product and design photos

Edit content/products.json. Each item has an images array. Replace its empty [] with:

```json
[
  {"file":"assets/photos/jj-tube-weights.jpg","alt":"Custom weights on the JJ"}
]
```

Photos appear on that design's individual page. Descriptions, notes, and status can be edited in the same file. The existing descriptions intentionally avoid invented dimensions or test claims. Add your real specifications and build notes when ready.

### Gear and configuration

Edit content/gear.json to update the equipment list and configuration notes. It starts with the JJ-CCR, Genesis 2.2, Petrel 3 / Perdix, existing Nikon / Aquatica camera, and analyzers discussed previously. Review this snapshot for changes before publishing. Planned camera upgrades are not listed as currently owned.

To include configuration photographs, add image entries to the images array in content/gear.json. Each entry uses file, alt, and an optional caption, following the same format as the underwater portfolio. The configuration field is plain text.

### Blog

Create a new file in content/posts using POST-TEMPLATE.md. Use a filename like 2026-11-01-project-update.md. Fill in the metadata, write your post, and set draft: false when ready. Upload images first, then refer to them as:

![Describe the picture](assets/photos/your-file.jpg)

Publishing automatically updates the blog and homepage. Keep draft: true while writing; draft files are not published on the site but remain visible in a public repository.

## Included pages

- Home: a short introduction and the five main areas.
- Software: DPV Planner, Dive Current, Gas Label Studio, and Innerspace.
- Photography: your own images, with an honest empty state until uploaded.
- Products & designs: JJ tube weights, DPV light holders, DPV compass, SeeSpray, and TriCell.
- Blog: text and photos documenting work in progress and finished work.
- Gear: equipment snapshot and configuration notes.
- Privacy: describes the actual static site, hosting, absence of analytics/forms, and linked-app boundaries.
- Project-use warning: explains that personal projects do not replace safety equipment, procedures, training, official maps, or independent planning.

Privacy and warning text describe this version; they are not a claim of legal review or product certification. If you later add sales, forms, analytics, or other features, review and update the policy.
