import requests
from pyisbn import convert as convert_isbn

def convert_row_to_dict(row):
    row_dict = {}
    for column in row.__table__.columns:
        row_dict[column.name] = str(getattr(row, column.name))

    return row_dict

def get_info_google_books(book, GBOOKS_key):
    url = "https://www.googleapis.com/books/v1/volumes"
    payload = {"q": "isbn:{}".format(book.isbn), "key": GBOOKS_key}


    response = requests.get("https://www.googleapis.com/books/v1/volumes", params=payload)

    book_json = response.json()

    book_info_dict = {"genres": [],
                      "summary": None,
                      "cover_img": None,
                      "response": book_json}
    
    if book_json.get("totalItems", 0) >= 1:
        try:
            book_info_dict["summary"] = book_json["items"][0]["volumeInfo"]["description"]
            book_info_dict["cover_img"] = book_json["items"][0]["volumeInfo"]["imageLinks"]["thumbnail"]
            book_info_dict["genres"] = book_json["items"][0]["volumeInfo"]["categories"]
        except KeyError:
            print("Need a new data source")

    return book_info_dict

def get_info_open_library(book):

    # library.link requires isbn-13, so convert book.isbn to isbn-13
    isbn13 = convert_isbn(book.isbn)

    #use isbn-13 to get url for nearby library search
    open_library_url = "https://openlibrary.org/api/books"
    payload = {"bibkeys" : "ISBN:{}".format(isbn13), "format" : "json", "jscmd" : "data"}

    response = requests.get(open_library_url, params=payload)
    if response:
        book_json = response.json()
        book_info_dict = {"genres": [],
                          "summary": None,
                          "excerpts": None,
                          "cover_img": None,
                          "response": book_json,
                          "previewURL": None}

        print(book_json)

        isbnstring = "ISBN:{}".format(isbn13)
        if book_json.get(isbnstring):
            try:
                if book_json[isbnstring].get('cover'):
                    book_info_dict["cover_img"] = book_json[isbnstring]["cover"]["medium"]
                
                if book_json[isbnstring].get('excerpts'):
                    book_info_dict["excerpts"] = book_json[isbnstring]['excerpts'][0]['text']
                
                for subject in book_json[isbnstring]['subjects'][:3]:
                    book_info_dict["genres"].append(subject['name'])

                if book_json[isbnstring].get('ebooks'):
                    if book_json[isbnstring]['ebooks'][0].get('preview_url'):
                        book_info_dict["previewURL"] = book_json[isbnstring]['ebooks'][0]['preview_url']
                        print("PREVIEW URL IS", book_info_dict["previewURL"])

            except KeyError:
                print("Open Library data not as expected")


    return book_info_dict

def create_combined_book_info_dict(open_lib_info, google_books_info, book_dict, avg_rating, book):

        book_dict["genres"] = open_lib_info['genres']
        book_dict["excerpts"] = open_lib_info['excerpts']
        book_dict["summary"] = google_books_info['summary']
        book_dict["cover_img"] = open_lib_info['cover_img']
        # book_dict["book_json"] = open_lib_info['response']
        book_dict["previewURL"] = open_lib_info['previewURL']
        book_dict["authorLink"] = "/authors/" + book.author
        book_dict['titleLink'] = '/books/' + str(book.book_id)
        print(book_dict)

        if not book_dict["genres"]:
            book_dict["genres"] = google_books_info['genres']
        if not book_dict["cover_img"]:
            book_dict["cover_img"] = google_books_info['cover_img']

        book_dict["avgRating"] = avg_rating

        return book_dict




