from rake_nltk import Rake
# import yake

def keyword_extration(text):
    # Init Rake
    rake_mltk_var = Rake()

    rake_mltk_var.extract_keywords_from_text(text)
    rankedList = rake_mltk_var.get_ranked_phrases()[:10]
    return rankedList

    # language = "en"
    # max_ngram_size = 1
    # deduplication_threshold = 0.9
    # numOfKeywords = 20
    # custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, 
    #                                             dedupLim=deduplication_threshold, top=numOfKeywords, features=None, )
    # keywords = custom_kw_extractor.extract_keywords(text)
    # return keywords
