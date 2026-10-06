# Research: content, health, multilingual and governance evidence for the multi-site SEO platform

Checked: 5 October 2026. GET requests only. No website was changed.

Trust labels:
- **primary**: Google Search Central, the Google Search Quality Rater Guidelines (QRG) PDF, schema.org, a government site, a law text, or a peer-reviewed paper.
- **secondary**: an industry news site or a statistics site.
- **vendor**: a tool maker's own docs or blog.
- **inference**: our own reading, not a statement in the source.
- **observed**: we fetched it from the client site today.

This file does not repeat `docs/mypipit/research-evidence.md` or `docs/rethink/03-research-content-methods.md`. It points to them where they overlap.

---

## 0. Correction to the extendmy.life observations (observed, 5 Oct 2026)

The brief said there were "no hreflang links between /en and /de pages". A GET request with a normal browser user agent shows that **hreflang is present in the HTML `<head>`** on every page type we checked:
- category: `/en/category/longevity-clinics`
- subcategory and regrouping pages
- article: `/en/article/healthspan-vs-lifespan`
- clinic (product): `/en/product/longevity-medical-center-italy`
- static: `/en/aboutus`

Each page lists `en`, `de` and `x-default`, and has a self-canonical. The DE pages return the same set, so the links go both ways. The attribute is written `hrefLang` (React style). HTML attribute names are not case-sensitive, so this is fine.

Remaining issues:
- **x-default URL redirects.** The x-default URL (for example `https://extendmy.life/article/healthspan-vs-lifespan`) returns **307 (temporary redirect) to the /en/ version**. It does this for a Googlebot user agent and for `Accept-Language: de` too. Google allows x-default on "auto-redirecting home pages", so this is not an error. It is simpler and clearer to point x-default straight at the `/en/` URL (inference). One possible cause of the earlier finding: a tool that strips `<head>` or does not render the page.
- **No hreflang in the sitemaps.** The 12 sitemaps have no `xhtml:link` entries. This is fine because the HTML method is used. Google needs only one method.
- **Every lastmod is the time the sitemap was built.** All `<lastmod>` values equal `2026-10-05T01:44:5x Z` (82 of 82 EN articles; 125 of 125 EN products, which differ only by milliseconds). See section 5.
- **The shared category meta description is confirmed.** "Explore categories and detailed product collections." is on the category, subcategory and regrouping pages.
- **The DE article is a real German text.** It has a German title, description and H1, so it is not boilerplate-only translation.

---

## 1. YMYL, E-E-A-T and health content

1.1 **Latest QRG version: 11 September 2025, 182 pages.** We downloaded the PDF today. Its header reads "General Guidelines … September 11, 2025".
- Secondary sources report that some blogs claim a June 2026 edition. The PDF Google hosts is still the September 2025 one.
- Source: "Search Quality Rater Guidelines", Google. https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf (date on document: 11 Sep 2025).
- Trust: primary.

1.2 **YMYL definition (QRG §2.3).** Health is the first YMYL type.
- Quote: "Some topics have a high risk of harm because content about these topics could significantly impact the health, financial stability, or safety of people, or the welfare or well-being of society. We call these topics 'Your Money or Your Life' or YMYL."
- Quote: "YMYL Health or Safety: Topics that could harm mental, physical, and emotional health, or any form of safety…"
- Quote: "mild inaccuracies or content from less reliable sources could significantly impact someone's health…"
- Inference: longevity clinics, treatments, biomarkers and aesthetic procedures are YMYL Health. Retreat pages are YMYL where they make health claims.
- Trust: primary.

1.3 **Trust is the centre of E-E-A-T (QRG §3.4).**
- Quote: "The most important member at the center of the E-E-A-T family is Trust." / "Informational pages on clear YMYL topics must be accurate to prevent harm to people and society."
- Quote (§3.4): "Trust is the most important member of the E-E-A-T family because untrustworthy pages have low E-E-A-T no matter how…"
- Trust: primary.

1.4 **Who must write it: experts, not only experience (QRG §3.4.1).**
- Quote: "If the purpose of a page on a clear YMYL topic is to give information or offer advice, a high level of expertise may be required for the page to be trustworthy." / "some types of YMYL information and advice must come from experts."
- The QRG's examples for "best left to experts" include "Sleep medications that are safe during pregnancy" and "Different treatment options for liver cancer and the associated life expectancies."
- Personal-experience pages can still rate high if they are "trustworthy, safe, and consistent with well-established expert consensus."
- Inference: treatment explanations, biomarker advice and clinic medical claims need an expert author or reviewer. A traveller-style "my retreat experience" piece does not.
- Trust: primary.

