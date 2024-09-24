
import argparse
import os
import pandas as pd
from pathlib import Path
from sklearn.metrics import confusion_matrix, accuracy_score, balanced_accuracy_score, classification_report
import sys
import yaml

sys.path.append(str(Path(os.getcwd(), os.environ.get("REL_DIR", ""))))

from llm.constants.constants_llm import ConstantsLLM
from llm.utils.utilities import create_path

def initialise():

    parse = argparse.ArgumentParser(
        description="calculate summary and per-category statistics",
        epilog="example: python models/test/test_model_statistics.py  --test_response_path data/testing/telcel/test_001.csv --statistic_path data/testing/telcel/s001.csv")
    parse.add_argument("--test_response_path",
                       required=True,
                       help="location of model responses for test data")
    parse.add_argument("--statistic_path",
                       nargs="?",
                       help="if provided, location to store statistics")
    parse.add_argument("--column_truth",
                       nargs="?",
                       default="true_category",
                       help="column with predictions to compare to actual")
    parse.add_argument("--column_predicted",
                       nargs="?",
                       default="llm_model_category",
                       help="column with predictions to compare to actual")
    args = parse.parse_args()

    return args


class StatisticReport:

    def __init__(self, default_flow_style, data):
        self.default_flow_style = default_flow_style
        self.data = data


class StatisticEngine:

    def __init__(self):
        self.cnst = ConstantsLLM()

    def calc_confusion_matrix(self, data_path, col_true, col_pred):
        # assume true_category is static, and predicted might be variable,
        # such as from mapping_rules or base model

        df = pd.read_csv(data_path).fillna("")
        df = df.map(lambda x: x.lower() if isinstance(x, str) else x)
        labels = df.loc[:,col_true].unique()

        predicted = df.loc[:,col_pred]
        actual = df.loc[:,col_true]

        acc_score = accuracy_score(actual, predicted)
        cls_report = classification_report(actual,
                                           predicted,
                                           labels=labels,
                                           output_dict=True,
                                           zero_division=0.0)
        conf_matrix = confusion_matrix(actual, predicted, labels=labels)
        conf_matrix = [ [ int(x) for x in row ] for row in conf_matrix ]

        accuracies = {}
        for category in labels:
            actual_category = (actual == category)
            predicted_category = (predicted == category)
            actual_true = len([ x for x in actual_category if x == True ])
            pred_true = len([ x for x in predicted_category if x == True ])
            accuracy = accuracy_score(actual_category, predicted_category)
            print(f"{category} - {accuracy} {actual_true} {pred_true}")
            accuracies[category] = round(float(accuracy), 2)

        #accuracies_df = pd.DataFrame(accuracies.items(), columns=['category', 'accuracy'])
        min_accuracy_key = min(accuracies, key=accuracies.get)
        min_accuracy_val = accuracies[min_accuracy_key]

        print(f"the model that produced {data_path} has an accuracy score of {acc_score}")
        print(f"the category {min_accuracy_key} has the worst accuracy of {min_accuracy_val}")
        print(f"accuracies per category {accuracies}")

        # specify format style for various metrics
        d01 = {
            "data_path": data_path,
            "total_accuracy": float(acc_score),
            "per_category_accuracy": accuracies,
            "classification_report": cls_report,
        }
        report01 = StatisticReport(False, d01)
        d02 = {
                "confusion_matrix": conf_matrix
            }
        report02 = StatisticReport(None, d02)
        return [report01, report02]

    def save_statistics(self, stat_path, stat_reports):

        if not stat_path:
            return

        def write_entry_yaml(f, stat_dict_entry, default_flow_style):
            for key, value in stat_dict_entry.items():
                d = {key: value}
                f.write("\n")
                f.write(yaml.safe_dump(d,
                                       allow_unicode=True,
                                       indent=4,
                                       default_flow_style=default_flow_style))

        create_path(stat_path)
        f = open(stat_path, "w")
        for report in stat_reports:
            write_entry_yaml(f, report.data, report.default_flow_style)
        f.close()
        print(f"statistics have been saved at {stat_path}")


if __name__ == "__main__":

    args = initialise()

    stat_engine = StatisticEngine()
    stat_reports = stat_engine.calc_confusion_matrix(args.test_response_path,
                                                     args.column_truth,
                                                     args.column_predicted)
    stat_engine.save_statistics(args.statistic_path, stat_reports)
