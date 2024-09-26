import xml.etree.cElementTree as ET
import xml.dom.minidom
from pathlib import Path

m_encoding = "UTF-8"


def create_album_xml(path: Path, album_data: dict):
    album = ET.Element("album")

    review = ET.SubElement(album, "review")
    outline = ET.SubElement(album, "outline")
    lockdata = ET.SubElement(album, "lockdata")
    lockdata.text = str(album_data.get("lockdata", "false")).lower()

    dateadded = ET.SubElement(album, "dateadded")
    dateadded.text = album_data.get("dateadded", "")

    title = ET.SubElement(album, "title")
    title.text = album_data.get("title", "")

    year = ET.SubElement(album, "year")
    year.text = str(album_data.get("year", ""))

    sorttitle = ET.SubElement(album, "sorttitle")
    sorttitle.text = album_data.get("sorttitle", "")

    runtime = ET.SubElement(album, "runtime")
    runtime.text = str(album_data.get("runtime", ""))

    art = ET.SubElement(album, "art")
    poster = ET.SubElement(art, "poster")
    poster.text = album_data.get("poster", "")

    track = ET.SubElement(album, "track")
    position = ET.SubElement(track, "position")
    position.text = str(album_data.get("track_position", ""))

    track_title = ET.SubElement(track, "title")
    track_title.text = album_data.get("track_title", "")

    duration = ET.SubElement(track, "duration")
    duration.text = album_data.get("track_duration", "")

    dom = xml.dom.minidom.parseString(ET.tostring(album))
    xml_string = dom.toprettyxml()
    part1, part2 = xml_string.split("?>")

    with open(path, "w") as xfile:
        xfile.write(part1 + 'encoding="{}"?>\n'.format(m_encoding) + part2)
        xfile.close()


# Example usage
