import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

def evaluation(true_positive, false_positive, false_negative, true_negative):
    
    precision_value = precision(true_positive, false_positive)
    recall_value = recall(true_positive, false_negative)
    f1_score_value = f1_score(precision_value, recall_value)
    
    print(f"Precision : {precision_value:.2f}")
    print(f"Recall    : {recall_value:.2f}")
    print(f"F1-Score  : {f1_score_value:.2f}")
    
    confussion_matrix(true_positive, false_positive, false_negative, true_negative)
    
def evaluation_value(true_positive, false_positive, false_negative, true_negative):
    
    precision_value = precision(true_positive, false_positive)
    recall_value = recall(true_positive, false_negative)
    f1_score_value = f1_score(precision_value, recall_value)
    return precision_value, recall_value, f1_score_value
    
    

def confussion_matrix(true_positive, false_positive, false_negative, true_negative):
    cm = np.array([[true_positive, false_positive], [false_negative, true_negative]])
    
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        xticklabels=["Thích", "Không thích"],  # nhãn trực tiếp trục x
        yticklabels=["Thích", "Không thích"],  # nhãn trực tiếp trục y
    )

    plt.xlabel("Giá trị thực tế\nActual value", fontweight='bold')
    plt.ylabel("Giá trị dự đoán\nPredicted value", fontweight='bold')
    plt.title("MA TRẬN NHẦM LẪN CỦA HỆ THỐNG GỢI Ý\nHYBRID CONTENT-BASED + MODEL-BASED COLLABORATIVE", fontweight='bold')
    plt.show()
    print(f"TP: {true_positive} | FP: {false_positive}")
    print(f"FN: {false_negative} | TN: {true_negative}")

def f1_score(precision, recall):
    if precision + recall == 0:
        return 0
    
    return 2 * precision * recall / (precision + recall) if (precision + recall) else 0

def recall(true_positive, false_negative):
    if true_positive + false_negative == 0:
        return 0
    
    return true_positive / (true_positive + false_negative)


def precision(true_positive, false_positive):
    if true_positive + false_positive == 0:
        return 0
    
    return true_positive / (true_positive + false_positive)
