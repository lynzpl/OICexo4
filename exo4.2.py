import streamlit as st
from PIL import Image, ExifTags
import io
import folium
from streamlit_folium import folium_static

def get_exif_data(image):
    """
    Extrait les métadonnées EXIF de l'image.

    Args:
        image: L'image dont les métadonnées EXIF doivent être extraites.

    Returns:
        dict: Un dictionnaire contenant les métadonnées EXIF de l'image.
    """
    exif_data = {}
    try:
        img = Image.open(image)
        exif = img._getexif()
        if exif is not None:
            for tag, value in exif.items():
                tag_name = ExifTags.TAGS.get(tag, tag)
                exif_data[tag_name] = value
    except Exception as e:
        st.error(f"Error: {e}")
    return exif_data

def update_exif_data(image, updated_exif):
    """
    Met à jour les métadonnées EXIF de l'image avec les nouvelles valeurs.

    Args:
        image: L'image à mettre à jour.
        updated_exif: Un dictionnaire avec les nouvelles valeurs EXIF.

    Returns:
        Image: L'image mise à jour avec les nouvelles métadonnées EXIF.
    """
    img = Image.open(image)
    exif = img._getexif()
    if exif is not None:
        for tag_name, value in updated_exif.items():
            tag_id = [k for k, v in ExifTags.TAGS.items() if v == tag_name]
            if tag_id:
                tag_id = tag_id[0]
                exif[int(tag_id)] = value
    img.info['exif'] = exif
    return img

def display_map(lat, lon):
    """
    Crée une carte centrée sur les coordonnées fournies et ajoute un marqueur.

    Args:
        lat (float): Latitude pour centrer la carte.
        lon (float): Longitude pour centrer la carte.

    Returns:
        folium.Map: Un objet carte Folium avec un marqueur à la position spécifiée.
    """
    m = folium.Map(location=[lat, lon], zoom_start=12)
    folium.Marker([lat, lon], popup='Current Location').add_to(m)
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
        folium.Marker([poi['lat'], poi['lon']], popup=poi['name']).add_to(map_obj)

def main():
    """
    Fonction principale pour exécuter l'application Streamlit.
    """
    st.title("EXIF Metadata Editor")

    # Upload image
    uploaded_file = st.file_uploader("Choose an image...", type="jpg")
    if uploaded_file is not None:
        # Affichage de l'image téléchargée
        st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)
        
        # Lire les métadonnées EXIF de l'image
        exif_data = get_exif_data(uploaded_file)
        st.write("Current EXIF Data:", exif_data)
        
        # Formulaire pour modifier les données EXIF
        st.subheader("Edit EXIF Data")
        
        with st.form(key='edit_exif'):
            date_time = st.text_input("DateTime", value=exif_data.get("DateTime", ""))
            make = st.text_input("Make (Camera Manufacturer)", value=exif_data.get("Make", ""))
            model = st.text_input("Model (Camera Model)", value=exif_data.get("Model", ""))
            exposure_time = st.text_input("Exposure Time", value=exif_data.get("ExposureTime", ""))
            f_number = st.text_input("F Number", value=exif_data.get("FNumber", ""))
            iso = st.text_input("ISO", value=exif_data.get("ISOSpeedRatings", ""))
            gps_lat = st.text_input("GPS Latitude", value=str(exif_data.get("GPSLatitude", "")))
            gps_lon = st.text_input("GPS Longitude", value=str(exif_data.get("GPSLongitude", "")))
            gps_lat_ref = st.selectbox("GPS Latitude Ref", ["N", "S"], index=["N", "S"].index(exif_data.get("GPSLatitudeRef", "N")))
            gps_lon_ref = st.selectbox("GPS Longitude Ref", ["E", "W"], index=["E", "W"].index(exif_data.get("GPSLongitudeRef", "E")))
            
            # Submit button
            submit_button = st.form_submit_button("Update EXIF Data")
            
            if submit_button:
                updated_exif = {
                    "DateTime": date_time,
                    "Make": make,
                    "Model": model,
                    "ExposureTime": exposure_time,
                    "FNumber": f_number,
                    "ISOSpeedRatings": iso,
                    "GPSLatitude": gps_lat,
                    "GPSLongitude": gps_lon,
                    "GPSLatitudeRef": gps_lat_ref,
                    "GPSLongitudeRef": gps_lon_ref
                }
                
                # Mise à jour des métadonnées EXIF
                updated_image = update_exif_data(uploaded_file, updated_exif)
                
                # Afficher l'image mise à jour
                buf = io.BytesIO()
                updated_image.save(buf, format="JPEG")
                buf.seek(0)
                st.image(buf, caption='Updated Image', use_column_width=True)
                st.success("EXIF Data updated successfully")
                
                # Afficher la nouvelle position GPS sur la carte
                try:
                    lat = float(gps_lat)
                    lon = float(gps_lon)
                    m = display_map(lat, lon)
                    folium_static(m)
                except ValueError:
                    st.error("Invalid GPS coordinates")

        # Afficher les POI
        st.subheader("Points of Interest")
        pois = [
            {'name': 'Tour Eiffel', 'lat': 48.8584, 'lon': 2.2945},
            {'name': 'Grande Muraille de Chine', 'lat': 40.4319, 'lon': 116.5704},
            {'name': 'Machu Picchu', 'lat': -13.1631, 'lon': -72.5450},
            {'name': 'Sydney Opera House', 'lat': -33.8568, 'lon': 151.2153},
            {'name': 'Statue de la Liberté', 'lat': 40.6892, 'lon': -74.0445}
        ]
        poi_map = folium.Map(location=[pois[0]['lat'], pois[0]['lon']], zoom_start=2)
        add_pois(poi_map, pois)
        folium_static(poi_map)

if __name__ == "__main__":
    main()

