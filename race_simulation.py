import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class GreyhoundRaceSimulator:
    def __init__(self, num_dogs=6, bookmaker_margin=0.15):
        self.num_dogs = num_dogs
        self.bookmaker_margin = bookmaker_margin
    

    def generate_true_abilities(self):
        return np.random.normal(0, 1, self.num_dogs)
    

    def simulate_race(self, true_abilities, race_variance=0.5):
        race_performance = true_abilities + np.random.normal(0, race_variance, self.num_dogs)
        rankings = (-race_performance).argsort()
        return rankings
    

    def generate_fair_odds(self, true_abilities, num_simulations=10000):
        wins = np.zeros(self.num_dogs)

        for _ in range(num_simulations):
            rankings = self.simulate_race(true_abilities)
            wins[rankings[0]] += 1
        
        # Add a small constant to avoid division by zero
        wins = wins + 0.0001
        win_probs = wins / (num_simulations + self.num_dogs + 0.0001)

        # Cap maximum odds at 50.0 for realism
        fair_odds = np.minimum(1/win_probs, 50.0)

        # Apply the bookmaker margin - the "spread"
        bookmaker_odds = fair_odds * (1 - self.bookmaker_margin)

        return bookmaker_odds


    def calculate_place_odds(self, win_odds, place_fraction=0.25):
        return 1 + (win_odds - 1) * place_fraction


if __name__ == '__main__':
    # Create the simulator

    simulator = GreyhoundRaceSimulator(num_dogs=6)

    # Simulate some races
    num_races = 100
    results = []

    for race in range(num_races):
        true_abilities = simulator.generate_true_abilities()
        win_odds = simulator.generate_fair_odds(true_abilities)
        place_odds = simulator.calculate_place_odds(win_odds)
        rankings = simulator.simulate_race(true_abilities)
        
        race_result = {
            'race_id': race,
            'winner': rankings[0],
            'second': rankings[1],
            'third': rankings[2]
        }

        for i in range(simulator.num_dogs):
            race_result[f'dog_{i}_win_odds'] = win_odds[i]
            race_result[f'dog_{i}_place_odds'] = place_odds[i]

        results.append(race_result)

    df_results = pd.DataFrame(results)

    print(df_results[['race_id', 'winner', 'second', 'third']].head())

    print("\nSample Odds for First Race:")
    odds_cols = [col for col in df_results.columns if 'odds' in col]
    print(df_results[odds_cols].iloc[0])

    # Plot distribution of win odds (excluding extreme values)
    plt.figure(figsize=(10, 6))
    win_odds_cols = [col for col in df_results.columns if 'win_odds' in col]
    all_odds = df_results[win_odds_cols].values.flatten()
    plt.hist(all_odds[all_odds < 30], bins=30, alpha=0.7)  # Plot odds under 30 for better visualization
    plt.title('Distribution of Win Odds (excluding extreme values)')
    plt.xlabel('Odds')
    plt.ylabel('Frequency')
    plt.show()

    # Calculate average odds and win rates
    print("\nStatistics:")
    print(f"Average win odds: {all_odds.mean():.2f}")

    # Calculate win rate for favorites
    for race in range(num_races):
        race_odds = df_results[[f'dog_{i}_win_odds' for i in range(simulator.num_dogs)]].iloc[race]
        favorite = race_odds.idxmin().split('_')[1]
        df_results.loc[race, 'favorite'] = int(favorite)

    favorite_win_rate = (df_results['favorite'] == df_results['winner']).mean()
    print(f"Favorite win rate: {favorite_win_rate:.2%}")

    # Calculate ROI for betting on favorites
    stake = 1.0
    returns = []
    for _, race in df_results.iterrows():
        favorite = int(race['favorite'])
        if favorite == race['winner']:
            returns.append(stake * race[f'dog_{favorite}_win_odds'] - stake)
        else:
            returns.append(-stake)

    roi = np.mean(returns)
    print(f"ROI betting on favorites: {roi:.2%}")
                
