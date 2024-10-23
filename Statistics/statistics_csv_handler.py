import pandas as pd


def get_season_and_episode_number_to_title_csv(
    episode_info_csv: pd.DataFrame,
) -> pd.DataFrame:
    df = episode_info_csv[["Season", "Episode Number", "Title"]].copy()

    df.loc[:, "Question"] = df.apply(
        lambda row: f"What is the title of season {row['Season']} episode {row['Episode Number']}?",
        axis=1,
    )
    df.loc[:, "Answer"] = df["Title"]

    season_and_episode_df = df[["Question", "Answer"]]

    return season_and_episode_df


def get_season_and_episode_number_from_title_csv(
    episode_info_csv: pd.DataFrame,
) -> pd.DataFrame:
    df = episode_info_csv[["Season", "Episode Number", "Title"]].copy()

    df.loc[:, "Question"] = df.apply(
        lambda row: f"What is the season and episode number of the episode titled {row['Title']}?",
        axis=1,
    )
    df.loc[:, "Answer"] = df.apply(
        lambda row: f"Season {row['Season']}, Episode {row['Episode Number']}", axis=1
    )

    season_and_episode_df = df[["Question", "Answer"]]

    return season_and_episode_df


def get_episode_number_to_title_csv(
    episode_info_csv: pd.DataFrame,
) -> pd.DataFrame:
    df = episode_info_csv["Title"].copy()

    # get the row index as the episode number
    df.index = df.index + 1
    df = df.reset_index()
    df.columns = ["Episode Number", "Title"]

    total_episodes = len(df)
    df.loc[:, "Question"] = df.apply(
        lambda row: f"What is the title of episode number {row['Episode Number']} out of {total_episodes} episodes of the tv show Seinfeld?",
        axis=1,
    )
    df.loc[:, "Answer"] = df["Title"]

    number_to_title = df[["Question", "Answer"]]

    return number_to_title


def get_episode_number_from_title_csv(
    episode_info_csv: pd.DataFrame,
) -> pd.DataFrame:
    df = episode_info_csv["Title"].copy()

    # get the row index as the episode number
    df.index = df.index + 1
    df = df.reset_index()
    df.columns = ["Episode Number", "Title"]

    total_episodes = len(df)
    df.loc[:, "Question"] = df.apply(
        lambda row: f"What is the episode number of the episode titled {row['Title']} out of {total_episodes} episodes of the tv show Seinfeld?",
        axis=1,
    )
    df.loc[:, "Answer"] = df["Episode Number"]

    number_to_title = df[["Question", "Answer"]]

    return number_to_title


def get_episode_plot_from_title_csv(
    episode_info_csv: pd.DataFrame,
    episodes_plot: pd.DataFrame,
) -> pd.DataFrame:
    df = pd.merge(
        episode_info_csv,
        episodes_plot,
        on=["Episode Number", "Title", "Season", "SEID"],
        how="inner",
    )

    df.loc[:, "Question"] = df.apply(
        lambda row: f"What is the plot of the episode titled {row['Title']}?",
        axis=1,
    )
    df.loc[:, "Answer"] = df["Plot"]

    plot_df = df[["Question", "Answer"]]

    return plot_df


def get_episode_plot_to_title_csv(
    episode_info_csv: pd.DataFrame,
    episodes_plot: pd.DataFrame,
) -> pd.DataFrame:
    df = pd.merge(
        episode_info_csv,
        episodes_plot,
        on=["Episode Number", "Title", "Season", "SEID"],
        how="inner",
    )

    df.loc[:, "Question"] = df.apply(
        lambda row: f"What is the title of the episode with the plot: '{row['Plot']}'?",
        axis=1,
    )
    df.loc[:, "Answer"] = df["Title"]

    plot_df = df[["Question", "Answer"]]

    return plot_df


def get_writer_from_title_csv(
    episode_info_csv: pd.DataFrame,
) -> pd.DataFrame:
    df = episode_info_csv[["Title", "Writers"]].copy()

    df.loc[:, "Question"] = df.apply(
        lambda row: f"Who wrote the episode titled {row['Title']}?",
        axis=1,
    )
    df.loc[:, "Answer"] = df["Writers"]

    writer_df = df[["Question", "Answer"]]

    return writer_df


def get_titles_from_writer_csv(
    episode_info_csv: pd.DataFrame,
) -> pd.DataFrame:
    df = episode_info_csv[["Title", "Writers"]].copy()

    # get all writers from all episodes, split them and stack them
    writers = (
        df["Writers"].str.split(",").apply(pd.Series).stack().reset_index(drop=True)
    )

    # get rid of the whitespace and drop duplicates
    writers = writers.str.strip().drop_duplicates()

    # for every writer, get the episodes they wrote
    writer_to_title = pd.DataFrame()
    episodes_list = []
    for writer in writers:
        episodes = df[df["Writers"].str.contains(writer)]["Title"]

        # turn episodes into a string
        episodes = ", ".join(episodes)

        episodes_list.append(episodes)

    # create the dataframe with a question and answer column
    writer_to_title.loc[:, "Question"] = [
        f"What episodes were written by {writer}?" for writer in writers
    ]
    writer_to_title.loc[:, "Answer"] = episodes_list

    return writer_to_title


def get_director_from_title_csv(
    episode_info_csv: pd.DataFrame,
) -> pd.DataFrame:
    df = episode_info_csv[["Title", "Director"]].copy()

    df.loc[:, "Question"] = df.apply(
        lambda row: f"Who directed the episode titled {row['Title']}?",
        axis=1,
    )
    df.loc[:, "Answer"] = df["Director"]

    director_df = df[["Question", "Answer"]]

    return director_df


