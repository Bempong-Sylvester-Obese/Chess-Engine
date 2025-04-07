#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import chess
import sys
import os

# Add the parent directory to the path so we can import the engine modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Engine.chess_suggester import ChessSuggester
from Engine.enhanced_engine import EnhancedChessSuggester

def load_training_data(file_path='Data/training_data.csv'):
    """Load the training data from CSV file."""
    try:
        df = pd.read_csv(file_path)
        print(f"Loaded {len(df)} positions from {file_path}")
        return df
    except FileNotFoundError:
        print(f"Training data file {file_path} not found")
        return None

def plot_opening_distribution(df, top_n=10):
    """Plot the distribution of openings in the training data."""
    plt.figure(figsize=(12, 6))
    
    # Count openings and get top N
    opening_counts = df['opening'].value_counts().head(top_n)
    
    # Create bar plot
    sns.barplot(x=opening_counts.values, y=opening_counts.index)
    plt.title(f'Top {top_n} Openings in Training Data')
    plt.xlabel('Number of Games')
    plt.ylabel('Opening')
    
    # Save plot
    plt.tight_layout()
    plt.savefig('Data/plots/opening_distribution.png')
    plt.close()

def plot_evaluation_distribution(df):
    """Plot the distribution of position evaluations."""
    plt.figure(figsize=(10, 6))
    
    # Create histogram of evaluations
    sns.histplot(data=df, x='evaluation', bins=50)
    plt.title('Distribution of Position Evaluations')
    plt.xlabel('Evaluation Score')
    plt.ylabel('Count')
    
    # Add vertical line at 0
    plt.axvline(x=0, color='r', linestyle='--', alpha=0.5)
    
    # Save plot
    plt.tight_layout()
    plt.savefig('Data/plots/evaluation_distribution.png')
    plt.close()

def plot_game_outcomes(df):
    """Plot the distribution of game outcomes."""
    plt.figure(figsize=(8, 8))
    
    # Count outcomes
    outcome_counts = df['result'].value_counts()
    
    # Create pie chart
    plt.pie(outcome_counts.values, labels=outcome_counts.index, autopct='%1.1f%%')
    plt.title('Distribution of Game Outcomes')
    
    # Save plot
    plt.tight_layout()
    plt.savefig('Data/plots/game_outcomes.png')
    plt.close()

def plot_player_ratings(df):
    """Plot the distribution of player ratings."""
    plt.figure(figsize=(12, 5))
    
    # Create subplots for white and black ratings
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    # White ratings
    sns.histplot(data=df, x='white_rating', bins=30, ax=ax1)
    ax1.set_title('Distribution of White Player Ratings')
    ax1.set_xlabel('Rating')
    ax1.set_ylabel('Count')
    
    # Black ratings
    sns.histplot(data=df, x='black_rating', bins=30, ax=ax2)
    ax2.set_title('Distribution of Black Player Ratings')
    ax2.set_xlabel('Rating')
    ax2.set_ylabel('Count')
    
    # Save plot
    plt.tight_layout()
    plt.savefig('Data/plots/player_ratings.png')
    plt.close()

def plot_engine_comparison(df, num_positions=100):
    """Plot comparison between original and enhanced engine evaluations."""
    # Initialize engines
    original_engine = ChessSuggester()
    enhanced_engine = EnhancedChessSuggester()
    
    # Sample random positions
    sample_positions = df.sample(min(num_positions, len(df)))
    
    # Get evaluations from both engines
    original_evals = []
    enhanced_evals = []
    training_evals = []
    
    for _, row in sample_positions.iterrows():
        board = chess.Board(row['fen'])
        original_evals.append(original_engine.evaluate_position(board))
        enhanced_evals.append(enhanced_engine.evaluate_position(board))
        training_evals.append(row['evaluation'])
    
    # Create scatter plot
    plt.figure(figsize=(10, 10))
    
    plt.scatter(training_evals, original_evals, alpha=0.5, label='Original Engine')
    plt.scatter(training_evals, enhanced_evals, alpha=0.5, label='Enhanced Engine')
    
    # Add diagonal line
    min_val = min(min(training_evals), min(original_evals), min(enhanced_evals))
    max_val = max(max(training_evals), max(original_evals), max(enhanced_evals))
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.5)
    
    plt.title('Engine Evaluations vs Training Data')
    plt.xlabel('Training Data Evaluation')
    plt.ylabel('Engine Evaluation')
    plt.legend()
    
    # Save plot
    plt.tight_layout()
    plt.savefig('Data/plots/engine_comparison.png')
    plt.close()

def plot_evaluation_correlation(df):
    """Plot correlation between different features and evaluation."""
    # Select numeric columns for correlation
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    # Calculate correlation matrix
    corr_matrix = df[numeric_cols].corr()
    
    # Create heatmap
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
    plt.title('Feature Correlation Matrix')
    
    # Save plot
    plt.tight_layout()
    plt.savefig('Data/plots/feature_correlation.png')
    plt.close()

def create_plots_directory():
    """Create directory for saving plots if it doesn't exist."""
    plots_dir = Path('Data/plots')
    plots_dir.mkdir(parents=True, exist_ok=True)
    return plots_dir

def main():
    """Main function to generate visualizations."""
    print("Generating visualizations for training data analysis...")
    
    # Create plots directory
    plots_dir = create_plots_directory()
    print(f"Created plots directory at {plots_dir}")
    
    # Load training data
    df = load_training_data()
    if df is None:
        return
    
    # Generate plots
    print("\nGenerating plots...")
    plot_opening_distribution(df)
    plot_evaluation_distribution(df)
    plot_game_outcomes(df)
    plot_player_ratings(df)
    plot_engine_comparison(df)
    plot_evaluation_correlation(df)
    
    print("\nAll plots have been saved to the Data/plots directory.")
    print("Generated the following visualizations:")
    print("1. Opening distribution (top 10 openings)")
    print("2. Position evaluation distribution")
    print("3. Game outcome distribution")
    print("4. Player rating distributions")
    print("5. Engine evaluation comparison")
    print("6. Feature correlation matrix")

if __name__ == "__main__":
    main() 