1.5 **Who is responsible must be clear (QRG §4.5.1, §2.5.2).**
- Quote: "For pages that require a high level of trust, information about who created the content and who is responsible for the content is critical."
- "Inadequate information about the website or content creator for its purpose" is on the list of signs of an untrustworthy page.
- Trust: primary.

1.6 **AI-written medical text at scale gets the lowest rating (QRG §4.6.5 / §4.6.6 and a worked example).**
- Quote: "The Lowest rating applies if all or almost all of the MC on the page … is copied, paraphrased, embedded, auto or AI generated, or reposted from other sources with little to no effort, little to no originality, and little to no added value…"
- Worked example, "This page is a YMYL medical article … Lowest: Scaled content abuse": "This is spam (scaled content abuse) and a highly untrustworthy medical page: it demonstrates no real expertise and may not be correct and is especially concerning for YMYL topics."
- The QRG also says: "the use of Generative AI tools alone does not determine the level of effort or Page Quality rating."
- Trust: primary.

1.7 **Google's own guide: YMYL must match expert consensus. The guide asks "written or reviewed by an expert?" and bans fake authors.**
- Source: "Creating helpful, reliable, people-first content", Google Search Central. https://developers.google.com/search/docs/fundamentals/creating-helpful-content (last updated 2026-10-01).
- Quote: "For topics that could significantly impact people's lives or well-being (YMYL topics), the content must be highly accurate and consistent with established expert consensus."
- Quote: "Is this content written or reviewed by an expert or enthusiast who demonstrably knows the topic well?"
- Quote: "our systems give even more weight to content that aligns with strong E-E-A-T for topics that could significantly impact the health…" / "E-E-A-T itself isn't a specific ranking factor."
- Who, How, Why:
  - Who: "Do bylines lead to further information about the author or authors involved, giving background about them and the areas they write about?"
  - How: "Is the use of automation, including AI-generation, self-evident to visitors through disclosures or in other ways?"
  - Why: "primarily to help people".
- Quote (new and important): "Fabricating creator profiles (such as by using AI-generated headshots, made-up names, or false credentials to make content appear as if it was written by human experts) is a form of deception."
- Trust: primary.

1.8 **Rater scores do not directly change ranking. Google's AI guidance points to QRG 4.6.6.**
- Source: "Google Search's guidance on using generative AI content…", https://developers.google.com/search/docs/fundamentals/using-gen-ai-content (last updated 2026-10-01).
- Quote: "they're used by our search raters to help evaluate the performance of our various search ranking systems, and their ratings don't directly influence ranking."
- Trust: primary. (The "fact-check all AI output, including metadata" rule is already in research-evidence.md 6.1.)

1.9 **Health information standard from outside SEO: PIF TICK criteria (UK Patient Information Forum), reviewed October 2024.**
- Source: "PIF TICK Criteria at a glance", https://pifonline.org.uk/download/file/enNzYldGUE8wYVlmUysrei9sL3BoQT09/criteria-at-a-glance-2024/
- Quotes:
  - "There is a designated person accountable for the overall quality of health and care information production."
  - "There is a process for version control and archiving…"
  - "A sign off process has been followed…"
  - "There is a process for reviewing and updating health and care information within appropriate timeframes."
  - "AI usage within your production process must be clearly documented."
  - "Appropriate experts/health professionals are involved in the information production process."
  - "The organisation has obtained, recorded and referenced up to date, relevant and trustworthy evidence sources."
- Trust: primary for UK health-information practice (it is not a Google rule).
- Unverified: secondary sites say PIF TICK requires a review "at least every 3 years". The criteria PDF only says "within appropriate timeframes".

1.10 **German law limits health advertising (Heilmittelwerbegesetz, HWG §11).** This matters for German drafts on aesthetic clinic pages.
- Outside professional circles, advertising for cosmetic surgery may not use before/after comparisons: "vergleichende Darstellung des Körperzustandes oder des Aussehens vor und nach dem Eingriff."
- Third-party statements (testimonials) are restricted when they are "missbräuchlicher, abstoßender oder irreführender Weise" (abusive, repugnant or misleading).
- Source: https://www.gesetze-im-internet.de/heilmwerbg/__11.html
- Trust: primary (law text). This is not legal advice. Whether a marketplace listing counts as "Werbung" (advertising) is a question for a lawyer (unverified).

**What this means for the platform (inference):**
- Mark longevity and aesthetic clinic pages and health articles as YMYL in the content model.
- For YMYL items, the workflow needs a required "medical reviewer" step: a named person with stated credentials, plus `lastReviewed`.
- Never invent authors, credentials or headshots (see 1.7).
- The engine may draft structure, headings and metadata. Every medical claim must be an `[ADD: …]` placeholder or a quote from a cited source, and an expert must check it. This extends the current "no invented facts" rule.
- Show "How" with a short disclosure that AI helped draft and an expert reviewed.
- In German, flag before/after and testimonial wording on aesthetic pages for a human check.

