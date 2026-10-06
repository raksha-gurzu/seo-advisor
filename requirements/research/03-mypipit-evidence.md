# MyPipit SEO engine: research evidence

All sources checked on 2 October 2026. "Last updated" is the date shown on the source page.

Trust levels:
- **primary**: the organisation that owns the system (Google Search Central, Google Search Console Help, Chrome for Developers, schema.org, Meta for Developers), or a peer-reviewed paper.
- **vendor**: a tool maker describing its own product (Yoast, Rank Math).
- **secondary**: news, blogs, or travel agency sites.

Quotes in "double quotes" were checked against the raw page text. Anything marked **unverified** could not be confirmed from a primary source in this session.

---

## 1. Google title links (`<title>`)

1.1 **Finding:** Google writes the blue title link itself. The `<title>` element is only one of several sources it uses.
- Source: "Influencing your title links in search results", Google Search Central. https://developers.google.com/search/docs/appearance/title-link (last updated 2025-12-10)
- Quote (paraphrase of the list): Google uses the content of `<title>` elements, the main visual title on the page, heading elements such as `<h1>`, `og:title` meta tags, other large and prominent text, anchor text on the page, text in links that point to the page, and `WebSite` structured data.
- Checked: 2 October 2026. Trust: primary.

1.2 **Finding:** Write a descriptive, short title that is unique to each page. Do not use repeated boilerplate titles.
- Source: same page.
- Quote: "Write descriptive and concise text for your `<title>` elements." / "Avoid repeated or boilerplate text in `<title>` elements." / "Titling every page on a commerce site 'Cheap products for sale', for example, makes it impossible for users to distinguish between two pages."
- Checked: 2 October 2026. Trust: primary.

1.3 **Finding:** There is no length limit, but long titles get cut off. Avoid keyword stuffing.
- Source: same page.
- Quote: "While there's no limit on how long a `<title>` element can be, the title link is truncated in Google Search results as needed, typically to fit the device width." / "there's no reason to have the same words or phrases appear multiple times."
- Checked: 2 October 2026. Trust: primary.

1.4 **Finding:** Keep the brand short and use a separator. The home page is the place for a longer brand line. Repeating that line on every page "will look repetitive". A pattern like MyPipit's "listing title · pipit" is fine.
- Source: same page.
- Quote: "Brand your titles concisely." Google gives a hyphen, colon or pipe as example separators.
- Checked: 2 October 2026. Trust: primary.

1.5 **Finding:** Google rewrites titles that are half-empty, out of date, inaccurate, "micro-boilerplate" (the same title across a group of pages), or in a different language or script from the page.
- Source: same page, section "Common issues…".
- Paraphrase: Google may change the title link if "the page title doesn't reflect the page content".
- MyPipit relevance: the public title "Cross Thorong La, 5,416 m" does not name the trek ("Annapurna Circuit"), the length ("18 days") or "trek". Google may not show it as written, and it does not match how people search. This last point is our inference, not something Google says.
- Checked: 2 October 2026. Trust: primary (rule) and inference (MyPipit relevance).

## 2. Meta descriptions and snippets

2.1 **Finding:** Google builds snippets mostly from the page text. It uses the meta description only when it describes the page better.
- Source: "Control your snippets in search results", Google Search Central. https://developers.google.com/search/docs/appearance/snippet (last updated 2026-04-20)
- Quote: "Snippets are automatically created from page content." / "Google sometimes uses the meta description HTML element if it might give users a more accurate description of the page than content taken directly from the page."
- Checked: 2 October 2026. Trust: primary.

2.2 **Finding:** Each page needs its own description. On large database-driven sites, generating descriptions with code is "encouraged". There is no length limit, but the snippet is cut to fit the screen. Lists of keywords are less likely to be shown.
- Source: same page.
- Quote: "Identical or similar descriptions on every page of a site aren't helpful…" / "programmatic generation of the descriptions can be appropriate and are encouraged." / "There's no limit on how long a meta description can be, but the snippet is truncated in Google Search results as needed, typically to fit the device width." / "Meta descriptions comprised of long strings of keywords … are less likely to be displayed as a snippet."
- Checked: 2 October 2026. Trust: primary.

2.3 **Finding:** Meta descriptions do **not** affect ranking. They affect only the snippet, and so possibly the click rate.
- Source: "Google does not use the keywords meta tag in web ranking", Google Search Central Blog (Matt Cutts), September 2009. https://developers.google.com/search/blog/2009/09/google-does-not-use-keywords-meta-tag
- Quote: "Even though we sometimes use the description meta tag for the snippets we show, we still don't use the description meta tag in our ranking."
- Note: this is an old post. The current snippet page (2.1) does not discuss ranking. No newer primary statement says the opposite.
- Checked: 2 October 2026. Trust: primary (2009).

2.4 **Finding:** The SEO Starter Guide describes a good meta description.
- Source: "SEO Starter Guide", Google Search Central. https://developers.google.com/search/docs/fundamentals/seo-starter-guide (last updated 2025-12-10)
- Quote: "A good meta description is short, unique to one particular page, and includes the most relevant points of the page."
- Checked: 2 October 2026. Trust: primary.

## 3. Image SEO: alt text, stable URLs, image sitemaps, og:image

3.1 **Finding:** Alt text should describe the image in context. Do not stuff it with keywords.
- Source: "Image SEO best practices", Google Search Central. https://developers.google.com/search/docs/appearance/google-images (last updated 2026-03-02)
- Quote: "Avoid filling `alt` attributes with keywords (also known as keyword stuffing)…". The doc rates `alt="Dalmatian puppy playing fetch"` as best and empty or missing alt as bad.
- SEO Starter Guide: "Alt text is a short, but descriptive piece of text that explains the relationship between the image and your content." Also: place images "near text that's relevant to the image."
- MyPipit relevance: most photos have empty alt, so they lose this signal.
- Checked: 2 October 2026. Trust: primary.

3.2 **Finding:** Use **stable** image URLs. Google wants the same URL every time and warns against URLs that change on every page load.
- Source A: Image SEO best practices (above).
  - Quote: "consistently reference the image with the same URL, so that Google can cache and reuse the image without needing to request it multiple times."
- Source B: "Mobile-first indexing best practices", Google Search Central. https://developers.google.com/search/docs/crawling-indexing/mobile/mobile-sites-mobile-first-indexing (last updated 2025-12-10)
  - Quote: "Don't use URLs that change every time the page loads for images."
