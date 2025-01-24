from dataclasses import dataclass
from espn_api import football

from environs import Env


@dataclass
class EspnSettings:
    espn_s2: str
    swid: str
    league_id: int
    year: int


def high_scores_by_week(league: football.League):
    print("High Scores by Week")
    print("-------------------")
    for week in range(0, 16):
        high_score = 0
        high_team = None
        for team in league.teams:
            score = team.scores[week]
            if score > high_score:
                high_score = score
                high_team = team
        print(f"week {week + 1}: {high_team.team_name} scored {high_score}")


def higest_score_of_season(league: football.League):
    print("Highest Score of the Season")
    print("---------------------------")
    high_score = 0
    high_team = None
    high_week = None
    for team in league.teams:
        for week in range(0, 16):
            score = team.scores[week]
            if score > high_score:
                high_score = score
                high_team = team
                high_week = week

    print(f"{high_team.team_name} scored {high_score} in week {high_week + 1}")


def find_highest_total_points(league: football.League):
    print("Highest Total Points")
    print("--------------------")
    highest_points_for = 0
    for team in league.teams:
        if team.points_for > highest_points_for:
            highest_points_for = team.points_for
            highest_team = team

    print(f"{highest_team.team_name} has the most points for with {highest_points_for}")


def parse_settings_from_env():
    env = Env()
    env.read_env()
    return EspnSettings(
        espn_s2=env.str("ESPN_S2"),
        swid=env.str("SWID"),
        league_id=env.int("LEAGUE_ID"),
        year=env.int("YEAR"),
    )


def get_league(settings: EspnSettings):
    return football.League(
        league_id=settings.league_id,
        year=settings.year,
        espn_s2=settings.espn_s2,
        swid=settings.swid,
    )


if __name__ == "__main__":
    settings = parse_settings_from_env()
    league = get_league(settings)
    high_scores_by_week(league)
    print("\n")
    higest_score_of_season(league)
    print("\n")
    find_highest_total_points(league)