---

## 2. Medical and health structured data

2.1 **Google has no medical or health rich result.** The Search Gallery lists:
- Article, Breadcrumb, Carousel, Course list, Dataset, Discussion forum, Education Q&A
- Employer aggregate rating, Event, Image metadata, Job posting, Local business
- Math solver, Movie, Organization, Product, Profile page, Q&A, Recipe
- Review snippet, Software app, Speakable, Subscription/paywalled content, Vacation rental, Video

It has no MedicalWebPage, MedicalClinic, Physician or FAQ entry.
- Source: "Structured data markup that Google Search supports", https://developers.google.com/search/docs/appearance/structured-data/search-gallery (last updated 2026-06-15).
- Trust: primary.

2.2 **FAQ rich results are gone for everyone.** They were limited to "well-known, authoritative government and health websites" from 2023. The doc then said "This feature will no longer appear in Google Search starting May 7, 2026", and the doc was removed in June 2026.
- Secondary reports say Search Console reporting ended in June 2026 and API support ended in August 2026. They also say Google may still read FAQPage markup to understand the page.
- Source: https://developers.google.com/search/docs/appearance/structured-data/faqpage (fetched today; notices dated 2023-09-14, 2026-05-08, 2026-06-15). Secondary: techwyse.com, bluehost.com (2026).
- Trust: primary + secondary.
- Inference: do not sell "FAQ schema for rich results" in the platform.

2.3 **The schema.org health types exist and are valid. They give no Google rich result.** (schema.org V30.1, 2026-09-16)
- `MedicalWebPage`: Thing > CreativeWork > WebPage > MedicalWebPage. "A web page that provides medical information." Its own property is `medicalAudience`.
- `reviewedBy` (on WebPage): "People or organizations that have reviewed the content on this web page for accuracy and/or completeness."
- `lastReviewed` (on WebPage): "Date on which the content on this web page was last reviewed for accuracy and/or completeness."
- `MedicalClinic`: Organization > LocalBusiness > MedicalBusiness > MedicalClinic, and also under MedicalOrganization. Its own properties are `availableService` and `medicalSpecialty`.
- `MedicalBusiness` is a LocalBusiness subtype. Its subtypes include Dermatology, DietNutrition, MedicalClinic, Physician, PlasticSurgery, PrimaryCare and others.
- `Physician` is "an individual physician or a physician's office considered as a MedicalOrganization". It is an **organisation or place type, not a Person**. For a named doctor as author or reviewer, use `Person` with `jobTitle` and `hasCredential` or `knowsAbout` (inference from the type tree).
- Sources: https://schema.org/MedicalWebPage, https://schema.org/MedicalClinic, https://schema.org/MedicalBusiness, https://schema.org/Physician
- Trust: primary.

2.4 **Article/BlogPosting: nothing is required. Author and dates are recommended.**
- Quote: "There are no required properties; instead, add the properties that apply to your content."
- Recommended: `author`, `author.name`, `author.url`, `dateModified`, `datePublished`, `headline`, `image`.
- Author rules:
  - "Make sure that all the authors that are presented as authors on the web page are also included in markup."
  - "Use the Person type for people, and the Organization type for organizations."
  - "In the author.name property, only specify the name of the author."
- Dates use ISO 8601. Add a time zone; without one, Google uses Googlebot's time zone.
- Source: "Article structured data", https://developers.google.com/search/docs/appearance/structured-data/article (last updated 2026-09-08).
- Trust: primary.
- Inference for extendmy.life: an empty `author` and null dates are not errors that block anything. But they are a missed trust signal and they disagree with any visible byline or date. Either fill them from real data or leave the properties out. Never output empty or null values.

2.5 **General structured data rules that apply here.**
- "Don't mark up content that is not visible to readers of the page."
- "Your structured data must be a true representation of the page content."
- "Try to use the most specific applicable type…"
- Source: https://developers.google.com/search/docs/appearance/structured-data/sd-policies (last updated 2026-07-10).
- Trust: primary.
- Inference:
  - Clinic pages using `Article` is a poor fit. `MedicalClinic` (or `MedicalBusiness` / `HealthAndBeautyBusiness` for aesthetic or spa) with `address` is more specific.
  - Only add `reviewedBy` if the reviewer is visible on the page.

