import streamlit as st
import pickle
import pandas as pd
import requests
import time


# Function to fetch movie poster with error handling & retries
def fetch_poster(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US'

    for _ in range(3):  # Retry up to 3 times
        try:
            response = requests.get(url, timeout=5)  # Set timeout
            response.raise_for_status()  # Raise error for bad response (e.g., 404, 500)
            data = response.json()

            if 'poster_path' in data and data['poster_path']:
                return "http://image.tmdb.org/t/p/w500/" + data['poster_path']
            else:
                return "https://via.placeholder.com/500x750?text=No+Image"  # Fallback image

        except requests.exceptions.RequestException as e:
            print(f"Error fetching poster: {e}")
            time.sleep(2)  # Wait before retrying

    return "https://via.placeholder.com/500x750?text=Error+Fetching+Image"  # Final fallback


# Function to recommend movies
def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

        recommended_movies = []
        recommended_movies_posters = []

        for i in movies_list:
            movie_id = movies.iloc[i[0]].movie_id  # Get correct movie ID
            recommended_movies.append(movies.iloc[i[0]].title)
            recommended_movies_posters.append(fetch_poster(movie_id))  # Fetch poster safely

        return recommended_movies, recommended_movies_posters

    except Exception as e:
        print(f"Error in recommendation: {e}")
        return [], []


# Load movie data and similarity matrix
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Streamlit UI
st.title('Movie Recommender System')

selected_movie_name = st.selectbox('Select a movie:', movies['title'].values)

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)

    if not names:
        st.error("Could not fetch recommendations. Please try again later.")
    else:
        cols = st.columns(5)  # Display recommendations in columns

        for col, name, poster in zip(cols, names, posters):
            with col:
                st.text(name)
                st.image(poster)
