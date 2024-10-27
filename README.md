# Bookly

**Bookly** is a book management application built with **FastAPI** (Python). It offers core CRUD (Create, Read, Update, Delete) functionalities for managing a book catalog, along with user authentication features. This project provides a fast, secure, and scalable way to handle book data and user accounts, making it a great example of modern web application development with Python.

## Features

- **CRUD Operations**:
  - Create, update, delete, and list books in the catalog.
  - Detailed book information, including title, author, description, and publication details.
- **User Authentication**:
  - Secure user registration and login.
  - Token-based authentication to protect endpoints.
  - User roles for access control (e.g., admin and regular users).
- **Book Search**:
  - Search for books by title, author, or genre.
- **Pagination**:
  - Paginated results for better performance and user experience when dealing with large book catalogs.
- **Data Validation**:
  - Strong validation for incoming requests, ensuring data integrity.

## Tech Stack

- **Backend**: FastAPI (Python)
- **JWT**: The JWT token used to authenticate requests
- **Database**: Postgresql (or any preferred database supported by SQLAlchemy)
- **Authentication**: JWT-based authentication using OAuth2

## Future Improvements

- Add more robust role-based access controls.
- Integration with external APIs for enhanced book information.
- Add Docker support for containerization.
- Implement unit and integration testing.
