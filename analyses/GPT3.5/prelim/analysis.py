import pandas as pd
from scipy.stats import kruskal, mannwhitneyu
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_data(file_name):
    # Load the data
    data = pd.read_csv(file_name, sep="\t")
    
    # Add calculated columns for percentages
    data['PERCENT_CORRECT_1'] = data['CORRECT_1'] / data['TOTAL'] * 100
    data['PERCENT_CORRECT_2'] = data['CORRECT_2'] / data['TOTAL'] * 100

    # Handle missing or invalid values
    print("Checking for missing or invalid values in PERCENT_CORRECT_2...")
    data.replace([float('inf'), float('-inf')], None, inplace=True)
    data = data.dropna(subset=['PERCENT_CORRECT_2'])
    print("Remaining data after cleaning:")
    print(data.head())

    # Map test labels for better understanding
    test_mapping = {
        "0_0": "Plain",
        "1_1": "CoT - silent",
        "2_2": "CoT",
        "3_3": "Counter",
        "4_4": "Expl",
        "5_5": "FS",
        "6_6": "Money"
    }
    data['Test_Description'] = data['Test'].map(test_mapping)

    # Plot trend graph for all data with mapping
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=data, x='Last_Digit', y='PERCENT_CORRECT_2', hue='Test_Description', marker='o')
    plt.title('Trend: PERCENT_CORRECT_2 by Last_Digit for Each Test')
    plt.xlabel('Last_Digit')
    plt.ylabel('PERCENT_CORRECT_2')
    plt.legend(title="Test Type")
    plt.savefig("trend_graph.png")
    plt.show()

    # Aggregate data by Test
    aggregated_data = data.groupby('Test', as_index=False).agg(
        mean_percent_correct=('PERCENT_CORRECT_2', 'mean'),
        std_percent_correct=('PERCENT_CORRECT_2', 'std'),
        count=('PERCENT_CORRECT_2', 'count')
    )
    print("\nAggregated Data:")
    print(aggregated_data)

    # Add rankings from best to worst
    aggregated_data = aggregated_data.sort_values(by='mean_percent_correct', ascending=False)
    aggregated_data['Rank'] = range(1, len(aggregated_data) + 1)

    # Visualize aggregated results
    plt.figure(figsize=(10, 6))
    sns.barplot(data=aggregated_data, x='Test', y='mean_percent_correct', ci=None, order=aggregated_data['Test'])
    plt.title('Mean PERCENT_CORRECT_2 by Test')
    plt.xlabel('Test')
    plt.ylabel('Mean PERCENT_CORRECT_2')
    plt.savefig("aggregated_results.png")
    plt.show()

    # Kruskal-Wallis test for overall significance
    grouped_data = [data[data['Test'] == test]['PERCENT_CORRECT_2'] for test in data['Test'].unique()]
    kruskal_result = kruskal(*grouped_data)
    print("\nKruskal-Wallis Test Results:")
    print(f"H-statistic: {kruskal_result.statistic}, p-value: {kruskal_result.pvalue}")

    # Additional Mann-Whitney U test for pairwise comparisons
    pairwise_results = []
    unique_tests = data['Test'].unique()
    for i in range(len(unique_tests)):
        for j in range(i + 1, len(unique_tests)):
            test1 = unique_tests[i]
            test2 = unique_tests[j]
            group1 = data[data['Test'] == test1]['PERCENT_CORRECT_2']
            group2 = data[data['Test'] == test2]['PERCENT_CORRECT_2']
            mw_result = mannwhitneyu(group1, group2, alternative='two-sided')
            pairwise_results.append({
                "Test 1": test_mapping[test1],
                "Test 2": test_mapping[test2],
                "U-Statistic": mw_result.statistic,
                "p-value": mw_result.pvalue
            })
    pairwise_df = pd.DataFrame(pairwise_results)

    # Save results to a file with verbose comments
    with open("analysis_results.txt", "w") as f:
        f.write("----- Trend Graph -----\n")
        f.write("The trend graph shows PERCENT_CORRECT_2 values by Last_Digit for each test type.\n")
        f.write("It provides a visual comparison of how performance changes across Last_Digit.\n")
        f.write("The graph is saved as 'trend_graph.png'.\n")
        f.write("\n----- Aggregated Data (Best to Worst) -----\n")
        f.write("The following table ranks tests based on their average PERCENT_CORRECT_2:\n")
        f.write(aggregated_data.to_string(index=False))
        f.write("\n\n----- Statistical Tests -----\n")
        f.write("1. Kruskal-Wallis Test Results:\n")
        f.write(f"H-statistic: {kruskal_result.statistic}, p-value: {kruskal_result.pvalue}\n")
        if kruskal_result.pvalue < 0.05:
            f.write("There is a significant difference between the test groups.\n")
        else:
            f.write("No significant difference between the test groups.\n")
        f.write("\n2. Pairwise Mann-Whitney U Test Results:\n")
        f.write("This test compares each pair of tests to identify significant differences:\n")
        f.write(pairwise_df.to_string(index=False))
    print("Analysis results saved to 'analysis_results.txt'.")

    # Save aggregated results and pairwise comparisons
    aggregated_data.to_csv("aggregated_results.csv", index=False)
    pairwise_df.to_csv("pairwise_results.csv", index=False)
    print("Aggregated results saved to 'aggregated_results.csv'.")
    print("Pairwise comparison results saved to 'pairwise_results.csv'.")

# Call the function
if __name__ == "__main__":
    file_name = "gpt-4o-mini.tsv"  # Replace with your file name
    analyze_data(file_name)
