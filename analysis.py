import os
os.environ['MPLCONFIGDIR'] = os.getcwd() + "/configs/"
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

def plot_subject_marks(subjects, email, plots_dir):
    if not subjects:
        return None
    plt.figure(figsize=(6, 3))
    sns.barplot(x=list(subjects.keys()), y=list(map(float, subjects.values())), palette="Blues_d")
    plt.title("Subject-wise Marks")
    plt.ylabel("Marks")
    plt.tight_layout()
    filename = f"{email}_subject_marks.png"
    path = os.path.join(plots_dir, filename)
    plt.savefig(path)
    plt.close()
    return f"plots/{filename}"

def plot_study_hours(study_hours, email, plots_dir):
    plt.figure(figsize=(3, 3))
    plt.bar(["Study Hours"], [study_hours], color="#4caf50")
    plt.ylim(0, 12)
    plt.title("Study Hours/Day")
    plt.tight_layout()
    filename = f"{email}_study_hours.png"
    path = os.path.join(plots_dir, filename)
    plt.savefig(path)
    plt.close()
    return f"plots/{filename}"

def plot_radar_chart(sleep_hours, screen_time, stress, study_hours, email, plots_dir):
    labels = ['Sleep', 'Screen', 'Stress', 'Study']
    stats = [sleep_hours, screen_time, stress, study_hours]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    stats += stats[:1]
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.plot(angles, stats, 'o-', linewidth=2)
    ax.fill(angles, stats, alpha=0.25)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_title("Lifestyle Radar")
    filename = f"{email}_radar.png"
    path = os.path.join(plots_dir, filename)
    plt.savefig(path)
    plt.close()
    return f"plots/{filename}"