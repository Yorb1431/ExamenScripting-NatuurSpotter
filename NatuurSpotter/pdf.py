from io import BytesIO
import requests
from bs4 import BeautifulSoup
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
from datetime import datetime
import folium
import urllib.parse
import openai
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

# Get API key from environment variables
api_key = os.getenv('OPENROUTER_API_KEY') or os.getenv('OPENAI_API_KEY')

client = None
base_url = None
if api_key:
    if os.getenv('OPENROUTER_API_KEY'):
        base_url = "https://openrouter.ai/api/v1/"
    else:
        base_url = "https://api.openai.com/v1/"

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
        # Simple test call to check if the client is configured correctly
        # Note: This might still fail if the key is invalid or network issues
        if client.models.list():
            print("OpenAI client successfully initialized.")
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")

def get_beetle_image(species_info, species):
    """Get beetle image from species info or Wikipedia."""
    beetle_image = None
    
    # Define a User-Agent header to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # Try to get image from species info first
    if species_info.get('photo_link'):
        try:
            print(f"Attempting to get image from species info: {species_info['photo_link']}")
            resp = requests.get(species_info['photo_link'], timeout=10, headers=headers)
            print(f"Species info image request status: {resp.status_code}")
            if resp.status_code == 200:
                beetle_image = BytesIO(resp.content)
                print("Successfully got image from species info.")
        except Exception as e:
            print(f"Error getting image from species info: {e}")
    
    # If no image in species info, try to get from Wikipedia
    if not beetle_image:
        try:
            # Try Dutch Wikipedia first
            url_nl = f"https://nl.wikipedia.org/wiki/{species.replace(' ', '_')}"
            print(f"Attempting to get image from Dutch Wikipedia: {url_nl}")
            resp = requests.get(url_nl, timeout=10, headers=headers)
            print(f"Dutch Wikipedia request status: {resp.status_code}")
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Look for the first image in the infobox
            infobox = soup.select_one("table.infobox")
            if infobox:
                img = infobox.select_one("img")
                if img and img.get("src"):
                    img_url = f"https:{img['src']}" if img['src'].startswith("//") else img['src']
                    print(f"Found image URL in Dutch infobox: {img_url}")
                    # Modify image URL for full resolution if possible and add headers
                    if '/thumb/' in img_url:
                        img_url = img_url.replace('/thumb/', '/')
                        # Remove trailing resolution part (e.g., /330px-...) if present
                        img_url = img_url[:img_url.rfind('/') if '/' in img_url else None]
                    print(f"Attempting to download infobox image from: {img_url}")
                    resp = requests.get(img_url, timeout=10, headers=headers)
                    print(f"Dutch infobox image download status: {resp.status_code}")
                    if resp.status_code == 200:
                        beetle_image = BytesIO(resp.content)
                        print("Successfully got image from Dutch infobox.")
            
            # If no image in infobox, try the first image in the content
            if not beetle_image:
                img = soup.select_one("div#mw-content-text img")
                if img and img.get("src"):
                    img_url = f"https:{img['src']}" if img['src'].startswith("//") else img['src']
                    print(f"Found image URL in Dutch content: {img_url}")
                     # Modify image URL for full resolution if possible and add headers
                    if '/thumb/' in img_url:
                        img_url = img_url.replace('/thumb/', '/')
                        # Remove trailing resolution part (e.g., /330px-...) if present
                        img_url = img_url[:img_url.rfind('/') if '/' in img_url else None]
                    print(f"Attempting to download content image from: {img_url}")
                    resp = requests.get(img_url, timeout=10, headers=headers)
                    print(f"Dutch content image download status: {resp.status_code}")
                    if resp.status_code == 200:
                        beetle_image = BytesIO(resp.content)
                        print("Successfully got image from Dutch content.")
            
            # If still no image, try English Wikipedia
            if not beetle_image:
                url_en = f"https://en.wikipedia.org/wiki/{species.replace(' ', '_')}"
                print(f"Attempting to get image from English Wikipedia: {url_en}")
                resp = requests.get(url_en, timeout=10, headers=headers)
                print(f"English Wikipedia request status: {resp.status_code}")
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                
                # Look for the first image in the infobox
                infobox = soup.select_one("table.infobox")
                if infobox:
                    img = infobox.select_one("img")
                    if img and img.get("src"):
                        img_url = f"https:{img['src']}" if img['src'].startswith("//") else img['src']
                        print(f"Found image URL in English infobox: {img_url}")
                         # Modify image URL for full resolution if possible and add headers
                        if '/thumb/' in img_url:
                            img_url = img_url.replace('/thumb/', '/')
                            # Remove trailing resolution part (e.g., /330px-...) if present
                            img_url = img_url[:img_url.rfind('/') if '/' in img_url else None]
                        print(f"Attempting to download infobox image from: {img_url}")
                        resp = requests.get(img_url, timeout=10, headers=headers)
                        print(f"English infobox image download status: {resp.status_code}")
                        if resp.status_code == 200:
                            beetle_image = BytesIO(resp.content)
                            print("Successfully got image from English infobox.")
                        
                # If no image in infobox, try the first image in the content
                if not beetle_image:
                    img = soup.select_one("div#mw-content-text img")
                    if img and img.get("src"):
                        img_url = f"https:{img['src']}" if img['src'].startswith("//") else img['src']
                        print(f"Found image URL in English content: {img_url}")
                         # Modify image URL for full resolution if possible and add headers
                        if '/thumb/' in img_url:
                            img_url = img_url.replace('/thumb/', '/')
                            # Remove trailing resolution part (e.g., /330px-...) if present
                            img_url = img_url[:img_url.rfind('/') if '/' in img_url else None]
                        print(f"Attempting to download content image from: {img_url}")
                        resp = requests.get(img_url, timeout=10, headers=headers)
                        print(f"English content image download status: {resp.status_code}")
                        if resp.status_code == 200:
                            beetle_image = BytesIO(resp.content)
                            print("Successfully got image from English content.")
        except Exception as e:
            print(f"Error getting image from Wikipedia: {e}")
    
    if not beetle_image:
        print("Could not find a beetle image from any source.")

    return beetle_image