- Source C: "December 2023 Google SEO Office Hours" (John Mueller). https://developers.google.com/search/help/office-hours/2023/december
  - Quote: "images tend to be recrawled less-frequently, so changing image URLs is going to take a bit of time to be reprocessed across all of the search systems." He also recommends redirecting old image URLs to new ones.
- Checked: 2 October 2026. Trust: primary.
- **Inference (not stated by Google about presigned links):** MyPipit's presigned S3/R2 URLs change and stop working after 3600 seconds. Google may index an image URL that later returns an error. Because images are recrawled rarely, the indexed copy will often be dead. The likely result is weak or no presence in Google Images. No Google document names presigned or expiring URLs directly, so this specific effect is **unverified** but strongly implied by B and C.

3.3 **Finding:** Social previews (`og:image`) cache images by URL. An expiring URL can break link previews.
- Source: "Images in Link Shares", Meta for Developers. https://developers.facebook.com/docs/sharing/webmasters/images (no date shown)
- Quote: "We cache all images referenced based on each image's URL" / "Use a new URL for the new image or the image won't be updated" / "Don't remove old images, as there maybe existing stories that reference the old image" / the first share may show no image because "the crawler has to see an image at least once before it can be rendered". Recommended size: "at least 1200 x 630 pixels".
- Inference: if the presigned `og:image` URL has expired when Facebook, WhatsApp or LinkedIn crawls it, the preview has no image. That is **unverified** for each platform; only Meta's docs were checked.
- Google also says to choose an og:image that is "relevant and representative of the page" (Image SEO best practices).
- Checked: 2 October 2026. Trust: primary (Meta for its own crawler).

3.4 **Finding:** Image sitemaps help Google find images. Images may live on another domain such as a CDN, if both domains are verified in Search Console.
- Source: "Image sitemaps", Google Search Central. https://developers.google.com/search/docs/crawling-indexing/sitemaps/image-sitemaps (last updated 2025-12-10)
- Quote: "Each `<url>` tag can contain up to 1,000 `<image:image>` tags." / "the image URL may not be on the same domain as your main site. This is fine, as long as you verify both domains in Search Console." Google has removed `<image:caption>`, `<image:title>`, `<image:geo_location>` and `<image:license>` from its docs.
- Image SEO page: "Google doesn't index CSS images". Use `<img src>`, and always give a `src` fallback when using `srcset` or `<picture>`.
- Checked: 2 October 2026. Trust: primary.

3.5 **Finding:** Use short, descriptive filenames.
- Source: Image SEO best practices.
- Quote: "`my-new-black-kitten.jpg` is better than `IMG00023.JPG`".
- Checked: 2 October 2026. Trust: primary.

## 4. robots.txt

4.1 **Finding:** A robots.txt that returns 404 (or any 4xx except 429) is treated as "no rules". Google crawls everything. MyPipit's missing robots.txt does not block crawling.
- Source: "How Google interprets the robots.txt specification", Google Search Central. https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt (last updated 2026-08-31)
- Quote: "Google's crawlers treat all `4xx` errors, except `429`, as if a valid robots.txt file didn't exist. This means that Google assumes that there are no crawl restrictions."
- A **5xx** error is different. Google stops crawling the site for 12 hours, then uses the last good copy for up to 30 days. Google caches robots.txt "for up to 24 hours".
- Checked: 2 October 2026. Trust: primary.

4.2 **Finding:** A `Sitemap:` line in robots.txt is one of three ways to tell Google about a sitemap. It must be a full URL.
- Source: same page.
- Quote: "It must be a fully qualified URL, including the protocol and host…"
- Source: "Build and submit a sitemap", Google Search Central. https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap (last updated 2026-07-08)
  - Submission routes: Search Console Sitemaps report, the Search Console API, or a robots.txt `Sitemap:` line.
  - Quote: "Google ignores `<priority>` and `<changefreq>` values." / "Google uses the `<lastmod>` value if it's consistently and verifiably … accurate." / "Submitting a sitemap is merely a hint…". Limit: 50,000 URLs or 50 MB per sitemap.
- Checked: 2 October 2026. Trust: primary.

## 5. Structured data for travel listings

5.1 **Finding:** Google's rich result gallery has **no** feature for TouristTrip, Trip, Tour, Hotel or LodgingBusiness. The travel-related features are "Vacation rental" (restricted, see 5.6) and "Local business".
- Source: "Structured data markup that Google Search supports", Google Search Central. https://developers.google.com/search/docs/appearance/structured-data/search-gallery (last updated 2026-06-15)
- Features listed: Article, Breadcrumb, Carousel, Course list, Dataset, Discussion forum, Education Q&A, Employer aggregate rating, Event, Image metadata, Job posting, Local business, Math solver, Movie, Organization, Product, Profile page, Q&A, Recipe, Review snippet, Software app, Speakable, Subscription/paywalled content, Vacation rental, Video.
- Checked: 2 October 2026. Trust: primary.

5.2 **Finding:** schema.org TouristTrip exists but is still in the "new" (pending) area. It sits under Thing > Intangible > Trip > TouristTrip and has `itinerary`, `offers`, `provider`, `subTrip`, `touristType` and other properties. It is valid vocabulary and may help machines understand the page, but it earns **no Google rich result**.
- Source: schema.org/TouristTrip. https://schema.org/TouristTrip
- Quote: "This term is in the 'new' area - implementation feedback and adoption from applications and websites can help improve our definitions." / "A tourist trip. A created itinerary of visits to one or more places of interest…"
- Trip: "A trip or journey. An itinerary of visits to one or more places." https://schema.org/Trip
- LodgingBusiness: "A lodging business, such as a motel, hotel, or inn." It is a subtype of LocalBusiness. https://schema.org/LodgingBusiness
- Checked: 2 October 2026. Trust: primary.

5.3 **Finding (product snippets):** A product snippet needs `name` plus at least one of `review`, `aggregateRating` or `offers`. MyPipit's Product JSON-LD has none of these, so it **cannot** produce a product rich result today.
- Source: "Product snippet (Product, Review, Offer) structured data", Google Search Central. https://developers.google.com/search/docs/appearance/structured-data/product-snippet (last updated 2026-09-08)
- Quote: "Product snippets require either review or aggregateRating or offers" / "product rich results only support pages that focus on a single product" / "We recommend focusing on adding markup to product pages instead of pages that list products or a category of products."
- Overview page: product snippets are "For product pages where people can't directly purchase the product". Merchant listings are "For pages where customers can purchase products from you." https://developers.google.com/search/docs/appearance/structured-data/product (last updated 2025-12-10)
- Checked: 2 October 2026. Trust: primary.

