---
layout: post
title: a post with code
date: 2023-07-30 15:09:00
description: Parsing raw Vietnamese address data
tags: formatting code
categories: sample-posts
featured: true
---

The accuracy and standardization of address data is critical for businesses, particularly in the e-commerce industry. Poorly parsed addresses can lead to slower delivery times, increased package returns, and unhappy customers. For data analysts, transforming raw address data into a standardized format can be a complex and daunting task, with even minor errors potentially having significant financial implications for the company.

The goal of this article is to discuss the unique challenges posed by unstructured Vietnamese address data and to present a practical approach for extracting key information such as provinces, districts, and wards from these addresses. By exploring the characteristics of this data and sharing my own methodology, I hope to provide useful insights and strategies for addressing this common data analytics challenge.

```markdown
Input: an unstructured string of Vietnamese address line
Output: province name, district name, and ward name
```

<h3>Administrative unit structure of Vietnam</h3>

Vietnam is divided into administrative units at three main levels: provinces/municipalities (both referred as provinces), districts/cities (both referred as districts), communes/wards/townships (all referred as wards), and villages/hamlets. At the top of the hierarchy are a combined of 63 provinces and municipalities, which are further divided into districts and cities. Rural districts are then broken down into communes and townships, while urban districts and cities are broken down into wards and communes. It is important to note that there are numeric districts and wards (Quận 7, Phường 11) that need to be considered in choosing the parsing method.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid path="assets/img/9.jpg" class="img-fluid rounded z-depth-1" %}
    </div>
</div>
<div class="caption">
Vietnamese unit structure
</div>

While there are further subdivisions into villages and hamlets, they are rarely used in addresses and official information about them could not be found. Therefore, they will not be included in this post. Additionally, this parsing project will not delve into deeper details such as street and alley names or specific places (e.g., Aeon Mall Hà Đông, Bến Nhà Rồng) as there is not enough data available to collect.

<h3>Understanding Vietnamese address writing</h3>

The Vietnamese alphabet consists of 29 letters, with four diacritics used in seven letters: ă, â, ê, ô, ơ, ư, and đ. An additional five diacritics indicate tone, such as à, á, ả, ã, and ạ. This makes the Vietnamese script distinct from other Latin writing systems. Additional details about these diacritics can be found at this <a href="https://vietnamesetypography.com/diacritical-details/" target="_blank">link</a>.

Now, let’s take a look at a few examples of written address:

```markdown
Fulbright University Vietnam, 105 đường Tôn Dật Tiên, Phường Tân Phú, Quận 7, Thành phố Hồ Chí Minh
// Fulbright University Vietnam, 105 Ton Dat Tien Street, Tan Phu Ward, District 7, Ho Chi Minh City
```

This is a clean example, all administrative units are written correctly, and they are also marked with a unit-defined word like Ward or District.

In reality, we are more likely to see something like this:

```markdown
Fulbright University Vietnam, 105 Tôn Dật Tiên, Tân Phú, Q7, TP.HCM
// Fulbright University Vietnam, 105 Ton Dat Tien, Tan Phu, D7, HCMC
```

Administrative units are often abbreviated or omitted in addresses. Vietnamese readers can usually understand what the unit refers to, even if it’s not spelled out completely. In the above example, “Q” or “TP.” are used to refer to a district or city/municipality, and “Tân Phú” could be used instead of “Phường Tân Phú” (Tan Phu Ward). In some cases, the name of the province is also omitted, such as in Ho Chi Minh City, where readers can infer that the address is within the city without the need for “HCMC.”

Similarly, if an address contains “TP. Cao Bằng” (Cao Bang City), it may not include the province name “tỉnh Cao Bằng” (Cao Bang Prov.), since it’s clear that it’s from Cao Bang and redundant to repeat it. However, determining the correct province based solely on the district name can be challenging, especially when two provinces share the same district name.

Also, there are different diacritic positions of a word in Vietnamese that do not affect its meaning, such as:

```markdown
Khánh Hoà -- Khánh Hòa
Thuỷ Nguyên -- Thủy Nguyên
```

While Vietnamese readers can intuitively recognize these differences, the algorithm should be designed to handle common misspellings and incorrect diacritic placement using fuzzy string matching techniques.

Finally, it’s important to note that many people can recognize Vietnamese addresses without diacritics, such as “Fulbright University Vietnam, 105 Ton Dat Tien, Tan Phu, Quan 7.” However, to prevent ambiguity caused by similar names, the algorithm should prioritize the use of diacritics and only consider diacritic-less units as a last resort when diacritic parsing fails.

