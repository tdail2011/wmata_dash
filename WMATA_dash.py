
from dash import Dash, dcc, html, Input, Output, callback
import requests
import warnings
from dotenv import dotenv_values

API_KEY = dotenv_values(".env")["WMATA_Personal_Primary"]
# Load the dataset  
station_codes = {
        "Ashburn": "N12",
        "L'Enfant Plaza Upper": "F03",
        "L'Enfant Plaza Lower": "D03",
        "Reston Town Center": "N07",
        "Suitland": "F10",
    }
url = "https://api.wmata.com/StationPrediction.svc/json/GetPrediction/"
hdr = {
        # Request headers
        "Cache-Control": "no-cache",
        "api_key": API_KEY,
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

@callback(
    Output(component_id='output-container-button', component_property='children'),
    Input(component_id='station-dropdown', component_property='value')
)

def callback_function(input_value):
    # Placeholder for any callback functions if needed in the future
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
                train_divs = []
                for group in list(
                    {d["Group"] for d in response_json["Trains"] if "Group" in d}
                    ):
                        train_divs.append(html.Div(children =
                            [html.Div(children=f"{train['Car']} car train on the {train['Line']} line, " + \
                            f"heading to {train['Destination']}, Departing in {train['Min']} minutes. ") 
                            for train in response_json["Trains"] if train["Group"] == group]))
                return html.Div(children=train_divs)
        except ValueError as e:
            print("Error parsing JSON response:", e)
        except KeyError as e:
            print("Key error in response data:", e)
        except Exception as e:
            print("An unexpected error occurred:", e)
        pass
# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
