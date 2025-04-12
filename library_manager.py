import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import random
##import plotly.express as px
#import plotly.graph_objects as go
#from streamlit_lottie import st_lottie
import requests

#set page configuration
st.set_page_config(
    page_title="Personal Library Managment System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

#custom css for styling
st.markdown("""
    <style>
        .main-header {
        font-size: 3rem !important;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        .sub_header {
        font-size: 1.8rem !important;
        color: #3BB2F6;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 1rem;
        }
        .success-message {
        padding: 1rem;
        background-color: #ECFDF5;
        border-left: 5px solid #10B981;
        border-radius: 0.25rem;
        }

        .warning-message {
        padding: 1rem;
        background-color: #FEF3E2;
        border-left: 5px solid #F59E0B;
        border-radius: 0.375rem;
        }

        .book-card{
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #3BB2F6;
        transition: transform 0.3s ease;
        box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05);
        }

        .book-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        }

        .read-badge {
        background-color: #10B981;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
        }

        .unread-badge {
        background-color: #F87171;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
        }

        .action-button {
        margin-right: 0.5rem;
        }
        .stButton button{
        border-radius: 0.375rem;
        }
</style>
""", unsafe_allow_html=True)

def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception as e:
        st.error(f"Error loading Lottie file: {e}")
        return None

if 'library' not in st.session_state:
    st.session_state.library = []
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'book_added' not in st.session_state:
    st.session_state.book_added = False
if 'book_removed' not in st.session_state:
    st.session_state.book_removed = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = "library"
if 'search_results' not in st.session_state:
    st.session_state.search_results = []

    #load library
def load_library():
    try:
        if os.path.exists('library.json'):
            with open('library.json', 'r') as file:
                st.session_state.library = json.load(file)
            return True
        return False
    except Exception as e:
        st.error(f"Error loading library: {e}")
        st.session_state.library = []

    #save library
def save_library():
    try:
        with open('library.json','w') as file:
            json.dump(st.session_state.library, file)
        return True
    except Exception as e:
        st.error(f"Error saving library: {e}")
        return False

    #add a book to library
def add_book(title, author, publication_year, genre, read_status):
    book ={
        'title': title,
        'author': author,
        'publication_year': publication_year,
        'genre': genre,
        'read_status': read_status,
        'added_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.library.append(book)
    save_library()
    st.session_state.book_added = True
    time.sleep(0.5) #animation delay

    #remove book
def remove_book(index):
        if 0 <= index < len(st.session_state.library):
            del st.session_state.library[index]
            save_library()
            st.session_state.book_removed = True
            return True
        return False
        #search book
def search_books(search_term, search_by):
    search_term = search_term.lower()
    results = []
    for book in st.session_state.library:
        if search_by == "Title" and search_term in book['title'].lower():
            results.append(book)
        elif search_by == "Author" and search_term in book['author'].lower():
            results.append(book)
        elif search_by == "Genre" and search_term in book['genre'].lower():
            results.append(book)
    st.session_state.search_results = results

    #calculate library stats
def calculate_library_stats():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book['read_status'] == 'Read')
    unread_books = total_books - read_books
    genre_counts = {}
    for book in st.session_state.library:
        genre = book['genre']
        genre_counts[genre] = genre_counts.get(genre, 0) + 1
    return total_books, read_books, unread_books, genre_counts

load_library()

# --- Sidebar ---
with st.sidebar:
    st.title("📚 Library Actions")
    if st.button("Show All Books"):
        st.session_state.current_view = "library"
        st.session_state.search_results = []
    if st.button("Add New Book"):
        st.session_state.current_view = "add_book"
    st.subheader("Search Books")
    search_term = st.text_input("Enter search term:")
    search_by = st.selectbox("Search by:", ["Title", "Author", "Genre"])
    if st.button("Search"):
        if search_term:
            search_books(search_term, search_by)
            st.session_state.current_view = "search_results"
            st.session_state.search_history.append(f"Searched '{search_term}' by {search_by} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.warning("Please enter a search term.")
    if st.button("View Search History"):
        st.session_state.current_view = "search_history"
    st.subheader("Library Statistics")
    total_books, read_books, unread_books, genre_counts = calculate_library_stats()
    st.metric("Total Books", total_books)
    st.metric("Read Books", read_books)
    st.metric("Unread Books", unread_books)
    if genre_counts:
        st.caption("Book Genres:")
        for genre, count in genre_counts.items():
            st.caption(f"- {genre}: {count}")

# --- Main Content ---
st.markdown("<h1 class='main-header'>📚 My Personal Library 📚</h1>", unsafe_allow_html=True)

if st.session_state.book_added:
    st.success("Book added successfully!")
    st.session_state.book_added = False
if st.session_state.book_removed:
    st.warning("Book removed successfully!")
    st.session_state.book_removed = False

if st.session_state.current_view == "library":
    st.markdown("<h2 class='sub_header'>Your Library</h2>", unsafe_allow_html=True)
    if not st.session_state.library:
        st.info("Your library is currently empty. Add some books!")
    else:
        for index, book in enumerate(st.session_state.library):
            with st.container():
                col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 1, 1])
                with col1:
                    st.markdown(f"<h4 style='margin-bottom: 0.1rem;'>{book['title']}</h4>", unsafe_allow_html=True)
                    st.markdown(f"<p style='font-size: 0.9rem; color: #555;'>By {book['author']} ({book['publication_year']})</p>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<p style='font-size: 0.9rem;'>Genre: {book['genre']}</p>", unsafe_allow_html=True)
                with col3:
                    if book['read_status'] == 'Read':
                        st.markdown("<span class='read-badge'>Read</span>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span class='unread-badge'>Unread</span>", unsafe_allow_html=True)
                with col6:
                    if st.button("Remove", key=f"remove_{index}", use_container_width=True):
                        remove_book(index)
                        st.rerun()

