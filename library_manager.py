import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# Set page configuration
st.set_page_config(
    page_title="Personal Library Manager",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem !important;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: center;
    }
    .sub-header {
        font-size: 1.8rem !important;
        color: #3B82F6;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .success-message {
        padding: 1rem;
        background-color: #ECFDF5;
        border-left: 5px solid #10B981;
        border-radius: 0.375rem;
    }
    .warning-message {
        padding: 1rem;
        background-color: #FEF3C7;
        border-left: 5px solid #F59E0B;
        border-radius: 0.375rem;
    }
    .book-card {
        background-color: #F3F4F6;
        color: #000000; /* Text color for visibility */
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 5px solid #3B82F6;
        transition: transform 0.3s ease;
    }
    .book-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Load Lottie animation
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Initialize session state
if 'library' not in st.session_state:
    st.session_state.library = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'book_added' not in st.session_state:
    st.session_state.book_added = False
if 'book_removed' not in st.session_state:
    st.session_state.book_removed = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = "library"  # Fixed typo from "curreent_view"

# Load library from JSON file
def load_library():
    if os.path.exists('library.json'):
        with open('library.json', 'r') as file:
            st.session_state.library = json.load(file)

# Save library to JSON file
def save_library():
    try:
        with open('library.json', 'w') as file:
            json.dump(st.session_state.library, file, indent=4)
    except Exception as e:
        st.error(f"Error saving library: {e}")

# Add a new book
def add_book(title, author, publication_year, genre, read_status):
    book = {
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
    time.sleep(0.5)

# Remove a book
def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True
        return True
    return False

# Search books (using .get() to avoid KeyError)
def search_books(search_term, search_by):
    search_term = search_term.lower()
    results = [book for book in st.session_state.library if search_term in book.get(search_by.lower(), "").lower()]
    st.session_state.search_results = results

# Library statistics (using .get() for safe key access)
def get_library_stats():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book.get('read_status', False))
    percent_read = (read_books / total_books * 100) if total_books > 0 else 0

    genres = {}
    authors = {}
    decades = {}

    for book in st.session_state.library:
        genre = book.get("genre", "Unknown")
        genres[genre] = genres.get(genre, 0) + 1

        author = book.get("author", "Unknown")
        authors[author] = authors.get(author, 0) + 1

        pub_year = book.get("publication_year")
        if pub_year:
            decade = (pub_year // 10) * 10
        else:
            decade = "Unknown"
        decades[decade] = decades.get(decade, 0) + 1

    return {
        'total_books': total_books,
        'read_books': read_books,
        'percent_read': percent_read,
        'genres': dict(sorted(genres.items(), key=lambda x: x[1], reverse=True)),
        'authors': dict(sorted(authors.items(), key=lambda x: x[1], reverse=True)),
        'decades': dict(sorted(decades.items()))
    }

# Load library on startup
load_library()

# Sidebar navigation
st.sidebar.markdown("<h1 style='text-align: center;'>📚 Navigation</h1>", unsafe_allow_html=True)
lottie_book = load_lottieurl("https://assets9.lottiefiles.com/temp/lf20_aKAfIn.json")
if lottie_book:
    with st.sidebar:
        st_lottie(lottie_book, height=200, key="book_animation")

nav_options = st.sidebar.radio(
    "Choose an option:",
    ["View Library", "Add Book", "Search Books", "Library Statistics"]
)
# Normalize current view for later use
st.session_state.current_view = nav_options.lower().replace(" ", "_")

# Main UI
st.markdown("<h1 class='main-header'>Personal Library Manager</h1>", unsafe_allow_html=True)

if st.session_state.current_view == "add_book":
    st.markdown("<h2 class='sub-header'>Add a New Book</h2>", unsafe_allow_html=True)
    with st.form(key='add_book_form'):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Book Title")
            author = st.text_input("Author")
            publication_year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, step=1)
        with col2:
            genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Science", "Technology", "Fantasy", "Other"])
            read_status = st.radio("Read Status", ["Read", "Unread"])
        submit_button = st.form_submit_button(label="Add Book")
        if submit_button and title and author:
            add_book(title, author, publication_year, genre, read_status == "Read")
            st.success("Book added successfully!")
            st.balloons()  # Trigger balloons immediately after addition