def get_quotes_from_main_characters_csv(
    scripts_csv: pd.DataFrame,
) -> pd.DataFrame:
    # get the main characters
    main_characters = ["JERRY", "GEORGE", "ELAINE", "KRAMER"]
    main_characters_to_full_name = {
        "JERRY": "Jerry Seinfeld",
        "GEORGE": "George Costanza",
        "ELAINE": "Elaine Benes",
        "KRAMER": "Cosmo Kramer",
    }

    # get all the quotes from the main characters
    main_characters_quotes = scripts_csv[scripts_csv["Character"].isin(main_characters)]

    # for every quote, ask who said the quote
    quotes_df = main_characters_quotes[["Character", "Dialogue"]].copy()
    quotes_df.loc[:, "Question"] = quotes_df.apply(
        lambda row: f"Who said the quote: '{row['Dialogue']}'?",
        axis=1,
    )

    quotes_df.loc[:, "Answer"] = quotes_df["Character"].apply(
        lambda character: main_characters_to_full_name[character],
    )

    quotes_df = quotes_df[["Question", "Answer"]]

    return quotes_df


def get_quotes_from_side_characters_csv(
    scripts_csv: pd.DataFrame,
) -> pd.DataFrame:
    # get the side characters
    side_characters = [
        "MORTY",
        "HELEN",
        "FRANK",
        "ESTELLE",
        "SUSAN",
        "DAVID",
        "JACK",
        "NEWMAN",
        "PUDDY",
        "JACKIE",
        "SOUP NAZI",
    ]
    side_characters_to_full_name = {
        "MORTY": "Morty Seinfeld",
        "HELEN": "Helen Seinfeld",
        "FRANK": "Frank Costanza",
        "ESTELLE": "Estelle Costanza",
        "SUSAN": "Susan Ross",
        "DAVID": "David Puddy",
        "JACK": "Jack Klompus",
        "NEWMAN": "Newman",
        "PUDDY": "David Puddy",
        "JACKIE": "Jackie Chiles",
        "SOUP NAZI": "Yev Kassem (Soup nazi)",
    }

    # get all the quotes from the side characters
    side_characters_quotes = scripts_csv[scripts_csv["Character"].isin(side_characters)]

    # for every quote, ask who said the quote
    quotes_df = side_characters_quotes[["Character", "Dialogue"]].copy()
    quotes_df.loc[:, "Question"] = quotes_df.apply(
        lambda row: f"Who said the quote: '{row['Dialogue']}'?",
        axis=1,
    )

    quotes_df.loc[:, "Answer"] = quotes_df["Character"].apply(
        lambda character: side_characters_to_full_name[character],
    )

    quotes_df = quotes_df[["Question", "Answer"]]

    return quotes_df


def get_episode_from_quote_csv(
    scripts_csv: pd.DataFrame,
) -> pd.DataFrame:
    # for every quote, ask which episode it is from
    quotes_df = scripts_csv[["Season", "Episode Number", "Dialogue"]].copy()
    quotes_df.loc[:, "Question"] = quotes_df.apply(
        lambda row: f"Which episode is the quote: '{row['Dialogue']}' from?",
        axis=1,
    )

    quotes_df.loc[:, "Answer"] = quotes_df.apply(
        lambda row: f"Season {int(row['Season'])}, Episode {int(row['Episode Number'])}",
        axis=1,
    )

    quotes_df = quotes_df[["Question", "Answer"]]

    return quotes_df


if __name__ == "__main__":
    scripts_csv = pd.read_csv("Data/scripts.csv")
    episode_info_csv = pd.read_csv("Data/episode_info.csv")
    episodes_plot_csv = pd.read_csv("Data/episodes_plot.csv")

    # get_season_and_episode_number_to_title_csv(episode_info_csv).to_csv(
    #     "Statistics/season_and_episode_number_to_title_questions.csv", index=False
    # )

    # get_season_and_episode_number_from_title_csv(episode_info_csv).to_csv(
    #     "Statistics/season_and_episode_number_from_title_questions.csv", index=False
    # )

    # get_episode_number_to_title_csv(episode_info_csv).to_csv(
    #     "Statistics/episode_number_to_title_questions.csv", index=False
    # )

    # get_episode_number_from_title_csv(episode_info_csv).to_csv(
    #     "Statistics/episode_number_from_title_questions.csv", index=False
    # )

    # get_episode_plot_from_title_csv(episode_info_csv, episodes_plot_csv).to_csv(
    #     "Statistics/episode_plot_from_title_questions.csv", index=False
    # )

    # get_episode_plot_to_title_csv(episode_info_csv, episodes_plot_csv).to_csv(
    #     "Statistics/episode_plot_to_title_questions.csv", index=False
    # )

    # get_writer_from_title_csv(episode_info_csv).to_csv(
    #     "Statistics/writer_from_title_questions.csv", index=False
    # )

    # get_titles_from_writer_csv(episode_info_csv).to_csv(
    #     "Statistics/titles_from_writer_questions.csv", index=False
    # )

    # get_director_from_title_csv(episode_info_csv).to_csv(
    #     "Statistics/director_from_title_questions.csv", index=False
    # )

    # get_quotes_from_main_characters_csv(scripts_csv).to_csv(
    #     "Statistics/quotes_from_main_characters_questions.csv", index=False
    # )

    # get_quotes_from_side_characters_csv(scripts_csv).to_csv(
    #     "Statistics/quotes_from_side_characters_questions.csv", index=False
    # )

    # get_episode_from_quote_csv(scripts_csv).to_csv(
    #     "Statistics/episode_from_quote_questions.csv", index=False
    # )