def get_seasonal_analysis(species, seasons, season_counts):
    """Get seasonal analysis using OpenAI API."""
    try:
        if not client:
            return "Geen seizoensanalyse beschikbaar (OpenAI API key niet gevonden)."
        
        prompt = f"""Analyzeer het seizoenspatroon van de {species} op basis van deze data:
        Seizoenen: {', '.join(seasons)}
        Aantallen: {', '.join([f'{k}: {v}' for k, v in season_counts.items()])}
        
        Geef een gedetailleerde analyse in het Nederlands van waarom dit patroon voorkomt, 
        inclusief biologische en ecologische factoren."""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Je bent een expert in insectenecologie en seizoenspatronen."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error getting seasonal analysis: {e}")
        return "Geen seizoensanalyse beschikbaar."

def get_rarity_status(species, description):
    """Determine rarity status based on a description using OpenAI API."""
    try:
        if not client:
            return "Geen zeldzaamheidstatus beschikbaar (OpenAI API key niet gevonden)."
        
        prompt = f"""Based on the following description of the {species} in Dutch, determine its rarity status in general terms (e.g., 'Zeer zeldzaam', 'Zeldzaam', 'Vrij algemeen', 'Algemeen'). Do not provide any other information.

        Description: {description}
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Using a suitable model for this task
            messages=[
                {"role": "system", "content": "You are an AI assistant that determines the rarity status of a species based on a provided description."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=20 # Keep the response concise
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error getting rarity status: {e}")
        return "Onbekend"

def create_seasonal_graph(species):
    """Create seasonal pattern graph based on LLM typical occurrence."""
    graph_img = BytesIO()
    plt.figure(figsize=(6, 4))
    
    seasonal_data = {}
    seasons_order = ['Spring', 'Summer', 'Autumn', 'Winter']
    
    # Get typical seasonal occurrence from LLM
    try:
        if client:
            prompt = f"""Provide the typical seasonal occurrence likelihood for the species {species} across the four seasons (Spring, Summer, Autumn, Winter) as a JSON object with season names as keys and percentage as values. Example: {{ \"Spring\": 20, \"Summer\": 60, \"Autumn\": 15, \"Winter\": 5 }}. If the species is not well-known or seasonal data is unavailable, provide {{ \"Spring\": 25, \"Summer\": 25, \"Autumn\": 25, \"Winter\": 25 }}. Do not include any other text.
            """
            print(f"Attempting to get seasonal occurrence from LLM for {species}")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo", # Or another suitable model
                messages=[
                    {"role": "system", "content": "You are an AI assistant that provides typical seasonal occurrence data for species in a specific JSON format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100, # Increase max_tokens slightly for JSON
                response_format={ "type": "json_object" } # Request JSON object format
            )
            seasonal_json_text = response.choices[0].message.content.strip()
            print(f"LLM seasonal JSON response: {seasonal_json_text}")
            
            # Parse the JSON response
            try:
                # Attempt to load JSON, handle potential leading/trailing non-JSON text
                # Find the first and last curly braces to isolate the JSON object
                json_start = seasonal_json_text.find('{')
                json_end = seasonal_json_text.rfind('}')
                if json_start != -1 and json_end != -1:
                    seasonal_json_text_cleaned = seasonal_json_text[json_start : json_end + 1]
                    seasonal_data_raw = json.loads(seasonal_json_text_cleaned)
                else:
                    raise json.JSONDecodeError("JSON object not found in LLM response", seasonal_json_text, 0)
                
                # Validate and format the parsed data
                if all(season in seasonal_data_raw and isinstance(seasonal_data_raw[season], (int, float)) for season in seasons_order):
                     seasonal_data = {season: max(0, float(seasonal_data_raw.get(season, 0))) for season in seasons_order} # Ensure non-negative floats
                     # Normalize percentages if total is not 100
                     total = sum(seasonal_data.values())
                     if total > 0:
                         seasonal_data = {season: (count / total) * 100 for season, count in seasonal_data.items()}
                     print("Successfully parsed LLM seasonal data.")
                else:
                    print(f"LLM returned unexpected JSON structure or values: {seasonal_data_raw}")
                    seasonal_data = dict(zip(seasons_order, [25, 25, 25, 25])) # Default if validation fails

            except json.JSONDecodeError as json_e:
                 print(f"Error decoding JSON from LLM seasonal data: {json_e}")
                 seasonal_data = dict(zip(seasons_order, [25, 25, 25, 25])) # Default on JSON error
            except Exception as parse_e:
                 print(f"Error parsing LLM seasonal data after JSON decode: {parse_e}")
                 seasonal_data = dict(zip(seasons_order, [25, 25, 25, 25])) # Default on other parsing error

        else:
             print("OpenAI client not initialized for seasonal data.")
             seasonal_data = dict(zip(seasons_order, [25, 25, 25, 25])) # Default if client fails

    except Exception as e:
        print(f"Error getting seasonal data from LLM: {e}")
        seasonal_data = dict(zip(seasons_order, [25, 25, 25, 25])) # Default on API error
    
    # Create a bar chart using the seasonal data
    seasons = list(seasonal_data.keys())
    counts = list(seasonal_data.values())

    if counts:
        try:
            sns.barplot(x=seasons, y=counts, palette='viridis', order=seasons_order) # Ensure correct order
            plt.title(f'Typisch Seizoenspatroon van {species}')
            plt.xlabel('Seizoen')
            plt.ylabel('Typische Waarnemingskans (%)')
            plt.ylim(0, 100)
        except Exception as e:
            print(f"Error creating seasonal graph: {e}")
            plt.text(0.5, 0.5, 'Fout bij het maken van de grafiek', ha='center', va='center')
    else:
        plt.text(0.5, 0.5, 'Geen data beschikbaar voor grafiek', ha='center', va='center')
    
    plt.tight_layout()
    plt.savefig(graph_img, format='png')
    plt.close()
    graph_img.seek(0)
    
    # We no longer return seasons and season_counts based on observation data here
    return graph_img, None, None

def generate_pdf(species, date, observer, species_info, observations):
    """Generate PDF report for a species."""
    try:
        # URL decode
        species = urllib.parse.unquote(species)
        observer = urllib.parse.unquote(observer)
        date = urllib.parse.unquote(date)
        
        # Get unique locations
        locations = set()
        for obs in observations:
            if obs.get('place'):
                locations.add(obs.get('place'))
            elif obs.get('location'):
                locations.add(obs.get('location'))
        
        # Get beetle image
        beetle_image = get_beetle_image(species_info, species)
        
        # Create seasonal graph (now based on LLM typical data)
        graph_img, _, _ = create_seasonal_graph(species)
        
        # Get seasonal analysis (still based on LLM but potentially using broader knowledge if prompt is adjusted)
        # For seasonal analysis text, let's call the LLM again with a prompt focused on explaining the typical pattern
        seasonal_analysis = "Geen seizoensanalyse beschikbaar."
        try:
            if client:
                prompt_analysis = f"""Leg in het Nederlands uit waarom de {species} typisch het meest wordt waargenomen in bepaalde seizoenen, gebaseerd op biologische en ecologische factoren. Baseer je antwoord op algemene kennis over deze soort en kevers in vergelijkbare habitats.\n\nTypische seizoensdistributie (dit is input voor jou, baseer je uitleg hierop): Spring, Summer, Autumn, Winter. Aantallen/kansen zijn verkregen uit een ander model. Focus op de *redenen* achter het patroon, niet op de exacte percentages.\n"""
                response_analysis = client.chat.completions.create(
                    model="gpt-3.5-turbo", # Or another suitable model
                    messages=[
                        {"role": "system", "content": "Je bent een expert in insectenecologie en seizoenspatronen en geeft uitleg over seizoenspatronen van kevers."},
                        {"role": "user", "content": prompt_analysis}
                    ]
                )
                seasonal_analysis = response_analysis.choices[0].message.content.strip()
            else:
                print("OpenAI client not initialized for seasonal analysis.")
        except Exception as e:
            print(f"Error getting seasonal analysis from LLM: {e}")

        # Get rarity status
        rarity_status = get_rarity_status(species, species_info.get('description', ''))
        
        # Create PDF
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Title
        elements.append(Paragraph(f"<b>{species}</b>", styles['Title']))
        if species_info.get('latin_name'):
            elements.append(Paragraph(f"<i>{species_info['latin_name']}</i>", styles['Italic']))
        elements.append(Spacer(1, 12))
        
        # Rarity Status
        elements.append(Paragraph("<b>Zeldzaamheidstatus</b>", styles['Heading3']))
        elements.append(Paragraph(rarity_status, styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Beetle Image
        if beetle_image:
            try:
                print("Attempting to add beetle image to PDF elements.")
                elements.append(Image(beetle_image, width=300, height=225))
                elements.append(Spacer(1, 12))
                print("Successfully added beetle image to PDF elements.")
            except Exception as e:
                print(f"Error adding image to PDF: {e}")
        else:
            print("No beetle image available to add to PDF.")
        
        # Description
        if species_info.get('description'):
            elements.append(Paragraph("<b>Beschrijving</b>", styles['Heading3']))
            elements.append(Paragraph(species_info['description'], styles['Normal']))
            elements.append(Spacer(1, 12))
        
        # Locations
        if locations:
            elements.append(Paragraph("<b>Gevonden in</b>", styles['Heading3']))
            for location in sorted(locations):
                elements.append(Paragraph(f"• {location}", styles['Normal']))
            elements.append(Spacer(1, 12))
        
        # Seasonality
        elements.append(Paragraph("<b>Seizoenspatroon</b>", styles['Heading3']))
        try:
            # Adjusted width for better bar chart display
            elements.append(Image(graph_img, width=450, height=300))
            elements.append(Spacer(1, 12))
        except Exception as e:
            print(f"Error adding graph to PDF: {e}")
        
        # Seasonal Analysis
        elements.append(Paragraph("<b>Seizoensanalyse</b>", styles['Heading3']))
        elements.append(Paragraph(seasonal_analysis, styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        pdf_buffer.seek(0)
        
        # Save PDF to output directory
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        filename = f"{species}.pdf"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        return pdf_buffer, filename
    except Exception as e:
        print(f"Error generating PDF: {e}")
        # Create a simple error PDF
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = [
            Paragraph("Er is een fout opgetreden bij het genereren van het PDF rapport.", styles['Title']),
            Spacer(1, 12),
            Paragraph(f"Foutmelding: {str(e)}", styles['Normal'])
        ]
        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer, f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf" 