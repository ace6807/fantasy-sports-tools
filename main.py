# A script to retrieve the users in a Sleeper fantasy football league

import os
import requests
import json


def get_league_info(league_id):
    league_endpoint = f"https://api.sleeper.app/v1/league/{league_id}"
    response = requests.get(league_endpoint)
    league_info = response.json()
    return league_info


def get_league_users(league_id):
    user_enpoint = f"https://api.sleeper.app/v1/league/{league_id}/users"
    response = requests.get(user_enpoint)
    users = response.json()
    return users


def get_league_rosters(league_id):
    rosters_endpoint = f"https://api.sleeper.app/v1/league/{league_id}/rosters"
    response = requests.get(rosters_endpoint)
    rosters = response.json()
    return rosters


def add_roster_info_to_user_dict(user_dict, rosters):
    for roster in rosters:
        user_id = roster["owner_id"]
        roster_id = roster["roster_id"]
        user_dict[user_id]["roster_id"] = roster_id
    return user_dict


def parse_user_info(users):
    user_dict = {}
    for user in users:
        user_id = user["user_id"]
        display_name = user["display_name"]
        team_name = user["metadata"].get("team_name")
        user_dict[user_id] = {"display_name": display_name, "team_name": team_name}
    return user_dict


def get_week_matchups(league_id, week):
    matchups_endpoint = f"https://api.sleeper.app/v1/league/{league_id}/matchups/{week}"
    response = requests.get(matchups_endpoint)
    matchups = response.json()
    return matchups


def get_week_scores(league_id, week):
    matchups = get_week_matchups(league_id, week)
    scores = {}
    for matchup in matchups:
        scores[matchup["roster_id"]] = matchup["points"]

    return scores


def get_stats(user_dict):
    # get the top overall scorer
    top_scorer = max(user_dict, key=lambda x: user_dict[x]["total_points"])
    top_scorer_team_name = user_dict[top_scorer]["team_name"]
    top_scorer_display_name = user_dict[top_scorer]["display_name"]

    # get the top scorer for each week
    top_scorers = {}
    for week in range(1, 18):
        top_scorer = max(user_dict, key=lambda x: user_dict[x]["scores"].get(week, 0))
        top_scorer_team_name = user_dict[top_scorer]["team_name"]
        top_scorers[week] = {
            "display_name": user_dict[top_scorer]["display_name"],
            "team_name": top_scorer_team_name,
            "score": user_dict[top_scorer]["scores"].get(week, 0),
        }

    stats = {
        "season": {
            "display_name": top_scorer_display_name,
            "team_name": top_scorer_team_name,
            "score": user_dict[top_scorer]["total_points"],
        },
        "weeks": top_scorers,
    }

    return stats


def make_output_directory(league_id):
    directory = f"output/{league_id}"
    try:
        os.makedirs(directory)
    except FileExistsError:
        pass

    return directory


def main(league_id, year):
    users = get_league_users(league_id)
    user_dict = parse_user_info(users)
    rosters = get_league_rosters(league_id)
    user_dict = add_roster_info_to_user_dict(user_dict, rosters)

    for week in range(1, 18):
        scores = get_week_scores(league_id, week)
        for user_id in user_dict:
            user_dict[user_id]["scores"] = user_dict[user_id].get("scores", {})
            user_dict[user_id]["scores"][week] = scores.get(
                user_dict[user_id].get("roster_id"), 0
            )

    for user_id in user_dict:
        user_dict[user_id]["total_points"] = sum(user_dict[user_id]["scores"].values())

    stats = get_stats(user_dict)

    output_dir = make_output_directory(league_id)

    with open(f"{output_dir}/{year}_teams.json", "w") as f:
        json.dump(user_dict, f, indent=4)

    with open(f"{output_dir}/{year}_stats.json", "w") as f:
        json.dump(stats, f, indent=4)


if __name__ == "__main__":
    main(league_id=1122378347419377664, year=2024)
