import React, { useState, useEffect } from 'react';
import axios from 'axios';

const App = () => {
  const [user, setUser] = useState({ username: '', email: '' });
  const [books, setBooks] = useState([]);
  const [newBook, setNewBook] = useState({
    title: '',
    description: '',
    user_username: '',
    rating: '',
    genre_id: '',
  });
  const [editingBookId, setEditingBookId] = useState(null);
  const [genres, setGenres] = useState([]);
  const [selectedGenre, setSelectedGenre] = useState('');
  const [newGenre, setNewGenre] = useState('');
  const [reportData, setReportData] = useState([]);


  useEffect(() => {
    fetchBooks();
    fetchGenres();
  }, []);

  const createUser = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:5000/users', user);
      console.log(response.data.message);
      setUser({ username: '', email: '' });
    } catch (error) {
      console.error('Error creating user:', error);
    }
  };

  const createBook = async () => {
    try {
      if (editingBookId) {
        await updateBook();
      } else {
        const response = await axios.post('http://127.0.0.1:5000/books', newBook);
        console.log(response.data.message);
        resetFormAndRefreshBooks();
      }
    } catch (error) {
      console.error('Error creating book:', error);
    }
  };

  const updateBook = async () => {
    try {
      const response = await axios.put(`http://127.0.0.1:5000/books/${editingBookId}`, newBook);
      console.log(response.data.message);
      resetFormAndRefreshBooks();
    } catch (error) {
      console.error('Error updating book:', error);
    }
  };

  const deleteBook = async (bookId) => {
    try {
      const response = await axios.delete(`http://127.0.0.1:5000/books/${bookId}`);
      console.log(response.data.message);
      fetchBooks();
    } catch (error) {
      console.error('Error deleting book:', error);
    }
  };

  const fetchBooks = async (genreId = null) => {
    try {
      const params = {
        genre_id: genreId,
      };
      const response = await axios.get('http://127.0.0.1:5000/books', {
        params: params,
      });
      setBooks(response.data);
    } catch (error) {
      console.error('Error fetching books:', error);
    }
  };

  const fetchGenres = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/genres');
      setGenres(response.data);
    } catch (error) {
      console.error('Error fetching genres:', error);
    }
  };

  const fetchBookReport = async () => {
    try {
      const params = {
        genre_id: selectedGenre !== '' ? selectedGenre : undefined,
      };
      const response = await axios.get('http://127.0.0.1:5000/books/report', {
        params: params,
      });
      setReportData(response.data);
      fetchBooks(selectedGenre !== '' ? selectedGenre : null);
    } catch (error) {
      console.error('Error fetching book report:', error);
    }
  };

  const createGenre = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:5000/genres', { name: newGenre });
      console.log(response.data.message);
      setNewGenre('');
      fetchGenres();
    } catch (error) {
      console.error('Error creating genre:', error);
    }
  };

  const startEditBook = (book) => {
    setEditingBookId(book.id);
    setNewBook({
      title: book.title,
      description: book.description,
      user_username: book.user_username,
      rating: book.rating.toString(),
    });
  };

  const resetFormAndRefreshBooks = () => {
    setNewBook({
      title: '',
      description: '',
      user_username: '',
      rating: '',
      genre_id: '',
    });
    setEditingBookId(null);
    fetchBooks();
  };

  return (
    <div>
      <h2>Create User</h2>
      <input
        type="text"
        placeholder="User"
        value={user.username}
        onChange={(e) => setUser({ ...user, username: e.target.value })}
      />
      <input
        type="email"
        placeholder="Email"
        value={user.email}
        onChange={(e) => setUser({ ...user, email: e.target.value })}
      />
      <button onClick={createUser}>Create User</button>

      <h2>{editingBookId ? 'Edit' : 'Create'} Review</h2>
      <input
        type="text"
        placeholder="Title"
        value={newBook.title}
        onChange={(e) => setNewBook({ ...newBook, title: e.target.value })}
      />
      <textarea
        placeholder="Review"
        value={newBook.description}
        onChange={(e) => setNewBook({ ...newBook, description: e.target.value })}
      ></textarea>
      <input
        type="text"
        placeholder="User"
        value={newBook.user_username}
        onChange={(e) => setNewBook({ ...newBook, user_username: e.target.value })}
      />
      <input
        type="text"
        placeholder="Rating"
        value={newBook.rating}
        onChange={(e) => setNewBook({ ...newBook, rating: e.target.value })}
      />
      <select
        value={newBook.genre_id}
        onChange={(e) => setNewBook({ ...newBook, genre_id: e.target.value })}
      >
        <option value="">Select Genre</option>
        {genres.map((genre) => (
          <option key={genre.id} value={genre.id}>
            {genre.name}
          </option>
        ))}
      </select>
      <button onClick={createBook}>{editingBookId ? 'Update' : 'Create'} Book</button>


      <div className="add-genre-section">
        <h2>Add Genre</h2>
        <input
          type="text"
          placeholder="Genre Name"
          value={newGenre}
          onChange={(e) => setNewGenre(e.target.value)}
        />
        <button onClick={createGenre}>Add Genre</button>
      </div>

      <div className="report-section">
        <h2>Generate Report</h2>
        <div className="report-controls">
          <label htmlFor="genre-select">Select Genre:</label>
          <select
            id="genre-select"
            value={selectedGenre}
            onChange={(e) => setSelectedGenre(e.target.value)}
          >
            <option value="">All Genres</option>
            {genres.map((genre) => (
              <option key={genre.id} value={genre.id}>
                {genre.name}
              </option>
            ))}
          </select>
          <button onClick={fetchBookReport}>Generate Report</button>
        </div>
        <div className="report-data">
          {Object.keys(reportData).length > 0 ? (
            <div>
              {selectedGenre === '' ? (
                <div>
                  {reportData.avg_rating !== undefined && reportData.avg_rating !== null ? (
                    <p>Average Ratings: {reportData.avg_rating.toFixed(2)}</p>
                  ) : (
                    <p>Average Ratings: N/A</p>
                  )}
                  <p>Ratings: {reportData.num_ratings}</p>
                  <p>Users: {reportData.num_users}</p>
                  <p>Books: {reportData.num_books}</p>
                  {reportData.highest_rated_book && (
                    <p>Best Rated: {reportData.highest_rated_book}</p>
                  )}
                  {reportData.lowest_rated_book && (
                    <p>Worst Rated: {reportData.lowest_rated_book}</p>
                  )}
                </div>
              ) : (
                <div>
                  {reportData.avg_rating !== undefined && reportData.avg_rating !== null ? (
                    <p>Average Ratings: {reportData.avg_rating.toFixed(2)}</p>
                  ) : (
                    <p>Average Ratings: N/A</p>
                  )}
                  <p>Ratings: {reportData.num_ratings}</p>
                  <p>Users: {reportData.num_users}</p>
                  <p>Books: {reportData.num_books}</p>
                  {reportData.highest_rated_book && (
                    <p>Best Rated: {reportData.highest_rated_book}</p>
                  )}
                  {reportData.lowest_rated_book && (
                    <p>Worst Rated: {reportData.lowest_rated_book}</p>
                  )}
                </div>
              )}
            </div>
          ) : (
            <p>No data available for the selected genre.</p>
          )}
        </div>
      </div>

      <div className="reviews-section">
        <h2>Book Reviews</h2>
        {books.length > 0 ? (
          <ul className="review-list">
            {books.map((book) => (
              <li key={book.id} className="review-item">
                <div className="review-header">
                  <h3>{book.title}</h3>
                  <div className="review-actions">
                    <button onClick={() => startEditBook(book)}>Edit</button>
                    <button onClick={() => deleteBook(book.id)}>Delete</button>
                  </div>
                </div>
                <div className="review-details">
                  <p>
                    <strong>Review:</strong> {book.description}
                  </p>
                  <p>
                    <strong>Posted by:</strong> {book.user_username}
                  </p>
                  <p>
                    <strong>Rating:</strong> {book.rating}
                  </p>
                  <p>
                    <strong>Genre:</strong> {book.genre.name}
                  </p>
                  <p>
                    <strong>Posted at:</strong> {book.created_at}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p>No book reviews found.</p>
        )}
      </div>
    </div>
  );
};

export default App;