5.4 **Finding (merchant listings):** Only pages where the visitor can actually buy are eligible. The price must be above zero. Merchant listings are tied to Google Shopping, which **does not allow services or future travel tickets**. A trek package is a service, so it is unlikely to qualify for merchant listings or Shopping.
- Source: "Merchant listing (Product, Offer) structured data", Google Search Central. https://developers.google.com/search/docs/appearance/structured-data/merchant-listing (last updated 2026-09-08)
  - Quote: "Only pages where a shopper can purchase a product are eligible for merchant listing experiences, not pages with links to other sites that sell the product." / "Unlike product snippets, merchant listing experiences require a price greater than zero."
- Source: "Unsupported Shopping content", Google Merchant Center Help. https://support.google.com/merchants/answer/6150006
  - Quote: "Future transport or event tickets are not allowed" / "Labor, time, effort, expertise, or actions, which do not result in ownership of a tangible product are not allowed."
- Note: schema.org defines Product as "Any offered product or service", so marking a tour as Product is valid vocabulary. Google's product docs do not say whether tours qualify for **product snippets**, so that is **unverified**. Test with the Rich Results Test before relying on it.
- Checked: 2 October 2026. Trust: primary.

5.5 **Finding (reviews and ratings):** Star ratings must come from reviews shown on the page. Do not copy them from other sites. Self-serving reviews on LocalBusiness or Organization pages are not eligible.
- Source: "Review snippet structured data", Google Search Central. https://developers.google.com/search/docs/appearance/structured-data/review-snippet (last updated 2026-09-08)
- Quote: "Don't aggregate reviews or ratings from other websites." / "If the entity that's being reviewed controls the reviews about itself, their pages that use LocalBusiness or any other type of Organization structured data are ineligible for star review feature."
- Supported review targets include Book, Course, Event, Local business, Movie, Product, Recipe, Software App, Organization and others. Trips are not on the list.
- Structured data general guidelines: "Don't mark up content that is not visible to readers of the page." Google does not guarantee rich results even with correct markup. https://developers.google.com/search/docs/appearance/structured-data/sd-policies (last updated 2026-07-10)
- Checked: 2 October 2026. Trust: primary.

5.6 **Finding (vacation rental):** Vacation rental structured data is closed to most sites. It needs a Google Technical Account Manager and Hotel Center access, and it is an early-adopter programme.
- Source: "Vacation rental (VacationRental) structured data", Google Search Central. https://developers.google.com/search/docs/appearance/structured-data/vacation-rental (last updated 2026-09-08)
- Quote: "These instructions are intended for sites that have already connected with a Google Technical Account Manager and have access to the Hotel Center." / "Filling out the form is an expression of interest and doesn't guarantee an invitation into the Early Adopters Program. This feature is limited to sites that meet certain eligibility criteria…"
- Required properties include `containsPlace`, `occupancy`, `identifier`, `image` (at least 8 photos), `latitude` and `longitude` (at least 5 decimals), and `name`.
- Checked: 2 October 2026. Trust: primary.

5.7 **Finding (hotels):** Hotel prices and free booking links on Google come through **Hotel Center** feeds, not through page markup. Structured data there is used only to check price accuracy.
- Source: "About hotel free booking links", Hotel Center Help. https://support.google.com/hotelprices/answer/10472393 (no date)
- Quote: "Any property with a bid in a hotel campaign, available rates, and a landing page will be eligible." There is a separate starter guide for newcomers.
- Checked: 2 October 2026. Trust: primary.

5.8 **Finding (tours and activities):** Google has a separate partner feed programme for tours and activities, called **Things to do**, run through the Actions Center. It needs an interest form, a content licence agreement and a JSON feed sent over SFTP. Treks and tours reach Google's tour surfaces through this feed, not through markup.
- Source: "Things to do: Overview and eligibility", Google Actions Center. https://developers.google.com/actions-center/verticals/things-to-do/overview (last updated 2026-04-01)
- Paraphrase: eligible partners are attractions, tour operators and activity providers (through connectivity partners), online travel agencies, reservation technology companies, and direct integrators. Partners complete an interest form and sign a content licence agreement. Feeds must be uploaded at least every 30 days (seen in search summary).
- **Unverified:** whether multi-day treks count as eligible products.
- Checked: 2 October 2026. Trust: primary.

5.9 **Finding (Organization):** Organization markup has no required properties. Put it on the home page or about page, not on every page. Use the most specific subtype.
- Source: "Organization structured data", Google Search Central. https://developers.google.com/search/docs/appearance/structured-data/organization (last updated 2026-09-08)
- Quote: "We recommend placing this information on your home page, or a single page that describes your organization… You don't need to include it on every page of your site." / "There are no required properties".
- Checked: 2 October 2026. Trust: primary.

5.10 **Finding (Breadcrumb):** BreadcrumbList needs `itemListElement`. Each ListItem needs `position` and `name`, and `item` (the URL) on every crumb except the last. Google says the feature "is available on desktop" in all regions.
- Source: "Breadcrumb structured data", Google Search Central. https://developers.google.com/search/docs/appearance/structured-data/breadcrumb (last updated 2026-09-08)
- Checked: 2 October 2026. Trust: primary.

5.11 **Finding (Article / BlogPosting):** Article, NewsArticle and BlogPosting have no required properties. Recommended properties are `author`, `datePublished`, `dateModified`, `headline` and `image`. Images must be crawlable and indexable, at least 50K pixels (width x height), in 16x9, 4x3 and 1x1 ratios. This matters for MyPipit's 36 blog posts and their expiring images.
- Source: "Article structured data", Google Search Central. https://developers.google.com/search/docs/appearance/structured-data/article (last updated 2026-09-08)
- Checked: 2 October 2026. Trust: primary.

## 6. Helpful content and AI-generated content

6.1 **Finding:** Using AI to write content is allowed. Mass-producing pages "without adding value" is spam. Every AI output must be fact-checked by a person, and that includes titles, meta descriptions, structured data and alt text.
- Source: "Google Search's guidance on using generative AI content on your website", Google Search Central. https://developers.google.com/search/docs/fundamentals/using-gen-ai-content (last updated 2026-10-01)
- Quote: "Generative AI can be particularly useful when researching a topic, and to add structure to original content. However, using generative AI tools or other similar tools to generate many pages without adding value for users may violate Google's spam policy on scaled content abuse." / "It is critical to manually factcheck and review all AI-generated content for accuracy and trustworthiness before publishing. This review also applies to metadata like `<title>` elements, meta description elements, structured data, and alternate texts for images…"
- E-commerce note: the "labelled as AI-generated" rule applies to **Google Merchant Center** product data and images (IPTC `TrainedAlgorithmicMedia`), not to normal web pages. Quote: "AI-generated product data such as title and description attributes must be specified separately and labeled as AI-generated."
- Checked: 2 October 2026. Trust: primary.

