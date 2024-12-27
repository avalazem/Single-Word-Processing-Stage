import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

csv_input_path=r'C:/Users/ali_a/Desktop/Single Word Processing Stage/Single Word Processing/Data/French Data/deliane_french_real/french_stimuli_real.csv'

stimuli_df = pd.read_csv(csv_input_path)

# Scatter Plot:

# Define custom color function
def get_custom_color(row):
    if row['Condition'] == 'RSLS' :
        return 'pink'
    elif row['Condition'] == 'RSLC' :
        return 'salmon'
    elif row['Condition'] == 'RLLS' :
        return 'crimson'
    elif row['Condition'] == 'RLLC' :
        return 'maroon'
    elif row['Condition'] == 'RSHS' :
        return 'lightblue'
    elif row['Condition'] == 'RSHC' :
        return 'lightskyblue'
    elif row['Condition'] == 'RLHS' :
        return 'deepskyblue'
    elif row['Condition'] == 'RLHC' :
        return 'indigo'

# Add a 'Custom Color' column
stimuli_df['Custom Color'] = stimuli_df.apply(get_custom_color, axis=1)

# Plot with scatterplot
scatter = sns.scatterplot(
    data=stimuli_df,
    x="Wordlength", 
    y="Zipf Frequency", 
    hue="Condition",  # For color legend
    style="Morphology",  # For shape legend
    style_order=['simple', 'complex'], 
    markers={'simple': 'o', 'complex': 'X'},  # Compatible filled markers
    palette=list(stimuli_df['Custom Color'].unique()),  # Convert to list
    legend='brief'  # Ensures legend displays
)


plt.title('Comparison of Length and Word Frequency Across 8 Conditions (French Stimuli)', y=1.06)
plt.legend(loc='upper left', bbox_to_anchor=(1, 1), title='Legend')
plt.show()

# remove color column from df
del stimuli_df['Custom Color']

# Group by both 'Condition' and 'Wordlength' and count the occurrences
condition_wordlength_counts = stimuli_df.groupby(['Condition', 'Wordlength']).size().reset_index(name='Count')

# Display the counts
print(condition_wordlength_counts)