2.6 **LocalBusiness: `name` and `address` are required.**
- Recommended: `aggregateRating`, `department`, `geo`, `menu`, `openingHoursSpecification`, `priceRange`, `review`, `servesCuisine`, `telephone`, `url`.
- "Use the most specific LocalBusiness sub-type possible". The doc names no medical subtypes in its examples.
- Reviews and ratings: "This property is only recommended for sites that capture reviews about other local businesses."
- Source: https://developers.google.com/search/docs/appearance/structured-data/local-business (last updated 2026-09-08).
- Trust: primary.
- Inference: a marketplace that collects its own user reviews of clinics fits this rule. Copying a clinic's own testimonials does not, and HWG (1.10) also limits testimonials.

---

## 3. Multilingual SEO for EN/DE

3.1 **Sitemap method for hreflang.**
- Quote: "Specify the xhtml namespace as follows: xmlns:xhtml="http://www.w3.org/1999/xhtml"" / "Each `<url>` element must have a child element `<xhtml:link rel="alternate" hreflang="…">` that lists every alternate version of the page, including itself."
- Source: "Tell Google about localized versions of your page", https://developers.google.com/search/docs/specialty/international/localized-versions (last updated 2026-09-21).
- Trust: primary.

3.2 **The links must go both ways, and URLs must be full.**
- Quote: "If two pages don't both point to each other, the tags will be ignored."
- Quote: "Alternate URLs must be fully-qualified, including the transport method (http/https), so: https://example.com/foo, not //example.com/foo or /foo."
- Common errors: missing return links; wrong codes (use ISO 639-1, with an optional ISO 3166-1 region); "en-UK" is wrong (use "en-GB"); a region on its own is not valid.
- Trust: primary.

3.3 **x-default.**
- Quote: "The reserved x-default value is used when no other language/region matches the user's browser setting… it was designed for language selector pages."
- The same page also suggests x-default for "language/country selectors or auto-redirecting home pages".
- Trust: primary.

3.4 **Canonical together with hreflang.**
- Quote: "If you're using hreflang elements, make sure to specify a canonical page in the same language, or the best possible substitute language…" / "For canonicalization purposes Google prefers URLs that are part of hreflang clusters."
- Source: https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls (last updated 2026-07-10).
- Trust: primary.
- Inference: a /de page must never canonicalise to its /en twin. extendmy.life does this correctly (self-canonicals).

3.5 **How Google picks the language.**
- Quote: "Google uses the visible content of your page to determine its language. We don't use any code-level language information such as lang attributes, or the URL." / "Google Search tries to find pages that match the language of the searcher."
- Warning: "Translating only the boilerplate text of your pages while keeping the bulk of your content in a single language… can create a bad user experience…"
- Source: "Managing multi-regional and multilingual sites", https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites (last updated 2025-12-10).
- Trust: primary.
- Inference: the platform must check that DE main content is German, not only that the DE menus are German.

3.6 **Machine translation: allowed if good, reviewed by a native speaker.**
- Source: "June 2024 Google SEO Office Hours", https://developers.google.com/search/help/office-hours/2024/june
- Gary Illyes: "If the auto translation is of low quality, maybe. You should ensure that a human native in those languages reviews (and perhaps fixes) the translations…"
- John Mueller: "There's no special markup that you can add to your pages to label them as automatic translations… if you think they're good for your users, then making them indexable is fine." / "Localized content is not considered duplicate content."
- Trust: primary.
- See also research-evidence.md 6.3 and 14.4: unreviewed automated translation at scale counts as scaled content abuse.

3.7 **Search Console no longer reports hreflang errors.** The International Targeting report was removed after 22 September 2022.
- Source: Search Engine Roundtable, "Google Search Console Deprecates International Targeting Report", Aug 2022. https://www.seroundtable.com/google-search-console-deprecates-international-targeting-report-33983.html
- Trust: secondary.
- Inference: the platform must check hreflang itself: return links, codes, full URLs, status 200 of the target, and that the target self-canonicalises.

3.8 **German search market (StatCounter, September 2026):**

| Search engine | All platforms | Desktop only |
|---|---|---|
| Google | 87.84% | 69.98% |
| Bing | 6.49% | 19.42% |
| Yahoo! | 1.71% | 5.21% |
| Yandex | 1.56% | 1.40% |
| DuckDuckGo | 1.07% | 1.92% |
| Ecosia | 1.03% | 1.36% |

- Sources: https://gs.statcounter.com/search-engine-market-share/all/germany and https://gs.statcounter.com/search-engine-market-share/desktop/germany (fetched 5 Oct 2026).
- Trust: secondary (page-view sample, not query share).
- Inference: on desktop in Germany, Bing is about 1 in 5 searches. That is a reason to also submit to Bing Webmaster Tools and keep lastmod accurate (see 5.3).

---

## 4. Category and listing pages