6.2 **Finding:** Google rewards quality "however it is produced". Automation that is used to manipulate ranking is spam.
- Source: "Google Search's guidance about AI-generated content", Google Search Central Blog, February 2023. https://developers.google.com/search/blog/2023/02/google-search-and-ai-content
- Quote: "Google rewards high-quality content, however it is produced" / "Appropriate use of AI or automation is not against our guidelines." It also suggests showing readers Who, How and Why the content was made.
- Checked: 2 October 2026. Trust: primary.

6.3 **Finding (scaled content abuse):** Generating many pages with AI, scraping, automated rewording or translation, or stitching content together without adding value all count as spam.
- Source: "Spam policies for Google web search", Google Search Central. https://developers.google.com/search/docs/essentials/spam-policies (last updated 2026-08-28)
- Quote: "Scaled content abuse is when many pages are generated for the primary purpose of manipulating search rankings and not helping users." Examples: "Using generative AI tools or other similar tools to generate many pages without adding value for users"; "Scraping feeds … (including through automated transformations like synonymizing, translating, or other obfuscation techniques)"; "Stitching or combining content from different web pages without adding value."
- The same page covers doorway abuse ("pages … created to rank for specific, similar search queries") and keyword stuffing.
- Checked: 2 October 2026. Trust: primary.

6.4 **Finding (people-first):** Google's self-check asks whether the content has original information and whether it is mass-produced or heavily automated. It says Google has **no preferred word count**.
- Source: "Creating helpful, reliable, people-first content", Google Search Central. https://developers.google.com/search/docs/fundamentals/creating-helpful-content (last updated 2026-10-01)
- Quote: "Does the content provide original information, reporting, research, or analysis?" / "Are you using extensive automation to produce content on many topics?" / "Are you writing to a particular word count because you've heard or read that Google has a preferred word count? (No, we don't.)"
- SEO Starter Guide: "The length of the content alone doesn't matter for ranking purposes (there's no magical word count target)." It also says E-E-A-T is not itself a ranking factor ("No, it's not.").
- Checked: 2 October 2026. Trust: primary.

6.5 **Finding (AI answer engines):** Google says no extra tricks are needed for AI Overviews or AI Mode. Write non-commodity content. Google ignores llms.txt and "chunking". Search Console has a Generative AI performance report.
- Source: "Optimizing for generative AI features on Google Search", Google Search Central. https://developers.google.com/search/docs/fundamentals/ai-optimization-guide (last updated 2026-07-10)
- Quote: "Don't just recycle what others on the internet have already said, or could easily be produced by a generative AI model." / about LLMS.txt: "Doing so will neither harm nor help your site's visibility or rankings in Google Search, as Google Search ignores them." / "There's no requirement to break your content into tiny pieces for AI to better understand it."
- Report launch: "Introducing Search Generative AI performance reports in Search Console", Google Search Central Blog, June 2026. https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports
- Checked: 2 October 2026. Trust: primary.

6.6 **What this means for auto-writing listing descriptions (inference):**
- AI drafts are allowed only if a person reviews them and they add real information from the agency, such as the actual itinerary, inclusions, guide details or permits.
- Writing hundreds of near-identical "Annapurna trek" pages from a template, or translating them automatically, matches the scaled content abuse examples.
- Metadata written by AI must also be reviewed.
- This supports the engine's existing "[ADD: …] placeholder, never invent facts" rule.

## 7. Duplicates, canonicals, thin pages and site quality

7.1 **Finding:** Duplicate content is not spam. Google picks one canonical URL from a set of duplicate or very similar pages. `rel=canonical` and redirects are strong signals; a sitemap is a weak signal.
- Source: "What is URL canonicalization", Google Search Central. https://developers.google.com/search/docs/crawling-indexing/canonicalization (last updated 2026-08-20)
- Quote: "A canonical URL is the URL of a page that Google chose as the most representative from a set of duplicate pages." / "Some duplicate content on a site is normal and it's not a violation of Google's spam policies."
- Source: "How to specify a canonical URL…", Google Search Central. https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls (last updated 2026-07-10)
- Quote: redirects are "A strong signal…", `rel="canonical"` is "A strong signal…", and sitemap inclusion is "A weak signal…". Also: "We don't recommend using noindex to prevent selection of a canonical page within a single site, because it will completely block the page from Search."
- SEO Starter Guide: duplicates are "not a violation of our spam policies, but it can be a bad user experience and search engines might waste crawling resources."
- Checked: 2 October 2026. Trust: primary.

7.2 **Finding:** When many pages are very similar, Google shows only the most relevant one (deduplication).
- Source: "A guide to Google Search ranking systems", Google Search Central. https://developers.google.com/search/docs/appearance/ranking-systems-guide (last updated 2025-12-10)
- Quote: "Some of these may be very similar to each other. In such cases, our systems show only the most relevant results to avoid unhelpful duplication."
- Inference: if several agencies list the same trek with near-identical text, only one will usually rank. Each listing needs its own facts (dates, inclusions, group size, guide, price) to be worth showing.
- Checked: 2 October 2026. Trust: primary (rule), inference (MyPipit).

7.3 **Finding:** Quality is judged per page, but site-wide signals also count. Weak sections can drag the site down. Google says deleting content is a last resort and that improving it comes first.
- Source: ranking systems guide (above).
  - Quote: "Our ranking systems are designed to work on the page level… Site-wide signals and classifiers are also used and contribute to our understanding of pages." The helpful content system "became part of our core ranking systems" in March 2024.
- Source: "Google Search's core updates and your website", Google Search Central. https://developers.google.com/search/docs/appearance/core-updates (last updated 2025-12-10)
  - Quote: "Deleting content is a last resort, and only to be considered if you think the content can't be salvaged… If that's the case for your site, then deleting the unhelpful content can help the good content on your site perform better."
- Checked: 2 October 2026. Trust: primary.

