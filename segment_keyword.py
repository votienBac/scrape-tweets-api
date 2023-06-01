import nltk
from rake_nltk import Rake

def extract_keywords(text):
    # Tải stopwords và punkt tokenizer nếu cần thiết
    nltk.download('stopwords')
    nltk.download('punkt')

    # Khởi tạo Rake
    r = Rake()

    # Trích xuất từ khóa từ văn bản
    r.extract_keywords_from_text(text)
    rankedList = r.get_ranked_phrases_with_scores()

    # Tạo danh sách từ khóa đã được định dạng
    keywordList = []
    for keyword in rankedList:
        keyword_updated = keyword[1].split()
        keyword_updated_string = " ".join(keyword_updated[:2])
        keywordList.append(keyword_updated_string)

    return keywordList