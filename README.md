# RunTime Dive Systems

A GitHub-owned project showcase, workshop blog, and photo log for runtimedivesystems.com. First design prepared October 28, 2026. Tern-inspired structure with original RunTime design and artwork.

## Start here, Josh

1. Sign in to **Jdd227** on GitHub.
2. Create a new repository named **runtime-dive-systems**. Choose Public if using GitHub Free. Initialize it with a README. This website source and any photos you add will be public.
3. Send the repository link back in our chat. I can help put these files in the repository. The GitHub connection available in this session cannot create the repository for you.
4. Once files are uploaded, open **Settings → Pages → Build and deployment → Source → GitHub Actions**.
5. Open **Actions → Publish RunTime → Run workflow**. Pick main and run it if the first automatic run happened before Pages was enabled.
6. Wait for a successful deployment. Open **Settings → Pages → Visit site** to see the initial github.io address.
7. Review the welcome post and statuses before connecting the public domain. They are starter editorial copy based on the projects discussed, not a record of new tests. Edit or remove the welcome post if desired.

You do not need a paid CMS or a new hosting account for this setup. GitHub plan eligibility and current terms still apply. This is a static publishing site: visitors can read posts and view photos; there is no online admin login, public upload form, or comment system.

## If you prefer uploading everything yourself

Unzip the package. Use GitHub Desktop to clone the new repository to your Mac. Copy the **contents** of this source folder into the cloned repository, including `.github/workflows/pages.yml`. In Finder, Command + Shift + period reveals hidden files. Do not copy `.openai`, `dist`, or `__pycache__`. Keep the files at the repository root, not inside an extra runtime-site folder.

In GitHub Desktop, review the changes, write “Add RunTime website”, click **Commit to main**, then **Push origin**. Follow the Pages steps above. The public website is generated from content and assets; you do not upload a ZIP as the website.

## Your first blog post, using GitHub in your browser

No code changes needed for routine posts.

1. Open the repository and click **content → posts**.
2. Click **Add file → Create new file**.
3. Name it `2026-11-01-your-post-title.md` (use the actual date, lowercase letters, numbers, and hyphens).
4. Copy the contents of `POST-TEMPLATE.md` into it.
5. Change the title, date, project, and excerpt. Keep metadata on single lines. Do not add surrounding quotation marks to values. A colon inside the title is fine.
6. Write the post below the second `---` line.
7. Leave `draft: true` to save without publishing. Set **draft: false** when ready.
8. Click **Commit changes**. Commit to main to publish directly. If GitHub requires a branch, create it, open a pull request, and merge it when ready.
9. Watch the Actions tab for a successful “Publish RunTime” run, then reload the site.

The homepage automatically shows the three latest published posts, newest date first. Drafts are excluded from the generated site, but their source text is visible in a public repository. Future dates do not schedule publication: any file with `draft: false` publishes on the next build. Each post gets its own page, and the workshop log can be searched and filtered by project.

### Example post

```markdown
---
title: An update from the workbench
date: 2026-11-01
project: TriCell
excerpt: A quick look at this week's progress.
draft: true
---
Today I worked on the next housing iteration.

## What changed

- Describe the change.
- Explain what you still need to check.

![Housing on the workbench](assets/photos/tricell-housing.jpg)

## Next step

Write what you plan to do next.
```

Supported formatting: paragraphs separated by blank lines, `##` or `###` headings, `-` bullet lists, `**bold**`, inline backticks, links, images, `>` quotes, and fenced code blocks. This is a small Markdown subset. Tables, numbered-list formatting, embedded HTML, and embedded videos are not supported. HTML is escaped for predictable publishing.

## Add pictures to a blog post

1. Export pictures as JPG, PNG, or WebP. Convert iPhone HEIC photos first. Around 1600–2400 pixels wide and under 1 MB each is a useful target.
2. Use simple filenames like `tricell-housing.jpg`, with no spaces or parentheses.
3. In the repository open **assets → photos**. Click **Add file → Upload files**. Select or drag in the picture and commit it.
4. Edit your post and place this on its own line:

   `![A description of the picture](assets/photos/tricell-housing.jpg)`

5. Commit your post. The description becomes accessible alternative text. Match the filename and capitalization exactly.

The builder checks local image paths. A missing or incorrectly named picture stops the publish run, leaving the previous deployed version in place. Complete the photo upload before publishing the post that uses it. To replace a photo, upload a replacement with the same filename. Only upload images you want public; public repository history can retain older versions.