7.4 **Finding (noindex):** `noindex` removes a page from Google. Google must be able to crawl the page to see the tag, so do not also block it in robots.txt.
- Source: "Block Search indexing with noindex", Google Search Central. https://developers.google.com/search/docs/crawling-indexing/block-indexing (last updated 2025-12-10)
- Quote: "Google will drop that page entirely from Google Search results…" / "For the noindex rule to be effective, the page or resource must not be blocked by a robots.txt file…"
- Inference for thin listings, such as a single meal or a visa-assistance service: either add real detail, merge them into a fuller page, or use `noindex` while keeping them reachable for users. Google has no rule that names "thin listings". This is a judgment based on 7.3 and 6.4.
- Checked: 2 October 2026. Trust: primary (rule), inference (MyPipit).

## 8. URL slugs

8.1 **Finding:** Use readable words, use hyphens, and use the audience's language. Avoid long ID numbers and needless parameters. Google gives **no length limit**.
- Source: "URL structure best practices for Google Search", Google Search Central. https://developers.google.com/search/docs/crawling-indexing/url-structure (last updated 2025-12-10)
- Quote: "When possible, use readable words rather than long ID numbers in your URLs." / "we recommend using hyphens (-) instead of underscores (_)" / "Use words in your audience's language in the URL (and, if applicable, transliterated words)." / "Overly complex URLs, especially those containing multiple parameters, can cause problems for crawlers…"
- Checked: 2 October 2026. Trust: primary.

8.2 **Finding:** Keywords in the URL have "hardly any effect" on ranking. A very long slug is not a ranking problem in Google's own words. Shorter slugs are simply easier for people to read.
- Source: SEO Starter Guide. https://developers.google.com/search/docs/fundamentals/seo-starter-guide (last updated 2025-12-10)
- Quote: "From a ranking perspective, the keywords in the name of the domain (or URL path) alone have hardly any effect beyond appearing in breadcrumbs." / "Using directories (or folders) to group similar topics can help Google learn how often the URLs in individual directories change."
- Vendor contrast: Rank Math's own test passes URLs of 75 characters or fewer (see 11.3). That is a vendor rule of thumb, not Google's.
- Practical note (inference): changing the slug of a live page needs a 301 redirect from the old URL, according to Google's site-move docs (not fetched in detail).
- Checked: 2 October 2026. Trust: primary.

## 9. Search Console API and data access

9.1 **Finding (Search Analytics query):**
- Dimensions: `country`, `device`, `page`, `query`, `searchAppearance`, `date`, `hour`.
- `rowLimit` is 1 to 25,000 (default 1,000), with paging through `startRow`.
- `type`: web, image, video, news, discover, googleNews.
- `dataState`: final, all, or hourly_all.
- `aggregationType`: auto, byPage, byProperty.
- The API returns only the "top" rows, not every row.
- Source: "Search Analytics: query", Google for Developers. https://developers.google.com/webmaster-tools/v1/searchanalytics/query (last updated 2026-08-11)
- Quote: "The API is bounded by internal limitations of Search Console and does not guarantee to return all data rows but rather top ones."
- Checked: 2 October 2026. Trust: primary.

9.2 **Finding:** You can get at most 50K rows per day per search type. Data usually arrives after 2 to 3 days. To get accurate totals, leave out the page and query dimensions.
- Source: "Getting all your data", Google for Developers. https://developers.google.com/webmaster-tools/v1/how-tos/all-your-data (last updated 2025-08-28)
- Quote: "the Search Analytics method exposes a maximum of 50K rows of data per day per search type (web, image, and so on--sorted by clicks)." / "Data is typically available after 2-3 days".
- Checked: 2 October 2026. Trust: primary.

9.3 **Finding:** Rare queries are hidden ("anonymized"). On a small site like MyPipit, many queries may be hidden.
- Source: "A deep dive into Search Console performance data filtering and limits", Google Search Central Blog, October 2022. https://developers.google.com/search/blog/2022/10/performance-data-deep-dive
- Quote: "Anonymized queries are those that aren't issued by more than a few dozen users over a two-to-three month period." / "While the actual anonymized queries are always omitted from the tables, they are included in chart totals, unless you filter by query."
- Checked: 2 October 2026. Trust: primary.

9.4 **Finding (retention):** The Performance report keeps 16 months of data. A scheduled job should store its own copy to keep longer history.
- Source: "Introducing the new Search Console", Google Search Central Blog, January 2018. https://developers.google.com/search/blog/2018/01/introducing-new-search-console
- Quote: "With the new report, you'll have 16 months of data…"
- Checked: 2 October 2026. Trust: primary (2018, still repeated in current help pages per search results).

9.5 **Finding (quotas):**
- Search Analytics: 1,200 queries per minute per site, 1,200 per minute per user, and 40,000 per minute or 30,000,000 per day per project. There is also a "load" quota; heavy page and query groupings cost more.
- URL Inspection API: **2,000 per day and 600 per minute per site**.
- Source: "Usage limits", Google for Developers. https://developers.google.com/webmaster-tools/limits (last updated 2025-08-28)
- Checked: 2 October 2026. Trust: primary.

9.6 **Finding (URL Inspection API):** It reports the status of the version in Google's index. It does not run a live test.
- Source: "urlInspection.index.inspect", Google for Developers. https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect (last updated 2024-07-23)
- Quote: "View the indexed, or indexable, status of the provided URL. Presently only the status of the version in the Google index is available."
- Scopes: `webmasters` or `webmasters.readonly`.
- With about 58 URLs, MyPipit could inspect every page daily within the quota (inference).
- Checked: 2 October 2026. Trust: primary.

9.7 **Finding (bulk data export):** Bulk data export sends a daily dump to BigQuery. It has no row limit but excludes anonymized queries. It needs a Google Cloud project with billing. It starts from setup and does not fill in older data; use the API for history.
- Source: "About bulk data export of Search Console data to BigQuery", Search Console Help. https://support.google.com/webmasters/answer/12918484
  - Quote: "Schedule a daily export of your Search Console performance data to BigQuery… with the exception of anonymized queries."
- Source: "Start a new bulk data export", Search Console Help. https://support.google.com/webmasters/answer/12917675
  - Quote: "You must set up a Google Cloud project with billing and enable BigQuery" / "The first export will happen up to 48 hours after your successful configuration" / "If you want to see historical data that precedes your initial setup, use the Search Console API or the reports."
- Source: "Bulk data export: a new and powerful way…", Search Central Blog, February 2023. https://developers.google.com/search/blog/2023/02/bulk-data-export
  - Quote: "the bulk data export is not affected by the daily data row limit."