elif st.session_state.current_view == "add_book":
    st.markdown("<h2 class='sub_header'>Add a New Book</h2>", unsafe_allow_html=True)
    with st.form(key='add_book_form'):
        title = st.text_input("Title:")
        author = st.text_input("Author:")
        publication_year = st.number_input("Publication Year:", min_value=0, max_value=datetime.now().year, step=1)
        genre = st.text_input("Genre:")
        read_status = st.selectbox("Read Status:", ["Read", "Unread"])
        submit_button = st.form_submit_button("Add Book")
        if submit_button:
            if title and author and genre:
                add_book(title, author, int(publication_year), genre, read_status)
            else:
                st.warning("Please fill in all the fields.")

elif st.session_state.current_view == "search_results":
    st.markdown(f"<h2 class='sub_header'>Search Results ({len(st.session_state.search_results)} found)</h2>", unsafe_allow_html=True)
    if not st.session_state.search_results:
        st.info("No books found matching your search criteria.")
    else:
        for index, book in enumerate(st.session_state.search_results):
            with st.container():
                col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 1, 1])
                with col1:
                    st.markdown(f"<h4 style='margin-bottom: 0.1rem;'>{book['title']}</h4>", unsafe_allow_html=True)
                    st.markdown(f"<p style='font-size: 0.9rem; color: #555;'>By {book['author']} ({book['publication_year']})</p>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<p style='font-size: 0.9rem;'>Genre: {book['genre']}</p>", unsafe_allow_html=True)
                with col3:
                    if book['read_status'] == 'Read':
                        st.markdown("<span class='read-badge'>Read</span>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span class='unread-badge'>Unread</span>", unsafe_allow_html=True)
                with col6:
                    if st.button("Remove", key=f"remove_search_{index}", use_container_width=True):
                        remove_book(st.session_state.library.index(book)) # Find the index in the main library
                        st.session_state.current_view = "library" # Go back to the main library view
                        st.rerun()

elif st.session_state.current_view == "search_history":
    st.markdown("<h2 class='sub_header'>Search History</h2>", unsafe_allow_html=True)
    if not st.session_state.search_history:
        st.info("Your search history is empty.")
    else:
        for item in reversed(st.session_state.search_history):
            st.markdown(f"- <small>{item}</small>", unsafe_allow_html=True)
