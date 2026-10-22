## Project setup (21/22-10-2026)
 - used uv for dependency management and src layout (avoid using pip and requirements in my projects in generall)
   makefile already ready (methods are up, down, ingest, transform, test, lint - typical stuff)

## About the API
 - Old GIOS endpoints ar depracated and being retired -> will be using the new GIOS API page.
 - GIOS API is documented in polish , I need to map correctly the parameters with eng terminology regarding scientific measurements on air pollution
 - copied a list of the stations in tests/fixtures folder called gios_stations, found out by parsing the json with jq that the total pages returned by the api  call were 15 (important for the ingester pagination), revised the json object structure to indentify the relevant keys I will need going forward.
- api rates 1500req/min for measurements
## Time zones
GIOŚ current data: bare local time (Europe/Warsaw), no offset, newest first.
Open-Meteo: UTC (requested with timezone=GMT).
Staging converts GIOŚ times to UTC. On the October DST change the 02:00 local
hour appears twice; 