- Cost: BigQuery storage and queries are charged above a free tier.
- For a 58-URL site, bulk export is overkill; the API is enough (inference).
- Checked: 2 October 2026. Trust: primary.

9.8 **Finding (properties and verification):** A **Domain property** (for example `mypipit.com`) covers every subdomain, including marketplace., agency. and www, and both http and https. It must be verified with a DNS record. A URL-prefix property covers one prefix and can be verified with an HTML file, meta tag, Google Analytics or Tag Manager. The verification token must stay in place.
- Source: "Add a website property to Search Console", Search Console Help. https://support.google.com/webmasters/answer/34592
  - Quote: a Domain property "Includes all subdomains (m, www, and so on) and multiple protocols"; verification is by "DNS record verification only".
- Source: "Verify your site ownership", Search Console Help. https://support.google.com/webmasters/answer/9008080
  - Quote: "To stay verified, don't remove the DNS record from your provider, even after verification succeeds."
- **Unverified in this session:** the exact steps to give a service account access. The usual method is to add the service account's email as a user on the property.
- Checked: 2 October 2026. Trust: primary.

## 10. Chrome extensions (Manifest V3): can scheduled audits live there?

10.1 **Finding (alarms):**
- The shortest alarm interval is 30 seconds.
- Alarms do not wake a sleeping device; missed alarms fire when it wakes.
- From Chrome 150, `persistAcrossSessions` controls whether an alarm survives a browser restart. It defaults to true in Chrome. Before Chrome 150, behaviour "can be unpredictable".
- Google advises re-creating important alarms every time the service worker starts.
- Source: "chrome.alarms", Chrome for Developers. https://developer.chrome.com/docs/extensions/reference/api/alarms (last updated 2026-09-11)
- Quote: "Chrome limits alarms to at most once every 30 seconds but may delay them an arbitrary amount more." / "Alarms continue to run while a device is sleeping. However, an alarm will not wake up a device. When the device wakes up, any missed alarms will fire." / "persistAcrossSessions … true (persists until the extension updates) or false (cleared if the extension is reloaded or the browser restarts…)" / "it is best to make sure important alarms exists each time your service worker starts up."
- Checked: 2 October 2026. Trust: primary.

10.2 **Finding (service worker limits):** Chrome stops the extension's service worker after 30 seconds of inactivity, after 5 minutes on a single event or API call, or if a `fetch()` takes more than 30 seconds to respond. `setTimeout` and `setInterval` timers are cancelled when the worker stops, so alarms must be used.
- Source: "The extension service worker lifecycle", Chrome for Developers. https://developer.chrome.com/docs/extensions/develop/concepts/service-workers/lifecycle (last updated 2023-05-02)
- Quote: "After 30 seconds of inactivity…" / "When a single request, such as an event or API call, takes longer than 5 minutes to process." / "When a fetch() response takes more than 30 seconds to arrive."
- Source: "Migrate to a service worker", Chrome for Developers. https://developer.chrome.com/docs/extensions/develop/migrate/to-service-workers (last updated 2023-03-09)
  - Quote: "the timers are canceled whenever the service worker is terminated."
- Checked: 2 October 2026. Trust: primary.

10.3 **Finding (browser must be running):** An extension runs only inside a running Chrome profile on one person's machine. If Chrome is closed or the laptop is off, no audit runs. It catches up only when Chrome next starts.
- This is **inference**. No Chrome doc found says "alarms do not fire while Chrome is closed" in those words. It follows from 10.1 (alarms do not wake a device; missed alarms fire later) and from the extension living inside the browser. **Unverified as a direct quote.**
- **Conclusion (inference):** daily, weekly and monthly audits that must run reliably belong on a **server**, for example a cron job or scheduled worker in the existing FastAPI app. An extension fits on-demand, in-editor checks.

10.4 **Finding (content scripts):** Content scripts can read and change the DOM of pages the extension can access. They run in an "isolated world". Injecting them needs host permissions or `activeTab`. They can call only a few extension APIs and must message the service worker for anything else.
- Source: "Content scripts", Chrome for Developers. https://developer.chrome.com/docs/extensions/develop/concepts/content-scripts
- Quote: content scripts can "read details of the web pages the browser visits, make changes to them, and pass information to their parent extension".
- MyPipit relevance (inference): this works for reading the Lexxy editor on agency.mypipit.com and inserting suggestions there.
- Checked: 2 October 2026. Trust: primary.

10.5 **Finding (permissions):** In MV3, `host_permissions` holds site match patterns, and adding or changing them triggers a warning to the user. `optional_host_permissions` can be granted at runtime.
- Source: "Declare permissions", Chrome for Developers. https://developer.chrome.com/docs/extensions/develop/concepts/declare-permissions (last updated 2024-02-05)
- Quote: "Adding or changing match patterns in the "host_permissions" and "content_scripts.matches" fields of the manifest file will also trigger a warning."
- Checked: 2 October 2026. Trust: primary.

10.6 **Finding (publishing an internal tool):**
- Visibility options are Public, Unlisted (anyone with the link), and Private (trusted testers, Google Groups, or a Google Workspace domain).
- **All visibility options go through the same review.**
- Domain-published items appear only in the organisation's private store. Admins can force-install them, and users cannot remove force-installed extensions.
- Self-hosting (outside the Chrome Web Store) works on Windows and macOS only through enterprise policy.
- Sources:
  - "Prepare to publish: set up distribution", Chrome for Developers. https://developer.chrome.com/docs/webstore/cws-dashboard-distribution (last updated 2020-12-07). Quote: "All visibility settings have the same policy requirements and will go through the same review process."
  - "Enterprise publishing options", Chrome for Developers. https://developer.chrome.com/docs/webstore/cws-enterprise (last updated 2021-07-29). Quote: "Users can't remove extensions that are force installed."
  - "Distribute your extension", Chrome for Developers. https://developer.chrome.com/docs/extensions/how-to/distribute (last updated 2023-12-12). Quote: "Windows and macOS users can only install self-hosted extensions through enterprise policies."
- Checked: 2 October 2026. Trust: primary.

10.7 **Finding (Chrome Web Store policies):** An extension must have a single, narrow purpose and request only the narrowest permissions. MV3 bans remotely hosted code, so the AI or audit logic must run on our server and be called as an API, not loaded as remote script.
- Source: "Chrome Web Store program policies", Chrome for Developers. https://developer.chrome.com/docs/webstore/program-policies/policies (last updated 2025-05-22)
- Quote: "An extension must have a single purpose that is narrow and easy to understand." / "Request access to the narrowest permissions necessary…" / "The full functionality of an extension must be easily discernible from its submitted code."
- Checked: 2 October 2026. Trust: primary.