4.1 **Faceted navigation (Google doc first published 17 Dec 2024).**
- Source: "Managing crawling of faceted navigation URLs", https://developers.google.com/search/docs/crawling-indexing/crawling-managing-faceted-navigation (last updated 2025-12-18). Announced in "Crawling December: Faceted navigation", https://developers.google.com/search/blog/2024/12/crawling-december-faceted-nav
- Problems it causes: overcrawling, and slower discovery of useful pages ("If crawling is spent on useless URLs, the crawlers have less time to spend on new, useful URLs").
- If facets need not be indexed: block them in robots.txt, using Google's example pattern `disallow: /*?*products=`, or use URL fragments.
- rel=canonical and rel=nofollow "are generally less effective in the long term".
- If facets must be indexed:
  - use `&` as the separator
  - keep a consistent filter order
  - "Return an HTTP 404 status code when a filter combination doesn't return results".
- Trust: primary.

4.2 **robots.txt matching rules.**
- Only `user-agent`, `allow`, `disallow` and `sitemap` are supported ("other fields such as crawl-delay aren't supported").
- `*` means "0 or more instances of any valid character". `$` means the end of the URL. Query strings are part of the match.
- The longest matching rule wins. On a tie, the least restrictive rule wins.
- Source: https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt (last updated 2026-08-31).
- Trust: primary.

**extendmy.life robots.txt (observed).** It has `Disallow: /*?sort=`, `/*?filter=` and `/*?product_type_id=`, then `/*?*min_price=`, `/*?*max_price=` and `/*?*sort_by_price=`. It also blocks `?ref=` and `utm_*`, and has `Host:`.
- `/*?sort=` matches only when `sort` is the **first** parameter. `/x?page=2&sort=asc` is **not** blocked. Google's pattern `/*?*sort=` would catch both (inference from the matching rules).
- `Host:` is ignored by Google; it is a Yandex directive (primary rule, inference applied).
- Blocking `?utm_*` and `?ref=` URLs means Google cannot see their canonical tag. This is fine as long as internal links never use these parameters (inference).

4.3 **Pagination.**
- Link each page to the next with `<a href>`.
- Give each page a unique URL (`?page=n`).
- "give each page its own canonical URL". Do not canonicalise all pages to page 1.
- Google "no longer uses" rel=next/prev.
- Use noindex or robots.txt for sort-order variants.
- Source: https://developers.google.com/search/docs/specialty/ecommerce/pagination-and-incremental-page-loading (last updated 2025-12-10).
- Trust: primary.

4.4 **Ecommerce URLs.**
- "Google does not use fragment identifiers in indexing."
- "Avoid internally linking to temporary parameters, such as session-IDs, tracking codes…"
- "Avoid using the same parameters twice."
- Source: https://developers.google.com/search/docs/specialty/ecommerce/designing-a-url-structure-for-ecommerce-sites (last updated 2025-12-10).
- Trust: primary.

4.5 **Duplicate meta descriptions.** This is already in research-evidence.md 2.2: "Identical or similar descriptions on every page of a site aren't helpful… programmatic generation of the descriptions can be appropriate and are encouraged."
- Inference for extendmy.life: build each category and subcategory description from its name, parent, clinic count and top locations, then have a human approve it. Give each subcategory its own H1 and not the parent's (see 8.3 on diversity and dedup). Google has no rule that names "subcategory H1"; this is a quality judgement.

---

## 5. Sitemap lastmod accuracy

5.1 **Google uses lastmod only if it matches reality.** Leave it out when you are not sure.
- Source: "Sitemaps ping endpoint is going away", Google Search Central Blog, **Monday 26 June 2023**. https://developers.google.com/search/blog/2023/06/sitemaps-lastmod-ping
- Quote: "we're using it as a signal for scheduling crawls to URLs that we previously discovered."
- Quote: "it needs to consistently match reality: if your page changed 7 years ago, but you're telling us in the lastmod element that it changed yesterday, eventually we're not going to believe you anymore when it comes to the last modified date of your pages."
- Quote: "You can use a lastmod element for all the pages in your sitemap, or just the ones you're confident about… some site software may not be able to easily tell the last modification date of the homepage or a category page… it's fine to leave out lastmod for those pages."
- Quote: "when we say 'last modification', we actually mean 'last significant modification'… if you changed the primary text, added or changed structured data, or updated some links, do update the lastmod value." Footer and sidebar changes do not count.
- The ping endpoint is deprecated. Submit sitemaps through robots.txt or Search Console.
- Trust: primary.
- See research-evidence.md 4.2 for the docs line "consistently and verifiably accurate".

5.2 **What identical lastmod on every URL does (inference from 5.1).** extendmy.life sets every lastmod to the moment the sitemap is built (observed). Google will learn that the value is not true and **ignore lastmod for the whole site**. A real update to one article then gets no faster recrawl from the sitemap. There is no penalty; the signal is simply lost.
- Fix: take lastmod from the CMS `updated_at` of the main content. Leave it out on category pages that only aggregate other pages.

