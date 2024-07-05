# metapub_analysis
scripts and data for more complex analysis of metapub's capabilities

Below in each section, find a description of current analysis and experiment characteristics 


## FindIt Coverage

### Goals

* Greatly increase the number of Journals found in MEDLINE that are supported by FindIt for paper PDF url production.
* Expand publisher coverage with additional FindIt machinery.
* Publish the number of Journals FindIt supports.

### How much coverage does FindIt have over the journals in PubMed? 

To find out, we need to scan all of the Journal abbreviations found in the MEDLINE journals list, which is an XML file.  When those are extracted, we need to query NCBI to get a sampler of PMIDs from each of these journal abbreviations.  Say one of the newest, one of the oldest, and one from a year somewhere in the middle.  We only need to do this for journals that aren't yet in the list of supported journals in `metapub.findit.SUPPORTED_JOURNALS`, so it's fine to skip any journal abbreviations from the MEDLINE list that are found in SUPPORTED_JOURNALS -- we'll note them in the CSV as "FindIt_support=True" but not bother looking up PMIDs for it, to save time.

We'll create a CSV from that scan, giving us the total number of journals not currently covered in FindIt.  The CSV should have one row per journal, and up to 3 sample PMIDs per journal.

This CSV is called "findit_journal_coverage.csv"


### Automatically expand FindIt coverage over Medline journals.

Next, we should iterate over all of the PMIDs in "findit_journal_coverage.csv" and see if we can "guess" the publisher.  Since the vast majority of Journals fall under just a few different publisher headings, we should be able to sort a lot of journal abbreviations this way.  E.g. all URLs resulting from a dx.doi.org redirect that land on a "sciencedirect.com" URL belong to the Elsevier / ScienceDirect collection of journals.  Likewise "karger.com" for Karger, "tandfonline" for Taylor & Francis, and so on.

So for each PMID, try to get a DOI and use it to create a dx.doi.org link.  For the first pass, just use the direct pmid2doi method.  Later passes we can try more complex methods like CrossRef if it seems worthwhile.

Any pubmed article we can attach a DOI to, we can get a dx.doi.org link.  Following that link should lead us to a publisher page. If it does, write that PMID, the journal abbreviation, the URL, the DOI, and our "guess" at which publisher it is into a new CSV.  We'll call it "findit_noformat.csv".  

The resultant CSV can then be parsed and sorted by "publisher_guess" to create text files for each publisher, one journal abbreviation per line.  These journals can be reasonably believed to be supported by the existing FindIt machinery and dropped into each publisher category under `metapub.findit.journals`.

Many PMIDs will end up with "publisher_guess" set to "Unknown".  These we can try to address using pattern-finding methodologies on their base URL, although some manual work will have to be done to figure out how to produce a PDF link.

