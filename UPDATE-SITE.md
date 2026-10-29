# Update your RunTime website

The site publishes automatically after changes are committed to the main branch. No GoDaddy or DNS changes are needed for normal updates.

## Add your own images

Upload public JPG, PNG, or WebP images into assets/photos. Use simple lowercase filenames without spaces. Blog images, portfolio photos, and product images can use the same folder.

### Underwater portfolio

1. Open **assets → photos** in your GitHub repository.
2. Choose **Add file → Upload files**, select your new photo, then **Commit changes** to main.
3. Open **content → gallery.json** and click the pencil to edit.
4. Add a comma after the previous photo entry, then add the new entry before the final closing `]`. Use the format below. Keep the existing entries to retain the current photos.
5. Click **Commit changes** and commit to main. Check **Actions → Publish RunTime** for a green check, then refresh Photography.

This example shows a gallery with one photo:

```json
[
  {
    "file": "assets/photos/octopus.jpg",
    "alt": "Describe what the photograph shows",
    "caption": "Your caption and optional location"
  }
]
```

A `thumbnail` field is optional. It can point to a smaller preview file, while `file` points to the larger image opened by the viewer. If omitted, the same image is used for both.

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
- Photography: your underwater photographs in a clickable gallery.
- Products & designs: JJ tube weights, DPV light holders, DPV compass, SeeSpray, and TriCell.
- Blog: text and photos documenting work in progress and finished work.
- Gear: equipment snapshot and configuration notes.
- Privacy: describes the actual static site, hosting, absence of analytics/forms, and linked-app boundaries.
- Project-use warning: explains that personal projects do not replace safety equipment, procedures, training, official maps, or independent planning.

Privacy and warning text describe this version; they are not a claim of legal review or product certification. If you later add sales, forms, analytics, or other features, review and update the policy.
