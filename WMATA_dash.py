
# WMATA_dash.py
# This script creates a Dash application that displays the next train information
# from the Washington Metropolitan Area Transit Authority (WMATA) API.
# It allows users to select a station from a dropdown menu and fetches the next train
# information for that station using the WMATA Next Train API.

from dash import Dash, dcc, html, Input, Output, callback
import requests
import warnings
from dotenv import dotenv_values

API_KEY = dotenv_values(".env")["WMATA_Personal_Primary"]


def create_output_line(train):
    """ Create a Dash HTML component for a single train's information.
    Args:
        train (dict): A dictionary containing train information.
    Returns:
        html.Div: A Dash HTML component containing the train information.
    """
    return html.Div(children=f"{train['Car']} car train on the {train['Line']} line, " +
                        f"heading to {train['DestinationName']}, departing in {train['Min']} minutes. ")


def create_output_group(response_json, group):
    """ Create a Dash HTML component for a group of trains.
    Args:
        response_json (dict): The JSON response from the WMATA API containing train data.
        group (str): The group identifier for the trains.
    Returns:
        html.Div: A Dash HTML component containing the grouped train information.
    """
    # Create a list of HTML components for each train in the group
    return html.Div(children=[*
                        [create_output_line(train) for train in response_json["Trains"] 
                         if train["Group"] == group], html.Br()])

# Define the station codes for the dropdown menu
# These codes are used to query the WMATA Next Train API for specific stations.
station_codes = {
        "Ashburn": "N12",
        "L'Enfant Plaza Upper": "F03",
        "L'Enfant Plaza Lower": "D03",
        "Reston Town Center": "N07",
        "Suitland": "F10",
        }

# Define external stylesheets for the Dash app
external_stylesheets = [
    "https://codepen.io/chriddyp/pen/bWLwgP.css"]
# Initialize the Dash app
app = Dash(__name__, external_stylesheets=external_stylesheets)
# Define the layout of the app
text = ("This is a simple Dash application powered by the WMATA Next Train API.")

app.layout = html.Div(
    children=[
        html.H1(children='WMATA Next Train Dashboard'),
        html.Div(children=text),
        html.Div(children=[
            dcc.Dropdown(["Select a station"] + list(station_codes.keys()),
                placeholder="Select a station", id='station-dropdown',
                style={'width': '48%', 'float': 'left', 'display': 'grid'}),
            html.Div(id='output-container-button', 
                style={'width': '48%', 'float': 'right', 'display': 'grid'}),
                    ]
            ),
        ]
    )

# Define the callback function to update the output based on the selected station.
@callback(
    Output(component_id='output-container-button', component_property='children'),
    Input(component_id='station-dropdown', component_property='value')
)

def callback_function(input_value, station_codes=station_codes):
    """ Callback function to fetch and display the next train information
    based on the selected station from the dropdown.
    Args:
        input_value (str): The selected station from the dropdown.
    Returns:
        html.Div: A Dash HTML component containing the next train information.
    """
    # URL for the WMATA Next Train API
    url = "https://api.wmata.com/StationPrediction.svc/json/GetPrediction/"
    # Set up headers for the request
    hdr = {
            "Cache-Control": "no-cache",
            "api_key": API_KEY,
        }
    station = input_value
    if station is None or station == "Select a station":
        return "Please select a station to get the next train information."
    else:
        try:
            # print("Trying secured")
            response = requests.get(
                url + station_codes[station],
                headers=hdr,
            )
        except requests.RequestException as ex:
            try:
                print(ex)
                print("trying unsecured")
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    response = requests.get(
                        url + station_codes[station], headers=hdr, verify=False
                    )
            except Exception as e:
                print(e)
        try: 
            response_json = response.json()
            if response.status_code != 200:
                print(
                    f"Error fetching data for {station}. "
                    f"Status code: {response.status_code}"
                )
                return
            elif "Trains" not in response_json:
                print("No train data available for this station.")
                return f"No train data available for this station."
            else:
                # Get sorted unique groups
                groups = sorted({d["Group"] for d in response_json["Trains"] if "Group" in d})

                # List comprehension to create output lines and separate groups with html.Br()
                # output is a list of html.Div and html.Br elements, ready for Dash
                return html.Div(children=[create_output_group(response_json, group)
                    for group in groups
                ])
        except ValueError as e:
            print("Error parsing JSON response:", e)
            return e
        except KeyError as e:
            print("Key error in response data:", e)
            return e
        except Exception as e:
            print("An unexpected error occurred:", e)
            return e
        
# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
