import pandas as pd
from scipy.stats import kruskal, mannwhitneyu, spearmanr
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_data(file_name):
    # ------------------------------------------------------------
    # 1. LOAD DATA
    # ------------------------------------------------------------
    data = pd.read_csv(file_name, sep="\t")
    
    # Compute percentages for both CORRECT_1 and CORRECT_2
    # (Even if CORRECT_1 is not used much, we’ll keep it for reference.)
    data['PERCENT_CORRECT_1'] = data['CORRECT_1'] / data['TOTAL'] * 100
    data['PERCENT_CORRECT_2'] = data['CORRECT_2'] / data['TOTAL'] * 100

    # Clean up missing or invalid values
    print("Checking for missing or invalid values in PERCENT_CORRECT_2...")
    data.replace([float('inf'), float('-inf')], None, inplace=True)
    data = data.dropna(subset=['PERCENT_CORRECT_2'])
    print("Remaining data after cleaning (first 5 rows):")
    print(data.head())

    # ------------------------------------------------------------
    # 2. MAP TEST LABELS FOR BETTER READABILITY
    # ------------------------------------------------------------
    # You can customize or extend this dictionary if you have additional test labels.
    test_mapping = {
        "0_0": "Plain",
        "1_1": "Chain-of-thought (silent)",
        "2_2": "Chain-of-thought (revealed)",
        "3_3": "Counterfactual",
        "4_4": "Chain-of-thought (self-exp.)",
        "5_5": "Few-shots",
        "6_6": "Money"
    }

    # Create a user-friendly label for each row based on the test type
    data['Test_Description'] = data['Test'].map(test_mapping)

    # Rename columns in data for clarity if desired:
    # 'Last_Digit' -> 'Critical_Step'
    data.rename(columns={'Last_Digit': 'Critical_Step'}, inplace=True)

    # ------------------------------------------------------------
    # 3. EXPLORATORY PLOT: PERFORMANCE vs. CRITICAL STEP
    # ------------------------------------------------------------
    # We'll visualize PERCENT_CORRECT_2 across different prompt methods,
    # plotted against the "Critical_Step."
    plt.figure(figsize=(10, 6))
    sns.lineplot(
        data=data,
        x='Critical_Step',
        y='PERCENT_CORRECT_2',
        hue='Test_Description',
        marker='o'
    )
    plt.title('Trend of Correctness (%) by Critical Step for Each Prompting Method')
    plt.xlabel('Critical Step')
    plt.ylabel('Percentage')
    plt.legend(title="Prompt Type")
    plt.savefig("trend_graph.png")
    plt.show()

    # ------------------------------------------------------------
    # 4. AGGREGATE DATA BY TEST (PROMPT) AND PRINT
    # ------------------------------------------------------------
    # We group by the original 'Test' code just for referencing,
    # but we display the mapped description in the final result.
    aggregated_data = data.groupby('Test', as_index=False).agg(
        mean_percent_correct=('PERCENT_CORRECT_2', 'mean'),
        std_percent_correct=('PERCENT_CORRECT_2', 'std'),
        count=('PERCENT_CORRECT_2', 'count')
    )

    print("\nAggregated Data by Test Code (unmapped):")
    print(aggregated_data)

    # Sort from best to worst
    aggregated_data = aggregated_data.sort_values(by='mean_percent_correct', ascending=False)
    aggregated_data['Rank'] = range(1, len(aggregated_data) + 1)

    # Merge aggregated_data with test_mapping so we see the descriptive name
    aggregated_data['Test_Description'] = aggregated_data['Test'].map(test_mapping)

    print("\nAggregated Data with Descriptions (Sorted by Mean % Correct):")
    print(aggregated_data[['Test','Test_Description','mean_percent_correct','std_percent_correct','count','Rank']])

    # ------------------------------------------------------------
    # 5. VISUALIZE AGGREGATED RESULTS
    # ------------------------------------------------------------
    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=aggregated_data,
        x='Test_Description',
        y='mean_percent_correct',
        ci=None,
        order=aggregated_data['Test_Description']
    )
    plt.title('Mean % Correct by Prompting Method')
    plt.xlabel('Prompting method')
    plt.ylabel('Mean percentage')
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    plt.savefig("aggregated_results.png")
    plt.show()

    # ------------------------------------------------------------
    # 6. NONPARAMETRIC COMPARISONS (KRUSKAL-WALLIS + MANN-WHITNEY U)
    # ------------------------------------------------------------
    # Kruskal-Wallis test: checks for differences among 3+ groups
    grouped_data = [data[data['Test'] == test]['PERCENT_CORRECT_2'] 
                    for test in data['Test'].unique()]
    kruskal_result = kruskal(*grouped_data)
    print("\nKruskal-Wallis Test Results (comparing prompt types overall):")
    print(f"H-statistic: {kruskal_result.statistic}, p-value: {kruskal_result.pvalue}")

    # Pairwise Mann-Whitney U tests for each pair of test groups
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
                "Test 1": f"{test1} - {test_mapping[test1]}",
                "Test 2": f"{test2} - {test_mapping[test2]}",
                "U-Statistic": mw_result.statistic,
                "p-value": mw_result.pvalue
            })
    pairwise_df = pd.DataFrame(pairwise_results)

    # ------------------------------------------------------------
    # 7. CHECK IF PERFORMANCE DROPS WITH RAISING CRITICAL STEP
    #    (EXPLORATORY SPEARMAN CORRELATION)
    # ------------------------------------------------------------
    # For each prompt method, we check correlation of PERCENT_CORRECT_2
    # with the Critical Step. This is purely exploratory.
    correlation_info = []
    for test_code in data['Test'].unique():
        sub_df = data[data['Test'] == test_code]
        if len(sub_df['Critical_Step'].unique()) > 1:  # Need >1 unique step
            rho, pval = spearmanr(sub_df['Critical_Step'], sub_df['PERCENT_CORRECT_2'])
            correlation_info.append({
                'Test_Code': test_code,
                'Test_Description': test_mapping.get(test_code, test_code),
                'Spearman_rho': rho,
                'Spearman_pvalue': pval
            })

    correlation_df = pd.DataFrame(correlation_info)

    # ------------------------------------------------------------
    # 8. SAVE RESULTS TO A FILE WITH VERBOSE COMMENTS
    # ------------------------------------------------------------
    with open("analysis_results.txt", "w") as f:
        f.write("----- Trend Graph -----\n")
        f.write("The file 'trend_graph.png' shows how PERCENT_CORRECT_2 changes as 'Critical_Step' increases,\n")
        f.write("with a separate line for each prompting method. If lines slope downward, that suggests\n")
        f.write("worsening performance at higher complexity levels.\n\n")

        f.write("----- Aggregated Data (Best to Worst) -----\n")
        f.write("Below is a sorted table of prompt methods by their average PERCENT_CORRECT_2.\n")
        f.write("(Higher mean_percent_correct = better overall performance.)\n\n")
        f.write(aggregated_data[['Test','Test_Description','mean_percent_correct',
                                 'std_percent_correct','count','Rank']].to_string(index=False))
        f.write("\n\n")

        f.write("----- Kruskal-Wallis Test (Overall Comparison) -----\n")
        f.write(f"H-statistic: {kruskal_result.statistic}, p-value: {kruskal_result.pvalue}\n")
        if kruskal_result.pvalue < 0.05:
            f.write("=> There is a statistically significant difference among the prompt methods.\n")
        else:
            f.write("=> No statistically significant difference among the prompt methods.\n")
        f.write("\n\n")

        f.write("----- Mann-Whitney U Tests (Pairwise) -----\n")
        f.write("Comparisons between each pair of prompt methods:\n")
        f.write(pairwise_df.to_string(index=False))
        f.write("\n\n")
        
        f.write("----- Correlation with Critical Step (Spearman) -----\n")
        f.write("For each prompt method, we check if there's a monotonic increase/decrease\n")
        f.write("in PERCENT_CORRECT_2 as 'Critical_Step' grows.\n\n")
        if len(correlation_df) == 0:
            f.write("No correlation data available (only 1 unique Critical_Step per prompt?).\n")
        else:
            f.write(correlation_df.to_string(index=False))
            f.write("\n\nInterpretation:\n")
            f.write("- Negative rho suggests performance decreases with higher Critical_Step.\n")
            f.write("- Positive rho suggests performance improves with higher Critical_Step.\n")
            f.write("- p-value < 0.05 implies correlation is statistically significant.\n")

    print("Analysis results saved to 'analysis_results.txt'.")
    aggregated_data.to_csv("aggregated_results.csv", index=False)
    pairwise_df.to_csv("pairwise_results.csv", index=False)
    correlation_df.to_csv("correlation_with_step.csv", index=False)
    print("Aggregated results saved to 'aggregated_results.csv'.")
    print("Pairwise comparison results saved to 'pairwise_results.csv'.")
    print("Correlation results saved to 'correlation_with_step.csv'.")

# Call the function if running as main
if __name__ == "__main__":
    file_name = "gpt-3.5-turbo.tsv"  # Replace with the actual file name or path
    analyze_data(file_name)