In light of these considerations, I propose the following algorithmic process to match Vietnamese addresses:

Step 1: Parse the province name, followed by the district name and then the ward name using their full names.

Step 2: Similar to Step 1, but allowing for 1 misspelling or incorrect diacritic placement.

Step 3: Similar to Step 1, but using diacritic-less unit name.

Step 4: Similar to Step 1, but using abbreviation unit name.

Step 5: If the district and ward names are provided without the province name, parse them and refer to the province based on the known location of the district/ward.

The order of the algorithmic process proposed is designed to minimize the possibility of conflicts caused by random occurrences. For instance, if the algorithm first parses using abbreviations (i.e. HN, HCM), they may appear in other parts of an address could mistakenly be interpreted as administrative units (i.e. Vinh city could be mistakenly parsed from Vinhomes). Thus, we must first attempt to parse with the most specific and accurate information and gradually move towards more general and ambiguous information.

<h3>The Dataset</h3>

The dataset includes 1000 records that reflect actual customer addresses for an e-commerce business. To protect customer privacy, I have randomized the street and alley numbers while preserving the raw structure of the addresses. This allows for accurate analysis of address formats and patterns.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid path="assets/img/9.jpg" class="img-fluid rounded z-depth-1" %}
    </div>
</div>
<div class="caption">Sample addresses</div>

In addition to the customer addresses, I used a modified version of the Vietnamese administrative unit data from the General Statistics Office of Vietnam. This data includes three files for provinces, districts, and wards, with each unit’s name, code, and an accompanying RegEx Name.

You can download the whole data package in this <a href="https://www.kaggle.com/datasets/namngl/testaddressinput" target="_blank">link</a>.

<h3>The Approach</h3>

One common approach to parsing Vietnamese addresses is to use <strong>regular expressions</strong> (RegEx) to match patterns in the address string. Regular expressions are a powerful tool for pattern matching and can be used to extract information such as the province, district, and ward from an address.

Regular expressions consist of a combination of characters and symbols that define a pattern. For example, to extract the numeric district, we can use the pattern:

```markdown
NUMERIC_DISTRICT = "q" + "(uận)?" + "(uan)?" + "[. ]*[1-9][0-9]?"
```

Think about why this pattern works by checking out the <a href="https://www.w3schools.com/python/gloss_python_regex_metacharacters.asp" target="_blank">RegEx metacharacters</a>.

These patterns can be used directly on Python or stored in a CSV files, as demonstrated by some occurences in the Regex Name column. For instance, the pattern “((BRVT)|(Bà Rịa – Vũng Tàu)|(Bà Rịa Vũng Tàu))” can match any of the three names to province Bà Rịa-Vũng Tàu.

However, regular expressions may not always return a result, especially if the address string is incomplete or contains errors. In such cases, we can use fuzzy matching algorithms to match the address string to a database of known addresses or to other sources of information. The algorithm prioritizes lowest Levenshtein distance, which measures the number of insertions, deletions, or substitutions needed to transform one string into another.

By combining regular expressions and fuzzy matching algorithms, we can develop a robust system for parsing Vietnamese addresses and extracting the relevant information.

<h3>Implementation & issues</h3>

For a detailed look at the code, see this <a href="https://github.com/MarcusLe02/Data-Science/blob/main/vietnam_address_parsing/vietnamese-address-parser.ipynb" target="_blank">link</a>.

After completing the parsing steps, we should have the sample results as follows:

# Sample result image

However, there are two challenges that need to be addressed in future work. One of the main issues is that identifying abbreviations and alternative names for administrative units is a manual process, and so far, we have only covered names for Hanoi and Ho Chi Minh City. With knowledge of all other provinces, this issue can be resolved permanently.

An additional issue arises when the algorithm matches a province name to a substring in the address that refers to something entirely different. For example, consider the below address line:

```markdown
"502/26b huỳnh tấn phát; phường bình thuận; q7", parsed as Bình Thuận province
```

This happens because the address line omits the actual province (HCMC), and the algorithm matches the only province-like instance “bình thuận” before attempting to match “q7” (District 7) to HCMC. To address this, we can introduce additional hierarchy conditions into the parsing process to ensure that the identified administrative unit is indeed the correct one. However, this approach is out of scope for this post and would be discuss in the future work.

That’s all for the day. Vietnamese addresses may be unstructured and difficult to parse, but don’t worry, it’s not as bad as trying to untangle a plate of bun cha with forks. With a little patience and the right approach, you can turn those jumbled addresses into beautifully structured data, and avoid ending up with a tangled mess on your plate (or in your dataset!).