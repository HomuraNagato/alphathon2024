
import pyreadstat
import pandas as pd

# Define the input .sas7bdat file and output .csv file

def read_sas_pyreadstat(fname):
    # Read the .sas7bdat file into a Pandas DataFrame
    df, meta = pyreadstat.read_sas7bdat(fname)
    return df

def read_sas_pandas(fname):
    df = pd.read_sas(fname)
    return df


if __name__ == "__main__":

    input_file = './mooncake/sp500list/sp500list.sas7bdat'  # Replace with your actual .sas7bdat file
    output_file = './mooncake/sp500list/sp500list.csv'  # Replace with your desired CSV filename

    #df = read_sas_pyreadstat(input_file)
    df = read_sas_pandas(input_file)

    # Write the DataFrame to a CSV file
    df.to_csv(output_file, index=False)
    print(f"Data from {input_file} has been successfully written to {output_file}")
