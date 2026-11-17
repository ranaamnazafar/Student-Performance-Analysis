# Import pandas library
import pandas as pd

# Load the student performance dataset
df = pd.read_csv("dataset/StudentsPerformance.csv")

# Display first 5 rows
print("First 5 Rows:")
print(df.head())

# Display dataset information
print("\nDataset Information:")
print(df.info())

# Display total rows and columns
print("\nDataset Shape:")
print(df.shape)

# Check missing values
print("\nMissing Values:")
print(df.isnull().sum())

# Check duplicate records
print("\nDuplicate Records:")
print(df.duplicated().sum())
# STEP 3: Handle Missing Values

# Find the mode of parental education
mode_value = df["parental level of education"].mode()[0]

# Fill missing values with mode
df["parental level of education"] = df["parental level of education"].fillna(mode_value)

# Check missing values again
print("\nMissing Values After Cleaning:")
print(df.isnull().sum())
# STEP 4: Remove Duplicate Records

# Check duplicate records
print("\nDuplicate Records Before Cleaning:")
print(df.duplicated().sum())

# Remove duplicate records
df = df.drop_duplicates()

# Check duplicates again
print("\nDuplicate Records After Cleaning:")
print(df.duplicated().sum())

# Display final dataset shape
print("\nDataset Shape After Removing Duplicates:")
print(df.shape)
# STEP 5: Data Type Checking and Correction

# Define text columns
text_columns = [
    "gender",
    "race/ethnicity",
    "parental level of education",
    "lunch",
    "test preparation course"
]

# Convert text columns into string type
for col in text_columns:
    df[col] = df[col].astype("string")

# Convert score columns into numeric types
score_columns = [
    "math score",
    "reading score",
    "writing score"
]

for col in score_columns:
    df[col] = pd.to_numeric(df[col], errors="raise")

# Display data types after correction
print("\nData Types After Correction:")
print(df.dtypes)
# STEP 6: Outlier Detection using IQR

# Select numerical columns
score_columns = [
    "math score",
    "reading score",
    "writing score"
]

# Check outliers in each column
for col in score_columns:

    # Calculate Q1 and Q3
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)

    # Calculate IQR
    IQR = Q3 - Q1

    # Calculate lower and upper limits
    lower_limit = Q1 - 1.5 * IQR
    upper_limit = Q3 + 1.5 * IQR

    # Identify outliers
    outliers = df[
        (df[col] < lower_limit) |
        (df[col] > upper_limit)
    ]

    # Display results
    print("\nColumn:", col)
    print("Lower Limit:", lower_limit)
    print("Upper Limit:", upper_limit)
    print("Number of Outliers:", len(outliers))
    print("Outlier Values:")
    print(outliers[col].values)
    # STEP 7: Data Validation

score_columns = [
    "math score",
    "reading score",
    "writing score"
]

for col in score_columns:

    # Check invalid scores
    invalid_scores = df[
        (df[col] < 0) | (df[col] > 100)
    ]

    print("\nColumn:", col)
    print("Invalid Scores:", len(invalid_scores))

    if len(invalid_scores) > 0:
        print(invalid_scores[col].values)
        # STEP 8: Handle Invalid Scores

# Replace scores greater than 100 with NaN
df.loc[df["math score"] > 100, "math score"] = pd.NA

# Calculate median of math score
math_median = df["math score"].median()

# Replace NaN with median
df["math score"] = df["math score"].fillna(math_median)

print("\nInvalid Scores After Cleaning:")
print(df[df["math score"] > 100])

print("\nMissing Values After Final Cleaning:")
print(df.isnull().sum())

print("\nFinal Dataset Shape:")
print(df.shape)
# STEP 9: Save Cleaned Dataset

df.to_csv(
    "cleaned_data/StudentsPerformance_Cleaned.csv",
    index=False
)

print("\nCleaned Dataset Saved Successfully!")
# STEP 10: Data Analysis

print("\n========== STUDENT PERFORMANCE ANALYSIS ==========")

# Total Students
print("\nTotal Number of Students:", len(df))

# Gender Count
print("\nGender Distribution:")
print(df["gender"].value_counts())

# Average Scores
print("\nAverage Math Score:", df["math score"].mean())
print("Average Reading Score:", df["reading score"].mean())
print("Average Writing Score:", df["writing score"].mean())

# Highest Scores
print("\nHighest Math Score:", df["math score"].max())
print("Highest Reading Score:", df["reading score"].max())
print("Highest Writing Score:", df["writing score"].max())

# Lowest Scores
print("\nLowest Math Score:", df["math score"].min())
print("Lowest Reading Score:", df["reading score"].min())
print("Lowest Writing Score:", df["writing score"].min())
# STEP 11: Data Visualization

import matplotlib.pyplot as plt
import os

# Create graphs folder if it does not exist
os.makedirs("graphs", exist_ok=True)


# Graph 1: Gender Distribution

gender_counts = df["gender"].value_counts()

plt.figure(figsize=(7, 5))
gender_counts.plot(kind="bar")

plt.title("Gender Distribution of Students")
plt.xlabel("Gender")
plt.ylabel("Number of Students")
plt.xticks(rotation=0)

plt.savefig("graphs/gender_distribution.png")
plt.show()


# Graph 2: Average Subject Scores

average_scores = [
    df["math score"].mean(),
    df["reading score"].mean(),
    df["writing score"].mean()
]

subjects = ["Math", "Reading", "Writing"]

plt.figure(figsize=(7, 5))
plt.bar(subjects, average_scores)

plt.title("Average Scores by Subject")
plt.xlabel("Subjects")
plt.ylabel("Average Marks")

plt.savefig("graphs/average_subject_scores.png")
plt.show()


# Graph 3: Subject Score Distribution

plt.figure(figsize=(8, 5))

plt.hist(df["math score"], bins=10, alpha=0.5, label="Math")
plt.hist(df["reading score"], bins=10, alpha=0.5, label="Reading")
plt.hist(df["writing score"], bins=10, alpha=0.5, label="Writing")

plt.title("Subject Score Distribution")
plt.xlabel("Marks")
plt.ylabel("Number of Students")
plt.legend()

plt.savefig("graphs/subject_score_distribution.png")
plt.show()

print("\nAll Graphs Created Successfully!")
# STEP 12: Advanced Data Analysis

print("\n========== ADVANCED DATA ANALYSIS ==========")

# Pass and Fail Analysis
df["average score"] = df[
    ["math score", "reading score", "writing score"]
].mean(axis=1)

df["result"] = df["average score"].apply(
    lambda x: "Pass" if x >= 40 else "Fail"
)

print("\nPass and Fail Students:")
print(df["result"].value_counts())


# Test Preparation Analysis
print("\nPerformance Based on Test Preparation:")
print(
    df.groupby("test preparation course")[
        ["math score", "reading score", "writing score"]
    ].mean()
)


# Lunch Type Analysis
print("\nPerformance Based on Lunch Type:")
print(
    df.groupby("lunch")[
        ["math score", "reading score", "writing score"]
    ].mean()
)


# Gender Wise Performance
print("\nGender Wise Average Performance:")
print(
    df.groupby("gender")[
        ["math score", "reading score", "writing score"]
    ].mean()
)
# Update Cleaned Dataset

df.to_csv(
    "cleaned_data/StudentsPerformance_Cleaned.csv",
    index=False
)

print("\nUpdated Cleaned Dataset Saved Successfully!")