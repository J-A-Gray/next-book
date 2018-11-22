import unittest 

from server import app
from database_functions import get_last_user_id, add_anon_user, get_last_rating_id, get_book_id, add_rating, create_user_list, create_neighbors_book_dict, get_recommendations_lst, get_books_by_author, get_book_by_title, get_book_by_book_id
from model import *
from outward import write_rating_data

class NextBookTests(unittest.TestCase):
    """Test NextBook site"""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    def test_homepage(self):
        result = self.client.get("/")
        self.assertIn(b"Nextbook", result.data)

    def test_lovedbooks(self):
        result = self.client.get('/lovedbooks')
        self.assertIn(b"Find Your Next Book", result.data)

    # def test_lovedbooksresults(self):
    #     result = self.client.get('/lovedbooksresults', data={'book1': '142407577',
    #                                                    'book2': '1934137197', 
    #                                                    'book3': '1713221', 
    #                                                    'book4': '2310015', 
    #                                                    'book5': '6161413',
    #                                                    'user_id': '1'},
    #                                                    follow_redirects=True)

    #     self.assertIn(b"I think you might like", result.data)
    #     self.assertNotIn(b'Find', result.data)






class NextBookTestsDatabase(unittest.TestCase):

    def setUp(self):
        """Set up for database function testing"""

        #Get the Flask test client
        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        #connect to test database
        connect_to_db(app, db_uri='postgresql:///testbook') #not connecting to the testbook db

        #create the tables and add the sample data
        db.create_all()
        example_data()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_testbook(self):
        """Test that the test db is being used"""
        book_count = len(Book.query.all())
        user_count = len(User.query.all())
        rating_count = len(Rating.query.all())


        self.assertEqual(book_count, 5)
        self.assertEqual(user_count, 5)
        self.assertEqual(rating_count, 10)


    def test_books(self):
        """Test that book list route is pulling data from the db """
        result = self.client.get('/books')
        self.assertIn(b"The White Lioness", result.data)
        self.assertNotIn(b"Brief History of Time", result.data)


    def test_get_last_user_id(self):
        """Test if the last user can be retieved from the database"""
        user_id = get_last_user_id()
        self.assertEqual(user_id, 5)
        self.assertNotEqual(user_id, 10000)


    def test_add_anon_user(self):

        anon = add_anon_user()
        self.assertEqual(anon.user_id, 6)
        self.assertLess(anon.user_id, 7)


    def test_get_last_rating_id(self):
        """Tests if last rating id can be retrieve from the database"""

        rating_id = get_last_rating_id()

        self.assertEqual(rating_id, 10)
        self.assertLess(rating_id, 11)


    # def test_get_book_id(self):
    #     """Test to get a book_id from an ISBN and display title on book_id page"""

    #     book_id = get_book_id(isbn='7491433')
    #     result = self.client.get('/books/'+ str(book_id))
    #     self.assertIn(b"The Shock of the Fall", result.data)
    #     self.assertNotIn(b"Brief History of Time", result.data)

    # def test_add_rating(self):

    #     rating = add_rating(user_id=1, book_id=7695)

    #     self.assertEqual(rating.book_id, 7695)

    #     result = self.client.get('/books/' + str(rating.book_id))
    #     self.assertIn(b"/users/1", result.data)
    #     self.assertNotIn(b"/users/15", result.data)


    def test_create_user_list(self):

        user_book_lst = create_user_list(user_id=1)

        self.assertIsInstance(user_book_lst[0], Book)


    def test_create_neighbors_book_dict(self):
        user_book_lst = create_user_list(user_id=1)
        user_book_id_lst = []
        for book in user_book_lst:
            user_book_id_lst.append(book.book_id)

        neighbors_dict = create_neighbors_book_dict(neighbors_user_id_lst=['1','2'], user_book_lst=user_book_id_lst, score=5)
        for key in neighbors_dict.keys():
            self.assertIsInstance(key, Book)

        
        neighbors_book_lst = []
        for key in neighbors_dict.keys():
            neighbors_book_lst.append(key.author)
        self.assertIn('Bernard Cornwell', neighbors_book_lst)
        self.assertNotIn('Marilynne Robinson', neighbors_book_lst)

    def test_get_books_by_author(self):
        """Test if (case-insensitive) db search by author function works"""
        books = get_books_by_author("ahern")
        author_lst = []
        for book in books:
            author_lst.append(book.author)
        self.assertIn("Cecelia Ahern", author_lst)


    def test_get_book_by_title(self):
        """Test if (case-insensitive) db search by title function works"""
        books = get_book_by_title("(the saxon stories, #6)")
        title_lst = []
        for book in books:
            title_lst.append(book.title)
        self.assertIn("Death of Kings (The Saxon Stories, #6)", title_lst)

        books2 = get_book_by_title("shock of the")
        title_lst2 = []
        for book in books2:
            title_lst2.append(book.title)
        self.assertIn("The Shock of the Fall", title_lst2)

    def test_get_book_by_book_id(self):
        """Test if db search by book_id function works"""
        book = get_book_by_book_id(3327)
        self.assertIn("Shock", book.title)

    
    # def test_get_recommendations_lst(self):

    #     user_book_lst = create_user_list(user_id=1)
    #     user_book_id_lst = []
    #     for book in user_book_lst:
    #         user_book_id_lst.append(book.book_id)

    #     neighbors_book_dict = create_neighbors_book_dict(neighbors_user_id_lst=['1','2'], user_book_lst=[], score=5)

    #     recommendations = get_recommendations_lst(neighbors_book_dict=neighbors_book_dict, num_neighbors=4)
    #     self.assertIsInstance(recommendations[0], Book)

#Write a test to test csv writer from outward.py


if __name__ == "__main__":

    unittest.main()
    init_app()