## 11. How in-editor SEO checkers work (vendor docs)

11.1 **Finding (Yoast SEO analysis):** Yoast checks:
- Keyphrase: in the introduction, length, density, in the meta description, in subheadings, in link text, in image alt, in the title and in the slug.
- Previously used keyphrase, keyphrase distribution (Premium), text length.
- Outbound and internal links, SEO title width, meta description length, stale cornerstone content (Premium).
- Source: "Yoast SEO Analysis", Yoast. https://yoast.com/features/seo-analysis/
- Quote examples: "Keyphrase in introduction - Checks whether words from the keyphrase can be found in the first paragraph." / "Keyphrase in slug - Checks if the keyphrase is used in the URL." / "Internal links - Checks if internal links are present and followed."
- Checked: 2 October 2026. Trust: vendor.

11.2 **Finding (Yoast thresholds and readability):**
- Meta description length: green between **120 and 156 characters**.
- Keyphrase density: green between **0.5% and 3%** (3.5% in Premium), checked only on texts of 100 words or more.
- Readability checks: subheading distribution, paragraph length, sentence length, consecutive sentences, passive voice (threshold 10% of sentences), transition words, word complexity (Premium), Flesch reading ease (English only).
- Sources:
  - Yoast. https://yoast.com/meta-description-length/
  - Yoast. https://yoast.com/what-is-keyphrase-density-and-why-is-it-important/
  - Yoast. https://yoast.com/features/readability-analysis/
- Thresholds come from search result summaries of these pages. The passive voice figure was seen on the readability page.
- Checked: 2 October 2026. Trust: vendor.
- Note: these numbers are Yoast's own rules of thumb. Google publishes no density or length targets (see 2.2, 6.4).

11.3 **Finding (Rank Math tests):**
- Basic: focus keyword in the SEO title (within the first 50 characters), in the meta description, in the URL, in the first 10% of the content, and in the content.
- Content length bands: 2,500+ words = 100%, down to under 600 words = 0%.
- Additional: keyword in subheadings, keyword in image alt, keyword density 1 to 1.5%, URL of 75 characters or fewer, external links (with at least one followed), internal links, focus keyword not used on other posts.
- Title readability: keyword near the start, sentiment, power words, a number in the title.
- Content readability: table of contents, paragraphs no longer than 120 words, at least 4 media items.
- Source: "Score 100/100 With Rank Math Post Tests", Rank Math. https://rankmath.com/kb/score-100-in-tests/ (no date shown)
- Checked: 2 October 2026. Trust: vendor.
- Note: the word-count bands **conflict with Google's** "no magical word count target" (6.4). We should not copy them.

11.4 **Finding (Rank Math Content AI):** Content AI takes a focus keyword, analyses search results on Rank Math's servers, and suggests word count, headings, links, media count, related keywords and questions. It uses a monthly credit system and has 40+ AI writing tools.
- Source: "How to Use Rank Math's Content AI", Rank Math. https://rankmath.com/kb/how-to-use-content-ai/
- Quote: "Our server collects the data from various sources using proprietary algorithms and uses our own AI to offer more relevant suggestions."
- Checked: 2 October 2026. Trust: vendor.

## 12. Travel and tourism keyword evidence (Nepal treks)

12.1 **Finding:** Google Trends data has a public API in **alpha** with limited access by application. It returns consistently scaled search interest (not absolute volumes) for the last 5 years, by day, week, month or year, with country and sub-region filters. It is useful for seasonality checks such as "Annapurna Circuit trek" by month.
- Sources:
  - "Introducing the Google Trends API (alpha)", Google Search Central Blog, July 2025. https://developers.google.com/search/blog/2025/07/trends-api
  - "Google Trends API Alpha", Google. https://developers.google.com/search/apis/trends
- Quote: "The Google Trends API provides access to a rolling window of the last 5 years of data".
- Status on 2 October 2026: still alpha; apply through a form.
- Checked: 2 October 2026. Trust: primary.

12.2 **Finding (peer-reviewed):** Search data improves tourism demand forecasts, so search interest is a usable signal for seasonality.
- Source: Bangwayo-Skeete, P.F. & Skeete, R.W. (2015). "Can Google data improve the forecasting performance of tourist arrivals? Mixed-data sampling approach." *Tourism Management* 46, 454–464. DOI 10.1016/j.tourman.2014.07.014
- Paraphrase: models using weekly Google data forecast Caribbean tourist arrivals better than models without it.
- Related: Önder, I. (2017), "Forecasting tourism demand with Google Trends: accuracy comparison of countries versus cities", *International Journal of Tourism Research* (title seen in search; not read).
- Checked: 2 October 2026. Trust: primary (peer-reviewed). Details come from the abstract or summary only.

12.3 **Finding (peer-reviewed):** Social media and review sites take a large share of travel search results, so a listing page competes with forums and review sites, not only with agencies.
- Source: Xiang, Z. & Gretzel, U. (2010). "Role of social media in online travel information search." *Tourism Management* 31(2), 179–188. DOI 10.1016/j.tourman.2009.02.016
- Paraphrase of abstract: the study simulated travel searches with destination keywords and found social media "constitute a substantial part of the search results".
- Note: this is US data from 2010, so it is old.
- Checked: 2 October 2026. Trust: primary (peer-reviewed).

12.4 **Finding (Nepal seasonality):** October is Nepal's busiest month for arrivals. Spring (March to May) and autumn (September to November) are the trekking peaks.
- Sources:
  - "Tourist arrivals near pre-pandemic levels; Nepal records 128,443 visitors in October", The Himalayan Times, reporting Nepal Tourism Board figures. https://thehimalayantimes.com/business/tourist-arrivals-near-pre-pandemic-levels-nepal-records-128443-visitors-in-october
    - Paraphrase: 128,443 visitors in October 2025, the busiest month of 2025.
  - Agency and guide sites, for example https://www.acethehimalaya.com/best-time-for-annapurna-circuit-trek/, describe peaks in late February to April and late September to November.
