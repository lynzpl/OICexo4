import streamlit as st
from PIL import Image, ExifTags
import folium
from io import BytesIO
from streamlit_folium import folium_static

def display_image(image):
    """
    Affiche l'image téléchargée dans l'application Streamlit.

    Args:
        image: L'image à afficher (au format file-like object).
    """
    st.image(image, caption='Uploaded Image', use_column_width=True)

def get_exif_data(image):
    """
    Extrait les métadonnées EXIF de l'image.

    Args:
        image: L'image dont les métadonnées EXIF doivent être extraites (au format file-like object).

    Returns:
        dict: Un dictionnaire contenant les métadonnées EXIF de l'image.
    """
    exif_data = {}
    try:
        img = Image.open(image)  # Ouvrir l'image
        exif = img._getexif()  # Obtenir les métadonnées EXIF
        if exif is not None:
            for tag, value in exif.items():
                # Convertir les tags EXIF en noms lisibles
                exif_data[ExifTags.TAGS.get(tag, tag)] = value
    except Exception as e:
        st.error(f"Error: {e}")
    return exif_data

def display_map(lat, lon):
    """
    Crée une carte centrée sur les coordonnées fournies et ajoute un marqueur.

    Args:
        lat (float): Latitude pour centrer la carte.
        lon (float): Longitude pour centrer la carte.

    Returns:
        folium.Map: Un objet carte Folium avec un marqueur à la position spécifiée.
    """
    m = folium.Map(location=[lat, lon], zoom_start=12)  # Créer une carte centrée sur les coordonnées
    folium.Marker([lat, lon], popup='Current Location').add_to(m)  # Ajouter un marqueur à la position
    return m

def add_pois(map_obj, pois):
    """
    Ajoute des points d'intérêt (POI) sur la carte.

    Args:
        map_obj (folium.Map): La carte Folium sur laquelle ajouter les POI.
        pois (list): Une liste de dictionnaires contenant les informations des POI.
                     Chaque dictionnaire doit avoir les clés 'name', 'lat' et 'lon'.
    """
    for poi in pois:
        folium.Marker([poi['lat'], poi['lon']], popup=poi['name']).add_to(map_obj)  # Ajouter chaque POI à la carte

def main():
    """
    Fonction principale pour exécuter l'application Streamlit.
    """
    st.title("EXIF Metadata Editor")  # Titre de l'application

    # Upload image
    uploaded_file = st.file_uploader("cahtr.jpg", type="jpg")
    if uploaded_file is not None:
        image = Image.open(uploaded_file)  # Ouvrir l'image téléchargée
        display_image(uploaded_file)  # Afficher l'image
        exif_data = get_exif_data(uploaded_file)  # Extraire les métadonnées EXIF
        st.write("EXIF Data:", exif_data)  # Afficher les métadonnées EXIF

        # Modify EXIF data
        if st.button("Modify EXIF Data"):
            gps_lat = st.number_input("Enter Latitude", -90.0, 90.0, 0.0)  # Saisir la latitude
            gps_lon = st.number_input("Enter Longitude", -180.0, 180.0, 0.0)  # Saisir la longitude
            st.write(f"Updated GPS Coordinates: Latitude {gps_lat}, Longitude {gps_lon}")

            # Show GPS data on map
            if 'Latitude' in exif_data and 'Longitude' in exif_data:
                lat = exif_data.get('Latitude')  # Obtenir la latitude EXIF
                lon = exif_data.get('Longitude')  # Obtenir la longitude EXIF
                m = display_map(lat, lon)  # Créer une carte avec la position GPS EXIF
                folium_static(m)  # Afficher la carte dans Streamlit

        # Show POIs
        st.subheader("Points of Interest")
        # Liste des points d'intérêt (POI)
        pois = [
            {'name': 'Tour Eiffel', 'lat': 48.8584, 'lon': 2.2945},
            {'name': 'Grande Muraille de Chine', 'lat': 40.4319, 'lon': 116.5704},
            {'name': 'Machu Picchu', 'lat': -13.1631, 'lon': -72.5450},
            {'name': 'Sydney Opera House', 'lat': -33.8568, 'lon': 151.2153},
            {'name': 'Statue de la Liberté', 'lat': 40.6892, 'lon': -74.0445}
        ]
        poi_map = folium.Map(location=[pois[0]['lat'], pois[0]['lon']], zoom_start=2)  # Créer une carte centrée sur le premier POI
        add_pois(poi_map, pois)  # Ajouter tous les POI à la carte
        folium_static(poi_map)  # Afficher la carte avec les POI dans Streamlit

if __name__ == "__main__":
    main()  # Exécuter la fonction principale lorsque le script est lancé
