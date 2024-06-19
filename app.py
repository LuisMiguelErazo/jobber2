import pandas as pd
import plotly.express as px
import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import zipfile

# Cargar el archivo CSV
with zipfile.ZipFile('map_skills.zip', 'r') as zipf:
    with zipf.open('map_skills.csv') as f:
        df = pd.read_csv(f)

# Título del Dashboard
st.title('Interactive Salary and Skills Dashboard')

# Filtros encadenados
categories = sorted(df['Category'].unique().tolist())
categories = ['All'] + categories
category = st.selectbox('Category', categories)

industries = df['Industry'].unique() if category == 'All' else df[df['Category'] == category]['Industry'].unique()
industries = ['All'] + sorted(industries.tolist())
industry = st.selectbox('Industry', industries)

experiences = df['Experience Level'].unique() if industry == 'All' else df[(df['Category'] == category) & (df['Industry'] == industry)]['Experience Level'].unique()
experiences = ['All'] + sorted(experiences.tolist())
experience = st.selectbox('Experience Level', experiences)

# Pestañas
tab1, tab2, tab3, tab4, tab5 = st.tabs(['Map', 'Salary by State', 'Key Skills', 'Salary Distribution', 'Salary Insights'])

def update_map(category, industry, experience):
    filtered_df = df.copy()
    if category != 'All':
        filtered_df = filtered_df[filtered_df['Category'] == category]
    if industry != 'All':
        filtered_df = filtered_df[filtered_df['Industry'] == industry]
    if experience != 'All':
        filtered_df = filtered_df[filtered_df['Experience Level'] == experience]

    state_salary = filtered_df.groupby('State').agg(
        Medium_Salary=('Medium Salary', 'mean'),
    ).reset_index()

    # Crear una columna formateada para los datos emergentes (hover)
    state_salary['Mean_Salary'] = state_salary['Medium_Salary'].map(lambda x: f"${x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    fig = px.choropleth(state_salary,
                        locations='State',
                        locationmode='USA-states',
                        color='Medium_Salary',
                        color_continuous_scale='Viridis',  # Mantener la paleta de colores original
                        scope='usa',
                        labels={'Medium_Salary': 'Medium Salary'},
                        hover_data={'State': True, 'Medium_Salary': False, 'Mean_Salary': True})
    fig.update_layout(title='Medium Salary by State', geo=dict(scope='usa'))
    st.plotly_chart(fig)

# Función para crear word cloud de habilidades clave
def plot_wordcloud(category):
    if category != 'All':
        filtered_df = df[df['Category'] == category]
        text = ' '.join(filtered_df['Soft Skill'].dropna().tolist())
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(f'Top Soft Skills in {category} Category')
        st.pyplot(plt)
    else:
        st.write('Select a Category to Display Word Cloud')

# Función para scatter plot de salarios por estado
def plot_salary_by_state(category, industry, experience):
    filtered_df = df.copy()
    if category != 'All':
        filtered_df = filtered_df[filtered_df['Category'] == category]
    if industry != 'All':
        filtered_df = filtered_df[filtered_df['Industry'] == industry]
    if experience != 'All':
        filtered_df = filtered_df[filtered_df['Experience Level'] == experience]

    fig = px.scatter(filtered_df, x='State', y='Medium Salary', size='Medium Salary',
                     hover_data=['State', 'Medium Salary'],
                     title='Medium Salary by State')
    st.plotly_chart(fig)

# Función para distribución de salarios
def plot_salary_distribution(category, industry):
    filtered_df = df.copy()
    if category != 'All':
        filtered_df = filtered_df[filtered_df['Category'] == category]
    if industry != 'All':
        filtered_df = filtered_df[filtered_df['Industry'] == industry]

    # Agrupar por 'Experience Level' y calcular el promedio de 'Medium Salary'
    grouped_df = filtered_df.groupby('Experience Level', as_index=False)['Medium Salary'].mean()

    # Crear el gráfico de barras con formato de número personalizado
    fig = px.bar(grouped_df, x='Experience Level', y='Medium Salary', color='Experience Level',
                 title='Salary Distribution by Experience Level')
    fig.update_traces(texttemplate='$%{y:,.2f}', textposition='outside')

    # Actualizar el eje y para tener el mismo formato
    fig.update_layout(yaxis_tickformat='$,.2f')

    st.plotly_chart(fig)

# Función para insights de salario
def plot_salary_insights(category):
    filtered_df = df.copy()
    if category != 'All':
        filtered_df = filtered_df[filtered_df['Category'] == category]

    fig = px.box(filtered_df, x='Category', y='Medium Salary',
                 title='Salary Insights by Category')
    st.plotly_chart(fig)

# Map tab
with tab1:
    update_map(category, industry, experience)

# Salary by State tab
with tab2:
    plot_salary_by_state(category, industry, experience)

# Key Skills tab
with tab3:
    plot_wordcloud(category)

# Salary Distribution tab
with tab4:
    plot_salary_distribution(category, industry)

# Salary Insights tab
with tab5:
    plot_salary_insights(category)
