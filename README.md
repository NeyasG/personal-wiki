# Neyas Guruswamy's Personal Wiki

This repository contains the source code for my personal wiki/blog, built using the [Hugo](https://gohugo.io/) static site generator and the [Stack theme](https://github.com/CaiJimmy/hugo-theme-stack). The site serves as a platform to document my learnings in programming, particularly focusing on personal Data Engineering projects. It is hosted on GitHub Pages.

## Development

To run the development server locally and view the site with draft posts included:

```bash
hugo server -D
```

Alternatively, you can use the pre-configured VS Code task "Serve Drafts" defined in [`.vscode/tasks.json`](.vscode/tasks.json). This will start the server in the background.

The site will typically be available at `http://localhost:1313/`.

## Building

To build the static site files for deployment:

```bash
hugo
```

This command generates the static files in the `public/` directory (which is ignored by Git as specified in [`.gitignore`](.gitignore)).

You can also use the VS Code task "Build" defined in [`.vscode/tasks.json`](.vscode/tasks.json).

## Deployment

Deployment to GitHub Pages is automated via the GitHub Actions workflow defined in [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml).

-   When changes are pushed to the `master` branch, the workflow automatically builds the site using `hugo --minify --gc`.
-   The contents of the `public/` directory are then deployed to the `gh-pages` branch, which is configured as the source for GitHub Pages.

## Updating the Theme

The Hugo Stack theme is included as a Hugo Module, specified in [`config/_default/module.toml`](config/_default/module.toml) and [`go.mod`](go.mod).

### Automatic Updates

A GitHub Actions workflow defined in [`.github/workflows/update-theme.yml`](.github/workflows/update-theme.yml) runs daily to check for and apply theme updates automatically.

### Manual Updates

To update the theme manually, run the following commands:

```bash
hugo mod get -u github.com/CaiJimmy/hugo-theme-stack/v3
hugo mod tidy
```

Commit the changes to [`go.mod`](go.mod) and [`go.sum`](go.sum) after updating.

> Note: This project uses `v3` of the theme. If a major new version (e.g., `v4`) is released, you may need to manually update the path in [`config/_default/module.toml`](config/_default/module.toml).

## Configuration

Key configuration files are located in the `config/_default/` directory:

*   [`config.toml`](config/_default/config.toml): Main Hugo configuration, including `baseURL`, `languageCode`, and `title`.
*   [`params.toml`](config/_default/params.toml): Theme-specific parameters, sidebar configuration, article settings, widgets, and comment settings.
*   [`menu.toml`](config/_default/menu.toml): Configuration for main and social menus.
*   [`markup.toml`](config/_default/markup.toml): Markdown rendering options, including table of contents and code highlighting.
*   [`permalinks.toml`](config/_default/permalinks.toml): URL structure for different content types.
*   [`related.toml`](config/_default/related.toml): Configuration for related content suggestions.

Content is primarily stored in the [`content/`](content/) directory, organized into sections like `post/` and `page/`. Static assets like images are stored in [`assets/`](assets/) or [`static/`](static/).

## Icons via CDN

Icons (e.g., social logos) are sourced from [Simple Icons](https://simpleicons.org/) via the [jsDelivr CDN](https://www.jsdelivr.com/).

-   **Find Icon Name:** Browse [simpleicons.org](https://simpleicons.org/).
-   **Construct URL:** `https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/ICON_NAME.svg` (replace `ICON_NAME`).
-   **Usage:** Use the URL where an image link is needed (e.g., in front matter).