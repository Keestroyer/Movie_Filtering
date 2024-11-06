import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px

st.title('Movie Analysis')
st.subheader("Movie Database Cleaning and Analysis By Keegan Nunes")

df1= pd.read_csv("movie.csv")

tab1,tab3,tab4 = st.tabs(["Data Cleaning",'Data Visualisation','Movie Searchbar'])

with tab1:
    st.header("Movie Dataset")
    st.dataframe(df1)
    st.subheader('Uncleaned Data Description')
    st.write(df1.describe())
    
    st.write('Null Values',df1.isnull().sum())
    df=df1.dropna()
    st.subheader("Cleaned data Description")
    st.write(df.describe())
    st.subheader("First 5 Rows")
    st.write(df.head())
    

# Split genres into separate columns
# First, create a list of all unique genres
genres = set()
for genre_list in df['Genre'].str.split(','):
    genres.update(genre_list)

# Create new columns for each genre
for genre in genres:
    df[f'{genre.strip()}'] = df['Genre'].str.contains(genre.strip()).astype(int)

# Split actors into separate columns
# First, create columns for up to 4 actors (since that's the maximum in your data)
df[['Actor_1', 'Actor_2', 'Actor_3', 'Actor_4']] = df['Actors'].str.split(',', expand=True)

# Clean up the actor names by removing leading/trailing whitespace
actor_columns = ['Actor_1', 'Actor_2', 'Actor_3', 'Actor_4']
for col in actor_columns:
    df[col] = df[col].str.strip()

# Get unique actors from all actor columns
def get_unique_actors(df):
    actors = set()
    for col in ['Actor_1', 'Actor_2', 'Actor_3', 'Actor_4']:
        actors.update(df[col].dropna().unique())
    return sorted(actors)

unique_actors = get_unique_actors(df)

genres=['History', 'Musical', 'War', 'Comedy', 'Thriller', 'Sci-Fi', 'Drama', 'Action', 'Crime', 'Music', 'Sport', 'Mystery', 'Family', 'Biography', 'Adventure', 'Animation', 'Fantasy', 'Horror', 'Western', 'Romance']
years=set(df['Year'])

with tab3:
    st.subheader('Movie Genre Analysis')
    selected_genre=st.multiselect("Choose Genre's", genres)
    c=[]
    for i in selected_genre:
        p=df[df[i]==1]["Revenue (Millions)"].sum()
        c.append(p)

    def plot_genre_revenue(df, selected_genres):
    # Create a new dataframe with genre-specific revenues
        genre_data = []
    
        for genre in selected_genres:
            # Filter movies that contain the specific genre
            genre_movies = df[df['Genre'].str.contains(genre, na=False)]
            total_revenue = genre_movies['Revenue (Millions)'].sum()
            movie_count = len(genre_movies)
            
            genre_data.append({
                'Genre': genre,
                'Total Revenue': total_revenue,
                'Number of Movies': movie_count
            })
        
        genre_df = pd.DataFrame(genre_data)
        
        # Create bar plot
        fig = px.bar(
            genre_df,
            x='Genre',
            y='Total Revenue',
            title='Total Revenue by Genre',
            text='Number of Movies'  # Show number of movies on top of each bar
        )
        # Customize the text color and other properties

        # Customize the plot
        fig.update_traces(
            textfont=dict(
            color='red',  # Change text color to red
            size=12      # Optional: adjust text size
            ),
            texttemplate='%{text} movies',
            textposition='outside',
            hovertemplate="Genre: %{x}<br>Total Revenue: $%{y:.2f}M<br>Movies: %{text}<extra></extra>"
        )
        
        fig.update_layout(
            plot_bgcolor='white',
            xaxis_title="Genre",
            yaxis_title="Total Revenue (Millions $)",
            yaxis=dict(tickprefix='$', ticksuffix='M')
        )
        
        return fig

    def mai():
        
        # Create and display the plot if genres are selected
        if selected_genre:
            revenue_fig = plot_genre_revenue(df, selected_genre)
            st.plotly_chart(revenue_fig, use_container_width=True)
        else:
            st.warning("Please select at least one genre to see the revenue analysis.")

    if __name__ == "__main__":
        mai()  
