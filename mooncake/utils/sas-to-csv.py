
import pyreadstat
import pandas as pd


def read_sas_pyreadstat(fname):
    # Read the .sas7bdat file into a Pandas DataFrame
    df, meta = pyreadstat.read_sas7bdat(fname)
    return df

def read_sas_pandas(fname):
    df = pd.read_sas(fname)
    return df


if __name__ == "__main__":

    input_file = './mooncake/data/sp500s/sp500cik.sas7bdat'
    output_file = './mooncake/data/sp500s/sp500cik.csv'

    #df = read_sas_pyreadstat(input_file)
    df = read_sas_pandas(input_file)

    # quick data clean to transform b'{cell}' -> {cell}
    for col, dtype in df.dtypes.items():
        if dtype == object:
            df[col] = df[col].str.decode("utf-8")

    # Write the DataFrame to a CSV file
    df.to_csv(output_file, index=False)
    print(f"Data from {input_file} has been successfully written to {output_file}")
