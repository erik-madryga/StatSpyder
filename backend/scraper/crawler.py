from __future__ import annotations

from typing import Optional, List

from bs4 import BeautifulSoup
from pydantic import BaseModel
import json


class PlayerSeason(BaseModel):
	year: int
	age: Optional[int]
	team: Optional[str]
	league: Optional[str]
	pos: Optional[str]
	games: Optional[int]
	games_started: Optional[int]
	targets: Optional[int]
	rec: Optional[int]
	rec_yds: Optional[int]
	rec_yds_per_rec: Optional[float]
	rec_td: Optional[int]
	catch_pct: Optional[float]
	yds_from_scrimmage: Optional[int]
	rush_att: Optional[int]
	rush_yds: Optional[int]
	fumbles: Optional[int]
	av: Optional[int]
	awards: Optional[str]


def _get_cell_text(row, data_stat: str) -> Optional[str]:
	el = row.select_one(f"[data-stat=\"{data_stat}\"]")
	if not el:
		return None
	txt = el.get_text(separator=" ", strip=True)
	return txt if txt != "" else None


def _int_or_none(s: Optional[str]) -> Optional[int]:
	if s is None:
		return None
	try:
		return int(s.replace(",", ""))
	except (ValueError, AttributeError):
		return None


def _float_or_none(s: Optional[str]) -> Optional[float]:
	if s is None:
		return None
	try:
		cleaned = s.replace("%", "").replace(",", "")
		return float(cleaned)
	except (ValueError, AttributeError):
		return None


def parse_receiving_and_rushing_tag(row) -> Optional[PlayerSeason]:
	"""Parse a BeautifulSoup `tr` Tag for receiving_and_rushing stats."""

	year_s = _get_cell_text(row, "year_id")
	# year is required
	year = _int_or_none(year_s)
	if year is None:
		return None

	age = _int_or_none(_get_cell_text(row, "age"))
	team = _get_cell_text(row, "team_name_abbr")
	league = _get_cell_text(row, "comp_name_abbr")
	pos = _get_cell_text(row, "pos")
	games = _int_or_none(_get_cell_text(row, "games"))
	games_started = _int_or_none(_get_cell_text(row, "games_started"))
	targets = _int_or_none(_get_cell_text(row, "targets"))
	rec = _int_or_none(_get_cell_text(row, "rec"))
	rec_yds = _int_or_none(_get_cell_text(row, "rec_yds"))
	rec_yds_per_rec = _float_or_none(_get_cell_text(row, "rec_yds_per_rec"))
	rec_td = _int_or_none(_get_cell_text(row, "rec_td"))
	catch_pct = _float_or_none(_get_cell_text(row, "catch_pct"))
	yds_from_scrimmage = _int_or_none(_get_cell_text(row, "yds_from_scrimmage"))
	rush_att = _int_or_none(_get_cell_text(row, "rush_att"))
	rush_yds = _int_or_none(_get_cell_text(row, "rush_yds"))
	fumbles = _int_or_none(_get_cell_text(row, "fumbles"))
	av = _int_or_none(_get_cell_text(row, "av"))

	# awards: prefer anchor texts joined by comma, fallback to plain text
	awards_el = row.select_one("[data-stat=awards]")
	awards = None
	if awards_el:
		anchors = [a.get_text(strip=True) for a in awards_el.select("a") if a.get_text(strip=True)]
		if anchors:
			awards = ",".join(anchors)
		else:
			txt = awards_el.get_text(separator=",", strip=True)
			awards = txt if txt != "" else None

	return PlayerSeason(
		year=year,
		age=age,
		team=team,
		league=league,
		pos=pos,
		games=games,
		games_started=games_started,
		targets=targets,
		rec=rec,
		rec_yds=rec_yds,
		rec_yds_per_rec=rec_yds_per_rec,
		rec_td=rec_td,
		catch_pct=catch_pct,
		yds_from_scrimmage=yds_from_scrimmage,
		rush_att=rush_att,
		rush_yds=rush_yds,
		fumbles=fumbles,
		av=av,
		awards=awards,
	)


