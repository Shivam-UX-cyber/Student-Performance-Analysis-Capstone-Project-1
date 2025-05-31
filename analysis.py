import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
      
def generate_summary(df):
    summary = {
        "Total Students": len(df),
        "Average Marks": df['Marks'].mean(),
        "Highest Marks": df['Marks'].max(),
        "Lowest Marks": df['Marks'].min(),
        "Pass Count": (df['Marks'] >= 33).sum(),
        "Fail Count": (df['Marks'] < 33).sum()
    }
    return summary

def plot_distribution(df, save_path='static/marks_distribution.png'):
    plt.figure(figsize=(8, 5))
    sns.histplot(df['Marks'], bins=10, kde=True)
    plt.title("Marks Distribution")
    plt.xlabel("Marks")
    plt.ylabel("Number of Students")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

def plot_top_students(df, save_path='static/top_students.png'):
    top_df = df.sort_values(by='Marks', ascending=False).head(5)
    plt.figure(figsize=(8, 5))
    sns.barplot(x='Name', y='Marks', data=top_df, palette='viridis')
    plt.title("Top 5 Students")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
