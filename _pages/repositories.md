---
layout: page
permalink: /repositories/
title: Repositories
description: A collection of my open-source projects and contributions.
nav: true
nav_order: 2
---

## GitHub Repositories

{% if site.data.repositories.github_users %}

<div class="repositories d-flex flex-wrap bg-inherit">
  {% for user in site.data.repositories.github_users %}
    {% include repository/repo_user.liquid username=user %}
  {% endfor %}
</div>

---

{% endif %}

{% if site.data.repositories.github_repos %}

<div class="repositories d-flex flex-wrap bg-inherit">
  {% for repo in site.data.repositories.github_repos %}
    {% include repository/repo.liquid repository=repo %}
  {% endfor %}
</div>

{% endif %}

## Star This Project

If you find my work helpful, please consider giving it a star on GitHub!

<div style="margin-top: 1rem;">
  <a class="github-button" href="https://github.com/SiO-2/kvcloak" data-color-scheme="no-preference: light; light: light; dark: dark;" data-icon="octicon-star" data-size="large" data-show-count="true" aria-label="Star SiO-2/kvcloak on GitHub">Star</a>
</div>

<script async defer src="https://buttons.github.io/buttons.js"></script>
