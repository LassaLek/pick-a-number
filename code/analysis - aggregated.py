import pandas as pd
from scipy.stats import kruskal, mannwhitneyu
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_combined_data():
    """
    This function reads 4 TSV files (file0.tsv, file1.tsv, file2.tsv, file3.tsv),
    merges them, and conducts:
        1) Prompt-based analysis across all models
        2) Model-based analysis across all prompts

    It then produces aggregated results in CSV format, bar plots, and a verbose text report.
    """

    # ------------------------------------------------
    # A) DEFINE YOUR MAPPINGS
    # ------------------------------------------------
    test_mapping = {
        "0_0": "Plain",
        "1_1": "Chain-of-thought (silent)",
        "2_2": "Chain-of-thought (revealed)",
        "3_3": "Counterfactual",
        "4_4": "Chain-of-thought (self-exp.)",
        "5_5": "Few-shots",
        "6_6": "Money"
    }

    # Extend or adjust this model mapping as appropriate to your data
    # e.g., "gpt-0" -> "Model 0", "gpt-1" -> "Model 1", etc.
    model_mapping = {
        "gpt-0": "GPT 3.5",
        "gpt-1": "GPT 4",
        "gpt-2": "GPT 4o-mini",
        "gpt-3": "GPT 4o",
        # Add more keys if needed, e.g., "gpt-4": "Model 4", etc.
    }

    # ------------------------------------------------
    # 1. LOAD & MERGE THE DATA
    # ------------------------------------------------
    file_names = ["file0.tsv", "file1.tsv", "file2.tsv", "file3.tsv"]
    data_frames = []

    for fname in file_names:
        df = pd.read_csv(fname, sep="\t")
        data_frames.append(df)

    combined_data = pd.concat(data_frames, ignore_index=True)

    # Compute PERCENT_CORRECT_2 from CORRECT_2 and TOTAL
    combined_data['PERCENT_CORRECT_2'] = (combined_data['CORRECT_2'] / combined_data['TOTAL']) * 100

    # Create descriptive columns for plotting and readability
    combined_data['Test_Description'] = combined_data['Test'].map(test_mapping).fillna(combined_data['Test'])
    combined_data['Model_Description'] = combined_data['Group'].map(model_mapping).fillna(combined_data['Group'])

    # ------------------------------------------------
    # 2. PROMPT-BASED ANALYSIS (ACROSS ALL MODELS)
    #    Group by 'Test' ignoring 'Group'
    # ------------------------------------------------
    prompt_groups = combined_data.groupby('Test_Description', as_index=False).agg(
        mean_correct=('PERCENT_CORRECT_2', 'mean'),
        std_correct=('PERCENT_CORRECT_2', 'std'),
        count=('PERCENT_CORRECT_2', 'count')
    )
    # Sort by descending mean correctness
    prompt_groups.sort_values(by='mean_correct', ascending=False, inplace=True)
    prompt_groups['Rank'] = range(1, len(prompt_groups) + 1)

    # Prepare data for Kruskal-Wallis (prompt-based)
    prompt_labels = combined_data['Test_Description'].unique()
    prompt_data_list = [combined_data.loc[combined_data['Test_Description'] == p, 'PERCENT_CORRECT_2']
                        for p in prompt_labels]
    kw_prompt = kruskal(*prompt_data_list)

    # Pairwise Mann-Whitney (prompt-based)
    prompt_pairwise = []
    for i in range(len(prompt_labels)):
        for j in range(i+1, len(prompt_labels)):
            p1 = prompt_labels[i]
            p2 = prompt_labels[j]
            group1 = combined_data.loc[combined_data['Test_Description'] == p1, 'PERCENT_CORRECT_2']
            group2 = combined_data.loc[combined_data['Test_Description'] == p2, 'PERCENT_CORRECT_2']
            mw_result = mannwhitneyu(group1, group2, alternative='two-sided')
            prompt_pairwise.append({
                "Prompt1": p1,
                "Prompt2": p2,
                "U": mw_result.statistic,
                "pval": mw_result.pvalue
            })

    # ------------------------------------------------
    # 3. MODEL-BASED ANALYSIS (ACROSS ALL PROMPTS)
    #    Group by 'Group' ignoring 'Test'
    # ------------------------------------------------
    model_groups = combined_data.groupby('Model_Description', as_index=False).agg(
        mean_correct=('PERCENT_CORRECT_2', 'mean'),
        std_correct=('PERCENT_CORRECT_2', 'std'),
        count=('PERCENT_CORRECT_2', 'count')
    )
    model_groups.sort_values(by='mean_correct', ascending=False, inplace=True)
    model_groups['Rank'] = range(1, len(model_groups) + 1)

    # Prepare data for Kruskal-Wallis (model-based)
    model_labels = combined_data['Model_Description'].unique()
    model_data_list = [combined_data.loc[combined_data['Model_Description'] == m, 'PERCENT_CORRECT_2']
                       for m in model_labels]
    kw_model = kruskal(*model_data_list)

    # Pairwise Mann-Whitney (model-based)
    model_pairwise = []
    for i in range(len(model_labels)):
        for j in range(i+1, len(model_labels)):
            m1 = model_labels[i]
            m2 = model_labels[j]
            grp1 = combined_data.loc[combined_data['Model_Description'] == m1, 'PERCENT_CORRECT_2']
            grp2 = combined_data.loc[combined_data['Model_Description'] == m2, 'PERCENT_CORRECT_2']
            mw_res = mannwhitneyu(grp1, grp2, alternative='two-sided')
            model_pairwise.append({
                "Model1": m1,
                "Model2": m2,
                "U": mw_res.statistic,
                "pval": mw_res.pvalue
            })

    # ------------------------------------------------
    # 4. VISUALS AND OUTPUT
    # ------------------------------------------------

    # --- A) Save aggregated results to CSV
    prompt_groups.to_csv("prompt_groups.csv", index=False)
    model_groups.to_csv("model_groups.csv", index=False)

    # --- B) Basic plot for prompt-based analysis
    plt.figure(figsize=(8,5))
    sns.barplot(data=prompt_groups, x='Test_Description', y='mean_correct', ci=None)
    plt.title("Mean %Correct by Prompt (All Models Combined)")
    plt.xlabel("Prompt Type")
    plt.ylabel("Mean Percentage")
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    plt.savefig("prompt_analysis_combined.png")
    plt.show()

    # --- C) Basic plot for model-based analysis
    plt.figure(figsize=(8,5))
    sns.barplot(data=model_groups, x='Model_Description', y='mean_correct', ci=None)
    plt.title("Mean %Correct by Model (All Prompts Combined)")
    plt.xlabel("Model")
    plt.ylabel("Mean Percentage")
    plt.tight_layout()
    plt.savefig("model_analysis_combined.png")
    plt.show()

    # --- D) Create a verbose text report
    with open("combined_analysis.txt", "w") as f:
        f.write("=== PROMPT-BASED ANALYSIS (All Models) ===\n\n")
        f.write(prompt_groups.to_string(index=False))
        f.write("\n\nKruskal-Wallis Test (Prompts):\n")
        f.write(f"  H-statistic = {kw_prompt.statistic}\n")
        f.write(f"  p-value     = {kw_prompt.pvalue}\n")
        if kw_prompt.pvalue < 0.05:
            f.write("  => Significant differences among prompt types.\n")
        else:
            f.write("  => No significant difference among prompt types.\n")

        f.write("\nPairwise Mann-Whitney (Prompts):\n")
        pairwise_df = pd.DataFrame(prompt_pairwise)
        f.write(pairwise_df.to_string(index=False))

        f.write("\n\n=== MODEL-BASED ANALYSIS (All Prompts) ===\n\n")
        f.write(model_groups.to_string(index=False))
        f.write("\n\nKruskal-Wallis Test (Models):\n")
        f.write(f"  H-statistic = {kw_model.statistic}\n")
        f.write(f"  p-value     = {kw_model.pvalue}\n")
        if kw_model.pvalue < 0.05:
            f.write("  => Significant differences among models.\n")
        else:
            f.write("  => No significant difference among models.\n")

        f.write("\nPairwise Mann-Whitney (Models):\n")
        modelwise_df = pd.DataFrame(model_pairwise)
        f.write(modelwise_df.to_string(index=False))

    print("Analysis complete. See 'combined_analysis.txt' for details.")
    print("Aggregated prompt results saved to 'prompt_groups.csv'.")
    print("Aggregated model results saved to 'model_groups.csv'.")

if __name__ == "__main__":
    analyze_combined_data()
