---
title: "Deep Dive into Pytest: Fixtures, Scopes, Parameterization, and Testing Spark Remotely"
description: "An intermediate look at solving my testing problems"
date: 2025-04-28 22:21:04+0000
lastmod: 2025-04-28T22:59:13+01:00
categories:
    - Deep Dive
    - Testing
tags:
    - Pytest
draft: true
---

## Test hard. Test often

If there is one thing I wish I learned earlier in my programming journey, it would be: 

> **DON'T. SKIP. TESTING.**

Well now I'm slightly older and perhaps slightly wiser, I'm starting to see the benefits of approaching a programming problem from a *testing first* workflow. Today in my work I was building out a metadata system to programmatically gather metadata from external sources (yeah okay... it's Excel 😔) and parse them into a standardised format that could be applied to table comments and table tags within [Unity Catalog](https://www.databricks.com/product/unity-catalog).

Test changes