def parse_receiving_and_rushing_row(html_content: str) -> Optional[PlayerSeason]:
	"""
	Parse a single `<tr>` row of receiving_and_rushing stats and return a `PlayerSeason`.

	The function is defensive: missing optional fields are set to None. If the
	required `year` value cannot be parsed, the function returns None.
	"""
	soup = BeautifulSoup(html_content, "html.parser")
	row = soup.select_one("tr")
	if row is None:
		return None
	return parse_receiving_and_rushing_tag(row)


def parse_receiving_and_rushing_table(html_content: str, row_selector: Optional[str] = None) -> List[PlayerSeason]:
	"""Parse a full HTML table (or fragment) and return a list of PlayerSeason.

	row_selector defaults to rows with ids starting with `receiving_and_rushing`.
	"""
	soup = BeautifulSoup(html_content, "html.parser")
	selector = row_selector or "tr[id^=\"receiving_and_rushing\"]"
	rows = soup.select(selector)
	results: List[PlayerSeason] = []
	for r in rows:
		parsed = parse_receiving_and_rushing_tag(r)
		if parsed:
			results.append(parsed)
	return results


if __name__ == "__main__":
	# quick local test using the provided snippet
	sample = (
		'<tr id="receiving_and_rushing.2020" data-row="0"> '
		'<th scope="row" class="left " data-stat="year_id" csk="2020"><a href="/players/J/JeffJu00/gamelog/2020/">2020</a><span class="sr_star"></span></th> '
		'<td class="right " data-stat="age">21</td> '
		'<td class="left " data-stat="team_name_abbr"><a href="/teams/min/2020.htm">MIN</a></td> '
		'<td class="left " data-stat="comp_name_abbr"><a href="/years/2020/">NFL</a></td> '
		'<td class="left " data-stat="pos">WR</td> '
		'<td class="right " data-stat="games">16</td> '
		'<td class="right " data-stat="games_started">14</td> '
		'<td class="right " data-stat="targets">125</td> '
		'<td class="right " data-stat="rec">88</td> '
		'<td class="right " data-stat="rec_yds">1400</td> '
		'<td class="right " data-stat="rec_yds_per_rec" csk="15.9090909091">15.9</td> '
		'<td class="right " data-stat="rec_td">7</td> '
		'<td class="right " data-stat="rec_first_down">58</td> '
		'<td class="right " data-stat="rec_success" csk="0.6160000000">61.6</td> '
		'<td class="right " data-stat="rec_long">71</td> '
		'<td class="right " data-stat="rec_per_g" csk="5.5000000000">5.5</td> '
		'<td class="right " data-stat="rec_yds_per_g" csk="87.5000000000">87.5</td> '
		'<td class="right " data-stat="catch_pct" csk="0.7040000000">70.4</td> '
		'<td class="right " data-stat="rec_yds_per_tgt" csk="11.2000000000">11.2</td> '
		'<td class="right " data-stat="rush_att">1</td> '
		'<td class="right " data-stat="rush_yds">2</td> '
		'<td class="right iz" data-stat="rush_td">0</td> '
		'<td class="right iz" data-stat="rush_first_down">0</td> '
		'<td class="right iz" data-stat="rush_success" csk="0.0000000000">0.0</td> '
		'<td class="right " data-stat="rush_long">2</td> '
		'<td class="right " data-stat="rush_yds_per_att" csk="2.0000000000">2.0</td> '
		'<td class="right " data-stat="rush_yds_per_g" csk="0.1250000000">0.1</td> '
		'<td class="right " data-stat="rush_att_per_g" csk="0.0625000000">0.1</td> '
		'<td class="right " data-stat="touches">89</td> '
		'<td class="right " data-stat="yds_per_touch" csk="15.7528089888">15.8</td> '
		'<td class="right " data-stat="yds_from_scrimmage">1402</td> '
		'<td class="right " data-stat="rush_receive_td">7</td> '
		'<td class="right " data-stat="fumbles">1</td> '
		'<td class="right " data-stat="av">13</td> '
		'<td class="left " data-stat="awards"><a href="/years/2020/probowl.htm">PB</a>,<a href="/years/2020/allpro.htm">AP-2</a>,<a href="/awards/awards_2020.htm">AP ORoY-2</a></td> '
		'</tr>'
	)

	parsed = parse_receiving_and_rushing_row(sample)
	if parsed:
		try:
			dumpable = parsed.model_dump()
		except AttributeError:
			dumpable = parsed.dict()
		print(json.dumps(dumpable, indent=2))
	else:
		print("Failed to parse row")

