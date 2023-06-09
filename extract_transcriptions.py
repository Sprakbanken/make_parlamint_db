import pandas as pd
import sqlite3
from pathlib import Path
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("path", help="path to the database")
parser.add_argument("-o", "--out_dir", help="Path to dir for output files")
parser.add_argument("-l", "--log_file", help="Path to log file where dates with no proceedings will be written")
parser.add_argument("-d", "--date_file", help="Path to csv file with the dates for the meetings to be extracted in a column named 'meeting_date'.")
args = parser.parse_args()

def make_proceedings_text(con, datelist, logfilepath, outdir):
    logfile = Path(logfilepath)
    for d in datelist:
        sql_query = f'''SELECT sent.sent_text FROM sentences sent 
            LEFT JOIN segments seg ON sent.seg_id = seg.seg_id 
            LEFT JOIN turns turn ON seg.turn_id = turn.turn_id 
        WHERE turn.meeting_id = "ParlaMint-NO_{d}.xml";'''
        cur = con.cursor()
        result = cur.execute(sql_query).fetchall()
        if len(result) == 0:
            print(d)
            with logfile.open(mode="a") as lf:
                lf.write(d + "\n")
        else:
            with (Path(outdir) / (d + "_proceedings.txt")).open(mode="w") as outfile:
                for row in result:
                    outfile.write(row[0] + "\n")

if __name__ == "__main__":
    con = sqlite3.connect(args.path)
    asr_dates = list(pd.read_csv(args.date_file)["meeting_date"].unique())
    make_proceedings_text(con, asr_dates, args.log_file, args.out_dir)
    con.close()