- Peer-reviewed: Pradhan & Koirala (2024), "Analyzing and Forecasting International Tourist Arrivals in Nepal", *International Journal of Operational Research/Nepal*. https://nepjol.info/index.php/ijorn/article/view/73153. It notes that "seasonal trends influence arrival patterns" but the summary did not give peak months.
- Checked: 2 October 2026. Trust: secondary (news, agencies). Peer-reviewed paper only partly checked.

12.5 **Finding (permit and cost queries):** Many competing Nepal trek pages target "permit", "cost" and "best time" queries; the result pages are full of guides such as "ACAP permit cost". The ACAP permit is issued by the National Trust for Nature Conservation, and agency sites quote NPR 3,000 for foreigners. Some say fees have been "hiked". Fees change, so the engine must never state a fee from memory. A fee belongs in an `[ADD: …]` placeholder unless the listing text gives it.
- Sources (examples only):
  - https://www.magicalnepal.com/travel-guide/annapurna/annapurna-circuit-trek-permits/
  - https://www.thelongestwayhome.com/travel-guides/nepal/permit-entry-fees-national-parks.html
  - https://www.nepalhighlandtreks.com/blog/trekking-permit-entry-fees-hiked
- Status: the current official fee is **unverified**; the NTNC site was not checked.
- Checked: 2 October 2026. Trust: secondary.

12.6 **Unverified:** Think with Google travel research ("micro-moments", what travellers search for when planning). The old thinkwithgoogle.com article URLs now redirect (301) to https://business.google.com/en-all/think/ and the original articles could not be read. Search snippets mention, for example, that travellers look at prices, reviews and activities when planning. Treat this as **unverified secondary** until the articles are found again.

12.7 **Finding:** Google has no Search Central guide written for travel SEO. The travel-specific Google channels are the Hotel Center (hotels), vacation rental structured data (restricted) and Things to do (tours and activities feed). See 5.6 to 5.8.
- Checked: 2 October 2026. Trust: primary (based on what was absent from the structured data gallery and the ecommerce and specialty guides).

## 13. Internal linking and site architecture

13.1 **Finding:** Google reliably follows only `<a href>` links. Anchor text should be descriptive and fairly short; avoid "click here" and keyword stuffing. Every important page needs at least one internal link.
- Source: "Link best practices for Google", Google Search Central. https://developers.google.com/search/docs/crawling-indexing/links-crawlable (last updated 2025-12-10)
- Quote: "Google uses links as a signal when determining the relevancy of pages and to find new pages to crawl." / "Good anchor text is descriptive, reasonably concise, and relevant to the page…"
- Use `rel="nofollow"`, `"sponsored"` or `"ugc"` where they apply, for example on links in agency-written content.
- Checked: 2 October 2026. Trust: primary.

13.2 **Finding (hub and category pages):** Link from menus to category pages, from category pages to sub-categories, and from those to every product (listing). Pages with more internal links count as more important. Use a sitemap when you cannot link to everything.
- Source: "Help Google understand your ecommerce website structure", Google Search Central. https://developers.google.com/search/docs/specialty/ecommerce/help-google-understand-your-ecommerce-site-structure (last updated 2025-12-10)
- Quote: "add links from menus to category pages, from category pages to sub-category pages, and finally from sub-category pages to all product pages." / "the more links a page has to it within a site, the higher the relative importance of the page to other pages on your site." / "Don't use JavaScript events on other HTML DOM elements for navigation."
- MyPipit relevance (inference): hub pages such as "Annapurna treks", "Everest treks" or "Kathmandu hotels" that link to every agency's listing would help both discovery and the duplicate problem in 7.2.
- Checked: 2 October 2026. Trust: primary.

13.3 **Finding:** Breadcrumbs (5.10) show where a page sits in the site hierarchy. Google lists "Breadcrumb" as a supported rich result.
- Checked: 2 October 2026. Trust: primary.

## 14. Hreflang and other languages (Nepali, Hindi, Chinese)

14.1 **Finding:** Give each language its own URL, such as `/ne/`, `/hi/`, `/zh-hans/` or a subdomain. Do not switch language by cookie or browser setting, and do not auto-redirect by language. Google's crawler sends no `Accept-Language` header.
- Source: "Managing multi-regional and multilingual sites", Google Search Central. https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites (last updated 2025-12-10)
- Quote: "Use different URLs for each language version of a page rather than using cookies or browser settings to adjust the content language." / "Avoid automatically redirecting users from one language version of a site to a different language version of a site." / "the crawler sends HTTP requests without setting Accept-Language in the request header."
- Checked: 2 October 2026. Trust: primary.

14.2 **Finding:** hreflang can be set in HTML `<link>` tags, HTTP headers or the sitemap. Each version must list itself and all the others, or the tags may be ignored.
- Codes: ISO 639-1 language codes (for example `ne`, `hi`, `zh`), with optional regions, and script variants such as `zh-Hans` and `zh-Hant`.
- Use `x-default` as the fallback.
- Google detects language from the visible content, not from hreflang or `lang`.
- Source: "Tell Google about localized versions of your page", Google Search Central. https://developers.google.com/search/docs/specialty/international/localized-versions (last updated 2026-09-21)
- Quote: "Each language version must list itself as well as all other language versions." / "Google doesn't use hreflang or the HTML lang attribute to detect the language of a page".
- Checked: 2 October 2026. Trust: primary.

14.3 **Finding:** Different language versions are not duplicates of each other. Same-language regional versions should use both canonical and hreflang.
- Source: canonicalization page (7.1).
- Quote: "Different language versions of a single page are considered duplicates only if the primary content is in the same language."
- Checked: 2 October 2026. Trust: primary.

14.4 **Finding:** Automated translation done at scale "where little value is provided to users" is listed as scaled content abuse (6.3). Machine-translated pages should be reviewed by a person before publishing.
- Checked: 2 October 2026. Trust: primary.

---

## Items marked unverified

- 3.2: the effect of presigned or expiring URLs on Google Images is an inference. Google warns against changing image URLs but does not name presigned URLs.
- 3.3: og:image behaviour on WhatsApp, LinkedIn and X was not checked. Only Meta's (Facebook) docs were.
- 5.4: whether a tour or trek marked as Product qualifies for product snippets is not stated by Google.
- 5.8: whether multi-day treks are eligible products in Things to do is not stated in the overview checked.
- 9.8: the exact steps to give a service account Search Console access were not checked.
- 10.3: that alarms do not run while Chrome is closed is an inference; there is no direct Chrome doc quote.
- 12.5: the current official ACAP and TIMS permit fees were not checked; only agency sites were read.
- 12.6: the Think with Google travel articles have moved and could not be read.
