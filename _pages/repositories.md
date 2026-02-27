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
