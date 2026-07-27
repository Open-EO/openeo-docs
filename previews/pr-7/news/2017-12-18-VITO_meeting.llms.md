# First week of intensive collaboration: Dec 4-6, 2017

Author

Edzer Pebesma

Published

December 18, 2017

On Dec 4-6, VITO’s [remote sensing lab](https://remotesensing.vito.be/) hosted the first openEO *week of intensive collaboration*, in Mol, Belgium. Thirteen developers from 8 different partners gathered to discuss, and work on realising the [first three use cases](https://appelmar.github.io/openeo-api-docs/poc/index.html), which are planned to be delivered in Month 6 (March 2018):

> First week of intense collaboration for [\#openEO](https://twitter.com/hashtag/openEO?src=hash&ref_src=twsrc%5Etfw) [@VITO_RS\_](https://twitter.com/VITO_RS_?ref_src=twsrc%5Etfw), drafting a first API and doing use cases. [@MundialisInfo](https://twitter.com/MundialisInfo?ref_src=twsrc%5Etfw) [@EODC_GmbH](https://twitter.com/EODC_GmbH?ref_src=twsrc%5Etfw) [\#ifgi](https://twitter.com/hashtag/ifgi?src=hash&ref_src=twsrc%5Etfw) [@CopernicusEU](https://twitter.com/CopernicusEU?ref_src=twsrc%5Etfw) [@sinergise](https://twitter.com/sinergise?ref_src=twsrc%5Etfw) [@EURAC](https://twitter.com/EURAC?ref_src=twsrc%5Etfw) [\#JRC](https://twitter.com/hashtag/JRC?src=hash&ref_src=twsrc%5Etfw) [pic.twitter.com/9uCYd9A96S](https://t.co/9uCYd9A96S)
>
> — openEO (@open_EO) [December 5, 2017](https://twitter.com/open_EO/status/938000627078230016?ref_src=twsrc%5Etfw)

We worked on the following back-ends:

- Sentinel hub
- EODC file-based
- Rasdaman
- GRASS
- GeoTrellis

and on the R and python clients, and started working on a \<a :href=“\$site.themeConfig.docPath + ‘glossary.html’”\>glossary.

Among the many insights we gathered by sitting together and talk, we found that

- the “core API” as described in the proposal is not so much a software layer on itself, but rather an API in front of every compute back-end; this simplifies the whole architecture pretty much
- OpenSearch should have the ability to describe *collections* of granules (or images, tiles) in addition to describing individual granules
- band can be seen as array dimension as well as attributes of array records, but seeing it as a dimension may make life easier
- use case 1 can be described as a sequence of filter operations (on image collection, bounding box, date range, and bands) followed by two aggregate operations (compute division over bands, compute mininum over time)

Intermediate results can be found in a bunch of repositories, mostly proof-of-concept, on the openEO [Github organisation](https://github.com/Open-EO/).