5.3 **Bing says the same, and calls this exact mistake the most common one.**
- Source: "The Importance of Setting the lastmod Tag in Your Sitemap", Bing Webmaster Blog, 1 Feb 2023. https://blogs.bing.com/webmaster/february-2023/The-Importance-of-Setting-the-lastmod-Tag-in-Your-Sitemap
- Quote: "The date on most XML sitemaps was set to the date of generation of the sitemap, rather than the date of content modification." / "The date must be set to the date the linked page was last modified, not when the sitemap is generated." Bing found 18% of sitemaps had lastmod set wrong.
- Trust: primary for Bing (a search engine's own blog).

---

## 6. Content refresh, dates and re-audit frequency

6.1 **Do not change dates without real change. Adding or removing content just to look "fresh" does not help.**
- Source: "Creating helpful, reliable, people-first content" (last updated 2026-10-01).
- Quote: "Are you changing the date of pages to make them seem fresh when the content has not substantially changed?" / "Are you adding a lot of new content or removing a lot of older content primarily because you believe it will help your search rankings overall by somehow making your site seem 'fresh?' (No, it won't)."
- Trust: primary.

6.2 **How to show dates.**
- "Add a user-visible date to the page and feature it prominently. Label your dates appropriately with text like 'Publish' or 'Last updated'."
- Use `datePublished`/`dateModified` on a CreativeWork subtype.
- "Ensure that the date … match between the equivalent user-visible and structured values."
- "Don't specify future dates…"
- "Minimize the presence of other dates on the page."
- Source: "Influence your byline dates in Google Search", https://developers.google.com/search/docs/appearance/publication-dates (last updated 2025-12-10).
- Trust: primary.

6.3 **Freshness matters only for some queries.**
- Quote: "We have various 'query deserves freshness' systems designed to show fresher content for queries where it would be expected."
- Source: "A guide to Google Search ranking systems", https://developers.google.com/search/docs/appearance/ranking-systems-guide (last updated 2025-12-10).
- Trust: primary.
- Inference: price and availability pages and "latest research" articles need refresh. Evergreen explainers mostly need accuracy review, not date bumps.

6.4 **How often to re-audit.** Google gives no number. Trusted public practice:
- UK Ministry of Justice website guidance: "When you publish something on the website, add a note in your calendar to review the page again in 6 months or a year to check that the content is still needed and relevant." https://websitebuilder.service.justice.gov.uk/designing-your-site/creating-content/ (no date shown). Trust: primary (UK government).
- GOV.UK: "Monitor your content regularly to check if it's useful for users and they can find it." https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/plan-manage-content/manage-existing-govuk-content/ Trust: primary. No interval is given.
- NHS website (observed today on /conditions/high-blood-pressure/): "Page last reviewed: 19 July 2024 / Next review due: 19 July 2027". That is a **3-year medical review cycle**, shown on the page. Trust: primary observation of one page. That this is NHS policy for all pages is unverified.
- PIF TICK: "within appropriate timeframes" (1.9).
- Inference for the platform:
  - Automated technical audits weekly.
  - Content review every 6 to 12 months for commercial pages.
  - YMYL medical review at least every 12 to 36 months, with `lastReviewed` and a "next review due" date stored per item.
  - Re-audit at once when Search Console shows a sustained drop.

---

## 7. Editorial workflow and governance

7.1 **GOV.UK (Whitehall Publisher) workflow.**
- States: "draft, to 'submitted' to 'published'". When content is ready, "press 'submit' for a second person to review it" (2i).
- "An editor or managing editor can then edit, publish, schedule or reject it." Rejected items go back to draft.
- Force publish is allowed only with a written reason. Such documents "are flagged as 'not reviewed.'"
- Source: "How to publish on GOV.UK – Reviewing and publishing content", 22 June 2022 (archived copy): https://s3.amazonaws.com/thegovernmentsays-files/content/181/1818082.html. GOV.UK moved this guidance to https://guidance.publishing.service.gov.uk/ on 8 June 2026 (Inside GOV.UK blog: https://insidegovuk.blog.gov.uk/2026/06/08/launching-gov-uks-new-content-and-publishing-guidance/).
- Trust: primary (archived copy of a government page; the current text on the new site was not found, so the exact wording is unverified on the new site).

7.2 **Peer review (2i) checks.**
- The reviewer is another content designer, not the author.
- It covers "spelling and grammar", "tone", "structure", "that the content type is correct", whether "it meets a user need", that it "is not already on GOV.WALES", and "the style guide".
- It happens "before fact checking".
- Source: "Peer reviewing content (2i) for GOV.WALES", 27 Nov 2019. https://www.gov.wales/peer-reviewing-content-2i-govwales
- Trust: primary.
- Inference: this gives the order write → 2i (editorial) → fact or expert check → approve → publish. "Is not already on the site" is a cannibalisation check (section 8).

7.3 **Major and minor changes, and change notes (GOV.UK, current site).**
- No change note is needed if you only "fixed typos", "made style changes, like changing a heading or layout" or "updated or removed broken links".
- Write one if you "added new information that means a user has to do something differently", "removed guidance that is out of date or misleading", or "updated changes to fees or deadlines".
- "Do not say the page has been updated without saying what has changed."
- Source: "Write change notes", https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/change-notes/ (no date shown).
- Trust: primary.
- Inference: the same "major vs minor" flag can drive `dateModified`, the visible "Last updated" date and sitemap `lastmod` (sections 5 and 6.1). Only a major change bumps them.

7.4 **CMS norms (vendor or open source).**
- WordPress (last updated 13 Jan 2023), https://wordpress.org/documentation/article/post-status/:
  - Built-in statuses: publish, future (scheduled), draft, pending (awaiting a user with the `publish_posts` capability), private, trash, auto-draft and inherit (revisions).
  - Users who can edit but not publish see "Submit for Review" instead of "Publish".
- Drupal Content Moderation (page dated 18 Aug 2026), https://www.drupal.org/docs/8/core/modules/content-moderation/overview:
  - Default states: Draft, Published, Archived.
  - Transitions: Create New Draft, Publish, Archive, Restore to Draft, Restore.
  - Roles: an Author can create but not publish; an Editor reviews and publishes.
  - It keeps "a published version that is live, but have a separate working copy that is undergoing review."
- Trust: vendor / open-source docs.
- Inference, a suggested state set for our platform:
  - States: Suggested (engine) → Draft (human editing) → In review (2i) → Expert review (YMYL only) → Approved → Scheduled or Published (pushed to the CMS by a person) → Needs review (set by a scheduled audit or a review date) → Archived.
  - Keep every version, plus who changed it, when and why. A "major/minor" flag goes with each change.
  - Roles: Writer, Editor, Medical reviewer, Publisher, Admin.
  - Nobody approves their own work for YMYL items.

---

## 8. Keyword-to-URL mapping and cannibalisation

8.1 **Site diversity: usually at most two results per site.**
- Quote: "our site diversity system works so that we generally won't show more than two web page listings from the same site in our top results… However, we may still show more than two listings in cases where our systems determine it's especially relevant." Subdomains usually count as the same site.
- Source: ranking systems guide (last updated 2025-12-10).
- Trust: primary.

8.2 **Several pages ranking for one query is not a problem in itself. Near-duplicate pages compete with each other.**
- Source: Search Engine Journal, "Google Answers SEO Question About Keyword Cannibalization", 22 Sep 2025, quoting John Mueller on Bluesky. https://www.searchenginejournal.com/google-answers-seo-question-about-keyword-cannibalization/556472/
- Mueller quotes:
  - "If you have 3 different pages appearing in the same search result, that doesn't seem problematic to me just because it's 'more than 1'."
  - "Search Console shows data for when pages were actually shown, it's not a theoretical measurement."
- Older Mueller quote, as reported by secondary sites (unverified at the original): "If you have a bunch of pages with roughly the same content, it's going to compete with each other… I prefer fewer, stronger pages over lots of weaker ones."
- Trust: secondary (reporting a Googler).

8.3 **Deduplication.** Google shows "only the most relevant results to avoid unhelpful duplication" (already in research-evidence.md 7.2).
- Inference for extendmy.life: subcategory pages that repeat the parent H1 and share one meta description look like near-duplicates. Each needs its own intent, its own heading and its own clinic list.

8.4 **Site structure and topic clusters.**
- Link menus to categories, categories to subcategories, and subcategories to products. "The more links a page has to it within a site, the higher the relative importance of the page." Already in research-evidence.md 13.2.
- New from the same doc (last updated 2025-12-10): link best sellers from the homepage or from blog posts. "The ultimate ecommerce SEO best practice is to create useful and interesting content that is valuable to users."
- Trust: primary.
- "Topic cluster / pillar page" is an SEO-industry term. Google does not use it (secondary concept).
- Inference for the platform:
  - Keep one keyword-to-URL map per site and per language: each target phrase has one primary URL.
  - Flag a new draft whose main phrase is already mapped to another URL.
  - Use Search Console page+query data (actual shows) to find real overlap, not theoretical overlap.
  - Link articles to the clinic and category pages they discuss.

---

## 9. Measuring SEO changes (new items only)

9.1 **Compare ranges and wait weeks to months.**
- Google suggests "Last 16 months" for context. It also suggests "Compare last 3 months to previous period" or "Compare last 3 months year over year". Use Google Trends to check seasonality.
- Quote: "some changes can take effect in a few days, while others could take several months… it may take months before our systems determine that a site is now producing helpful content in the long term." / "wait a few weeks to analyze your site in Search Console again."
- Source: "Debugging drops in Google Search traffic", https://developers.google.com/search/docs/monitor-debug/debugging-search-traffic-drops (last updated 2025-12-10).
- Trust: primary.

9.2 **Weekly and monthly views (10 Dec 2025).** These smooth out day-of-week mismatches when you compare periods.
- Quote: "By switching to weekly or monthly granularity, the chart becomes much cleaner, allowing you to compare performance between two periods without getting distracted by day-of-the-week mismatches."
- Source: https://developers.google.com/search/blog/2025/12/weekly-monthly-views-search-console
- Trust: primary.

9.3 **Custom annotations (17 Nov 2025).** You can mark the date of a change on the Performance chart: up to 120 characters per note, and visible to everyone with access to the property.
- Examples Google gives: "updating a template", "Changing content to focus on different user intents".
- Source: https://developers.google.com/search/blog/2025/11/custom-chart-annotations
- Trust: primary.
- Unverified: whether an API exists to write annotations. None was found; the post describes only the UI.
- Inference: the platform should log its own change dates per URL and also tell users to add a GSC annotation.

9.4 **24-hour view (12 Dec 2024).** Data comes "with a delay of only a few hours". Points that are still incomplete show as a dotted line. Google says the average data delay was cut "by almost half".
- Source: https://developers.google.com/search/blog/2024/12/recent-data-search-console
- Trust: primary.
- Inference: for before/after comparisons, use only final data (`dataState=final`, already in research-evidence.md 9.1).

9.5 **Branded queries filter (Nov 2025).** It is AI-classified and works only for top-level (domain) properties with "sufficient volume". It "has no effect on how Google Search ranking works."
- Source: https://developers.google.com/search/blog/2025/11/search-console-branded-filter
- Trust: primary.
- Inference: for small sites such as MyPipit, the filter may not appear. Measure non-brand change with our own brand-term list.

9.6 **SEO split testing needs scale that our two sites do not have.**
- SearchPilot's rule of thumb is "1,000 organic site visits per day" to the section under test, on many pages with the same template. Source: "5 minimum requirements for running SEO tests", Will Critchlow, 15 Sep 2022 (updated 9 Apr 2024). https://www.searchpilot.com/resources/blog/before-you-begin-seo-testing
- Its newer model can run on "less than 10%" of the old 30,000 sessions/month minimum. Source: https://www.searchpilot.com/resources/blog/weve-doubled-the-sensitivity-of-our-seo-split-testing-platform (5 Aug 2019, updated 7 Aug 2023).
- Trust: vendor.
- Inference: with 17 to 53 pages (MyPipit) or about 237 per language (extendmy.life), real split tests are not practical. Use before/after with a control instead.

9.7 **Before/after with a control series: CausalImpact (peer-reviewed).**
- The method predicts the counterfactual from control time series (for example, untouched pages of the same type) using a Bayesian structural time-series model.
- Source: Brodersen, Gallusser, Koehler, Remy & Scott, "Inferring causal impact using Bayesian structural time-series models", Annals of Applied Statistics 9(1):247–274, March 2015. DOI 10.1214/14-AOAS788. https://projecteuclid.org/journals/annals-of-applied-statistics/volume-9/issue-1/Inferring-causal-impact-using-Bayesian-structural-time-series-models/10.1214/14-AOAS788.full
- Open-source package: https://google.github.io/CausalImpact/
- Trust: primary (peer-reviewed).
- Inference: this suits "we changed 10 clinic pages; compare them with 30 unchanged clinic pages". Results on very small samples will be weak, so report a range and not a single number.

---

## Items marked unverified

- 1.9: that PIF TICK requires review "every 3 years" (secondary claim; the criteria PDF says "appropriate timeframes").
- 1.10: whether HWG applies to a marketplace's clinic listings. This needs legal advice.
- 2.2: the June 2026 end of Search Console reporting and the August 2026 end of API support for FAQ (secondary sources).
- 6.4: whether NHS uses a 3-year review on all pages (one page observed).
- 7.1: the exact wording of the 2i workflow on the new guidance.publishing.service.gov.uk site (the archived 2022 copy was used).
- 8.2: the original source of the "fewer, stronger pages" Mueller quote.
- 9.3: whether there is an API to create Search Console annotations.
- Section 0: why the earlier review saw "no hreflang". The current HTML clearly has it.
