from .classes import *
from icalendar import Calendar, Event
from datetime import datetime


def export(output_file, tmp_file="ex.json"):
    # Load your export
    t = load_interventions_export(tmp_file)

    # Initialize the calendar
    cal = Calendar()
    cal.add("prodid", "-//EASE by antonin.verdier@epita.fr")
    cal.add("version", "2.0")

    for i in t.interventions:
        iType = i.activityType.code

        # Parse start and end times (adjust if your format differs from ISO)
        iStart = i.startDateTime
        iEnd = i.endDateTime
        iUid = f"EASE-{i.id}"

        if i.interventionPedagogicalUnits is not None:
            pedagogicalUnit = i.interventionPedagogicalUnits[0]["pedagogicalUnit"]
            iName = pedagogicalUnit["caption"]["fr"]
            iCode = pedagogicalUnit["code"]
        else:
            iName = i.description
            iCode = "N/A"

        resource = i.interventionResources[0]
        iRoom = resource["resource"]["caption"]["fr"]

        # Create a new calendar event
        event = Event()
        event.add("summary", f"[{iType}] {iName} ({iCode})")
        event.add("dtstart", iStart)
        event.add("dtend", iEnd)
        event.add("location", iRoom)
        event.add("description", f"Activity Type: {iType}\nCode: {iCode}")
        event.add('uid', iUid)

        # Add the event to the calendar
        cal.add_component(event)

    # Write the calendar to an .ics file
    with open(output_file, "wb") as f:
        f.write(cal.to_ical())

    print(f"Successfully generated {output_file}!")