#THE LINE CHART
    def create_rating_trend(df):
    # Calculate average rating per year
        yearly_ratings = df.groupby('Year')['Rating'].agg([
            ('Average Rating', 'mean'),
            ('Number of Movies', 'count')
        ]).reset_index()
    
        # Create line chart using plotly
        fig = px.line(
            yearly_ratings,
            x='Year',
            y='Average Rating',
            markers=True,
            title='Average Movie Ratings by Year',
            labels={'Year': 'Year', 'Average Rating': 'Average Rating'},
        )
        
        # Customize the chart
        fig.update_traces(
            line_color='#1f77b4',
            marker=dict(size=10, symbol='circle'),
            hovertemplate="Year: %{x}<br>Average Rating: %{y:.2f}<extra></extra>"
        )
        
        fig.update_layout(
            hovermode='x unified',
            plot_bgcolor='white',
            xaxis=dict(
                gridcolor='lightgrey',
                tickmode='linear'
            ),
            yaxis=dict(
                gridcolor='lightgrey',
                range=[0, 10]  # Rating scale is typically 0-10
            )
        )
        
        return fig, yearly_ratings

    def main():
        
        # Create and display the rating trend chart
        st.header("Movie Rating Trends")
        fig, yearly_ratings = create_rating_trend(df)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display yearly statistics
        st.markdown("Yearly Statistics")
        st.dataframe(
            yearly_ratings.style.format({
                'Average Rating': '{:.2f}',
                'Number of Movies': '{:,.0f}'
            })
        )

    if __name__ == "__main__":
        main()
        
    def create_votes_revenue_scatter(df):
        fig = px.scatter(
            df,
            x="Votes",
            y="Revenue (Millions)",
            title="Movie Votes vs. Revenue",
            labels={
                "Votes": "Number of Votes",
                "Revenue (Millions)": "Revenue (Millions $)"
            },
            trendline="ols",  # Add linear regression line
            trendline_color_override="red"
        )

        fig.update_layout(
            plot_bgcolor='white',
            xaxis=dict(gridcolor='lightgrey'),
            yaxis=dict(gridcolor='lightgrey', tickprefix='$', ticksuffix='M')
        )

        return fig

    def create_top_directors_plot(df):
        # Count the number of movies per director
        director_counts = df.groupby('Director')['Title'].count().reset_index(name='Movie Count')

        # Sort and get the top 10 directors
        top_directors = director_counts.nlargest(10, 'Movie Count')

        fig = px.bar(
            top_directors,
            x='Director',
            y='Movie Count',
            title='Top 10 Directors by Number of Movies',
            labels={
                "Director": "Director",
                "Movie Count": "Number of Movies"
            }
        )

        fig.update_layout(
            plot_bgcolor='white',
            xaxis=dict(gridcolor='lightgrey'),
            yaxis=dict(gridcolor='lightgrey')
        )

        return fig

    def man():
        st.title("Movie Insights")

        st.header("Votes vs. Revenue Correlation")
        votes_revenue_plot = create_votes_revenue_scatter(df)
        st.plotly_chart(votes_revenue_plot, use_container_width=True)

        st.header("Top Directors by Number of Movies")
        top_directors_plot = create_top_directors_plot(df)
        st.plotly_chart(top_directors_plot, use_container_width=True)

    if __name__ == "__main__":
        man()
        