elif st.session_state.current_view == "view_library":
    st.markdown("<h2 class='sub-header'>Your Library</h2>", unsafe_allow_html=True)
    if st.session_state.book_added:
        st.balloons()
        st.session_state.book_added = False
    if not st.session_state.library:
        st.info("Your library is empty. Please add some books.")
    else:
        for index, book in enumerate(st.session_state.library):
            st.markdown(f"""
            <div class='book-card'>
                <h3>{book.get('title', 'N/A')}</h3>
                <p><strong>Author:</strong> {book.get('author', 'N/A')}</p>
                <p><strong>Year:</strong> {book.get('publication_year', 'N/A')}</p>
                <p><strong>Genre:</strong> {book.get('genre', 'N/A')}</p>
                <p><strong>Read:</strong> {"Yes" if book.get('read_status', False) else "No"}</p>
            </div>
            """, unsafe_allow_html=True)
            # Add a remove button for each book
            if st.button("Remove Book", key=f"remove_{index}"):
                remove_book(index)
                st.success(f"Removed book: {book.get('title', 'N/A')}")
                if hasattr(st, "experimental_rerun"):
                    st.experimental_rerun()
                else:
                    st.warning("Please refresh the page to see the updated library.")

elif st.session_state.current_view == "search_books":
    st.markdown("<h2 class='sub-header'>Search Books</h2>", unsafe_allow_html=True)
    search_term = st.text_input("Enter search term:")
    search_by = st.selectbox("Search by:", ["Title", "Author", "Genre"])
    if st.button("Search"):
        search_books(search_term, search_by)
    if st.session_state.search_results:
        for book in st.session_state.search_results:
            st.markdown(f"""
            <div class='book-card'>
                <h3>{book.get('title', 'N/A')}</h3>
                <p><strong>Author:</strong> {book.get('author', 'N/A')}</p>
                <p><strong>Year:</strong> {book.get('publication_year', 'N/A')}</p>
                <p><strong>Genre:</strong> {book.get('genre', 'N/A')}</p>
                <p><strong>Read:</strong> {"Yes" if book.get('read_status', False) else "No"}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No results found. Try a different search term.")

elif st.session_state.current_view == "library_statistics":
    st.markdown("<h2 class='sub-header'>Library Statistics</h2>", unsafe_allow_html=True)
    stats = get_library_stats()
    st.metric("Total Books", stats['total_books'])
    st.metric("Books Read", stats['read_books'])
    st.metric("Percentage Read", f"{stats['percent_read']:.1f}%")
    
    # Chart: Books by Genre - attractive, simple bar chart
    if stats['genres']:
        df_genres = pd.DataFrame(list(stats['genres'].items()), columns=["Genre", "Count"])
        fig_genres = px.bar(
            df_genres,
            x="Genre",
            y="Count",
            title="Books by Genre",
            text_auto=True,
            color="Genre",
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_genres.update_layout(title={'x':0.5})
        st.plotly_chart(fig_genres, use_container_width=True)
    
    # Chart: Books by Decade - clean and simple
    if stats['decades']:
        df_decades = pd.DataFrame(list(stats['decades'].items()), columns=["Decade", "Count"])
        df_decades = df_decades.sort_values("Decade")
        fig_decades = px.bar(
            df_decades,
            x="Decade",
            y="Count",
            title="Books by Decade",
            text_auto=True,
            color="Decade",
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_decades.update_layout(title={'x':0.5})
        st.plotly_chart(fig_decades, use_container_width=True)
    
    # Chart: Top 10 Authors - attractive donut chart
    if stats['authors']:
        df_authors = pd.DataFrame(list(stats['authors'].items()), columns=["Author", "Count"])
        df_authors = df_authors.sort_values("Count", ascending=False).head(10)
        fig_authors = px.pie(
            df_authors,
            values="Count",
            names="Author",
            title="Top 10 Authors",
            template="plotly_white",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig_authors.update_layout(title={'x':0.5})
        st.plotly_chart(fig_authors, use_container_width=True)

st.markdown("---")
st.markdown("© 2025 Raffay Personal Library Manager", unsafe_allow_html=True)

