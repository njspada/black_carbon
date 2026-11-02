# First Step: Narrow the Traffic Data to Vallejo

## Current priority

Inspect the PeMS traffic data and reduce it to **I-80 stations in the Vallejo area**, keeping eastbound and westbound traffic identifiable. The first milestone is a small traffic dataset whose locations and columns are understood.

Combining traffic with black carbon (BC) can come later. The available environmental data are minute-resolution BC measurements, sensor coordinates, and temperature. No additional weather data are needed for this initial task.

## What we know about the traffic file

The attachment recovered from the earlier conversation is **`d04_text_station_day_2026_09.txt`**. It contains daily records, although the conversation referred to hourly data. If a separate station-hour file is available, inspect it separately before using it for hourly comparisons.

Inspection of the recovered file found:

| Item | Result |
|---|---|
| Dates | September 1–30, 2026 |
| Size | 117,150 rows; 3,905 station IDs |
| Structure | 16 comma-separated columns, without a header |
| Apparent I-80 subset | 15,750 rows; 525 station IDs |
| I-80 direction codes | E and W |
| Station locations | Still need to be matched to station IDs |

The apparent I-80 subset uses the file's route field; column meanings should be checked against the PeMS file description before finalizing the filter. **I-80 alone does not mean Vallejo:** the file includes stations elsewhere along the freeway.

## Simple workflow

```text
PeMS traffic file
       |
Inspect columns, dates, and station IDs
       |
Filter to I-80
       |
Match station IDs to locations
       |
Keep verified Vallejo stations
       |
Save a smaller traffic file + station list
```

## Practical checklist

| Step | What to do | Done when… |
|---|---|---|
| 1. Understand the file | Confirm whether it is daily or hourly and label columns using the matching PeMS documentation. | Date, station ID, route, direction, station type, and traffic-count fields are understood. |
| 2. Isolate I-80 | Filter the route field and make a list of unique station IDs. | A smaller I-80 file and candidate station list are saved. |
| 3. Find station locations | Match candidate IDs to metadata or verified station details. | Each selected station has a documented location. |
| 4. Choose the Vallejo boundary | Mark the intended I-80 stretch on a map, using clear endpoints or a city boundary. | It is clear why each station is included or excluded. |
| 5. Save the Vallejo subset | Keep stations inside the chosen area, preserving direction and station type. Start with mainline stations for the freeway analysis. | A Vallejo traffic file and a short station lookup table are ready to inspect. |
| 6. Check one day | Look for duplicate station/date records, missing counts, and unexpected values. Keep quality fields if supplied. | One day's records can be explained and traced back to the original file. |

## If monthly station metadata are missing

Start with the easiest available option:

1. **A nearby month's PeMS metadata:** match station IDs and check that location, direction, and station type are consistent. Record the metadata date; do not assume stations never change.
2. **PeMS station pages or map:** look up candidate IDs and record their coordinates or clearly identified locations.
3. **Official Caltrans location information:** if a station has a county, route, and complete postmile reference, use [Caltrans Postmile Services](https://postmile.dot.ca.gov/) to help locate it.

Use a small lookup table:

| Station ID | Direction | Type | Location / coordinates | Source and date | Keep? |
|---|---|---|---|---|---|
| To be verified | — | — | — | — | — |

Leave uncertain stations out of the first subset until their locations are verified. The goal is a trustworthy small selection; a complete historical location database can wait.

## Three rules to keep the first pass correct

- **Keep stations separate.** Adding counts from consecutive freeway stations can count the same vehicles several times. Do not label that sum “total Vallejo traffic.”
- **Keep station types separate.** Mainline, ramp, and connector records should not be mixed into one total. Check the PeMS definitions for the type codes.
- **Respect the time interval.** Daily counts cannot reveal busy hours. Use actual hourly data for a later hourly BC comparison; do not divide daily counts by 24 to invent hourly observations.

## What comes after this

Once the Vallejo subset is understood, try **one day of overlapping hourly traffic and BC data**, then expand to five days if the match works. That later step will require checking timestamps and averaging valid BC minutes into hourly concentrations. Temperature can be included if its timestamps and location are suitable.

For now, there is no need to obtain wind, precipitation, or other weather data, build a statistical model, or automate the full history. Temperature alone would not account for all weather influences, so any early BC–traffic comparisons should remain descriptive.

**Immediate deliverable:** a verified Vallejo station list and a filtered traffic file—not yet a completed BC–traffic analysis.