with tab4:
    st.header('Filter Options')

    with st.expander('Filter by Year'):
        selected_year=st.selectbox("Select Year", years)

         # Number of movies slider
        n_movies = st.slider(
            'Number of Movies to Display',
            min_value=1,
            max_value=30,
            value=5
        )

     # Filter movies by selected Year and sort by rating
        filtered_movies = df[df['Year']==selected_year].sort_values('Rating', ascending=False)

    # Display results
        st.subheader(f'Top {n_movies} Movies Released in {selected_year} Movies by Rating')
        # Show filtered movies
        for i, movie in filtered_movies.head(n_movies).iterrows():
            with st.container():
                st.markdown(f"""
                **{movie['Title']} ({movie['Year']})** - Rating: {movie['Rating']}/10
                - Director: {movie['Director']}
                - Description: {movie['Description']}
                - Runtime: {movie['Runtime (Minutes)']} minutes
                - Revenue: ${movie['Revenue (Millions)']}M
                ---
                """)

        # Show total count
        total_movies = len(filtered_movies)
        st.info(f'Total {selected_year} movies: {total_movies}')
 
    with st.expander("Filter by Genre"):

        # Genre selection dropdown
        selected_genre = st.selectbox(
            'Select Genre',
            genres
        )

        # Number of movies slider
        n_movies = st.slider(
            'Number of Movies to display',
            min_value=1,
            max_value=30,
            value=5
        )

         # Filter movies by selected genre and sort by rating
        filtered_movies = df[df[f'{selected_genre}'] == 1].sort_values('Rating', ascending=False)


        # Display results
        st.subheader(f'Top {n_movies} {selected_genre} Movies by Rating')
        # Show filtered movies
        for i, movie in filtered_movies.head(n_movies).iterrows():
            with st.container():
                st.markdown(f"""
                **{movie['Title']} ({movie['Year']})** - Rating: {movie['Rating']}/10
                - Director: {movie['Director']}
                - Description: {movie['Description']}
                - Runtime: {movie['Runtime (Minutes)']} minutes
                - Revenue: ${movie['Revenue (Millions)']}M
                ---
                """)

        # Show total count
        total_genre_movies = len(filtered_movies)
        st.info(f'Total {selected_genre} movies: {total_genre_movies}')


    with st.expander('Filter By Actors'):

        st.header('Select Actors and Number of Movies')

        # Multiple actor selection
        selected_actors = st.multiselect(
            'Select up to 4 actors',
            options=unique_actors,
            max_selections=4
        )

        # Number of movies to display
        n_movies = st.slider(
            'Number of Movies to Display',
            min_value=1,
            max_value=20,
            value=5
        )

        if selected_actors:
            # Filter movies that have any of the selected actors
            mask = df['Actor_1'].isin(selected_actors) | \
                df['Actor_2'].isin(selected_actors) | \
                df['Actor_3'].isin(selected_actors) | \
                df['Actor_4'].isin(selected_actors)
            
            filtered_movies = df[mask].sort_values('Rating', ascending=False)
            
            if len(filtered_movies) == 0:
                st.error('No Such Movie Exists')
            else:
                st.subheader(f'Top Movies starring {", ".join(selected_actors)}')
                
                # Display movies
                movies_shown = 0
                for i, movie in filtered_movies.iterrows():
                    if movies_shown < n_movies:
                        # Get all actors in this movie
                        movie_actors = [movie['Actor_1'], movie['Actor_2'], 
                                    movie['Actor_3'], movie['Actor_4']]
                        # Highlight selected actors in the cast
                        cast = []
                        for actor in movie_actors:
                            if pd.notna(actor):
                                if actor in selected_actors:
                                    cast.append(f"**{actor}**")
                                else:
                                    cast.append(actor)
                        
                        st.markdown(f"""
                        #### {movie['Title']} ({movie['Year']})
                        - Rating: {movie['Rating']}/10
                        - Director: {movie['Director']}
                        - Cast: {', '.join(cast)}
                        - Description: {movie['Description']}
                        - Genre: {movie['Genre']}
                        - Revenue: ${movie['Revenue (Millions)']}M
                        ---
                        """)
                        movies_shown += 1
                    else:
                        break
                
                if movies_shown < n_movies:
                    st.warning(f'More Movies with these actors do not exist. Showing all {movies_shown} available movies.')
                
                # Show total count in sidebar
                st.info(f'Total movies found: {len(filtered_movies)}')
        else:
            st.info('Please select at least one actor to see their movies.')