## Add a picture to the Photo log

Blog photos and Photo log entries are separate, so you control which images appear in the gallery.

After uploading an image to assets/photos, edit `content/gallery.json`. Replace the initial `[]` with:

```json
[
  {
    "file": "assets/photos/tricell-housing.jpg",
    "alt": "TriCell housing sitting on the workbench",
    "caption": "A new housing iteration."
  }
]
```

For another picture, add a comma between objects:

```json
[
  {"file":"assets/photos/first.jpg","alt":"Describe the first image","caption":"First caption"},
  {"file":"assets/photos/second.jpg","alt":"Describe the second image","caption":"Second caption"}
]
```

Do not put a comma after the final object. Commit changes. Each gallery photo opens in an enlarged viewer; Close or Escape returns to the gallery. Until you add images, the site shows an honest empty state rather than stock images presented as your work.

## Update project descriptions, links, and statuses

Edit `content/projects.json`. Each entry has name, description, body, status, url, and note fields. Keep JSON double quotes and commas intact. Keep existing slugs stable so shared links continue to work.

- `Running`: a tool currently in use; this is not a monitored uptime result.
- `Pilot`: a tool being tested with users.
- `In development`: work in progress.
- The `url` opens the actual application. Empty means there is no launch button.

Verified from existing GitHub CNAME files:

- DPV Planner: https://dpvplanner.runtimedivesystems.com/
- Labels: https://labels.runtimedivesystems.com/

Innerspace application URL supplied in the project context: https://app.innerspacescubasociety.com/. Check its current availability and desired project stage before launch. A welcome post and manually maintained status labels are included as editable starting content. No current uptime or fresh equipment tests are claimed.

## Connect runtimedivesystems.com

Do this after the github.io preview works. Tell me where the domain's DNS is managed so we can walk through its exact screen together. We have not changed DNS or claimed that the domain is live.

1. In GitHub account settings, use **Pages** to verify the domain with the TXT record GitHub supplies, if available. Use its exact record value.
2. In this new repository, open **Settings → Pages → Custom domain**, enter `runtimedivesystems.com`, and Save **before** changing DNS.
3. At the DNS provider, set the root/apex A records (`@`) to these GitHub Pages addresses:

   | Type | Host | Value |
   | --- | --- | --- |
   | A | @ | 185.199.108.153 |
   | A | @ | 185.199.109.153 |
   | A | @ | 185.199.110.153 |
   | A | @ | 185.199.111.153 |
   | CNAME | www | jdd227.github.io |

4. Replace conflicting records for **@ or www only** as appropriate to the provider. Preserve the existing `labels` and `dpvplanner` records, mail records, and other unrelated records. Those apps stay in their own repositories and continue to run separately.
5. Wait for GitHub's DNS check and certificate provisioning. DNS may take up to 24 hours. Enable **Enforce HTTPS** once it becomes available.
6. Re-run “Publish RunTime” after configuring the domain. The workflow reads GitHub's base path and builds correct URLs for either a repository preview or the root custom domain.
7. Check home, project launch buttons, one post, and photos over HTTPS.

This workflow uses GitHub Actions. The custom domain is configured in Pages settings; a source CNAME file is not required for an Actions deployment.

## If an update doesn't show up

- Open Actions. A red run means the new version did not deploy. Open the Build site step for the exact error.
- A common error is a missing photo, invalid JSON, or missing post metadata. Fix the named file and commit again.
- A green run means publication completed. Refresh the page or use a private window to rule out stale browser content.
- If you committed to another branch, merge that branch into main to trigger publishing.
- To undo a content change, open the file's History, copy the previous contents back into the file, and commit. If working with me, share the repository link and describe the version to restore.

## Developer notes

Python 3.10+ only; no packages to install. Run `python3 build.py` from the source folder. Generated output goes to `dist/`. `BASE_PATH=/runtime-dive-systems python3 build.py` builds for a repository subpath. The workflow determines the correct base path automatically. The builder validates all local href/src paths and excludes drafts. The CSS uses Google Fonts with system fallbacks; the site remains usable if fonts cannot load. No analytics or visitor tracking are installed.

The original vector artwork is decorative, not a navigational chart or photographic record. The site does not calculate live diving data. Existing applications open separately.

Official references checked October 28, 2026:
- https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site
- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site
- https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository
