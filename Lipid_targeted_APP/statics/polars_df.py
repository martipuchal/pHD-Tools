import polars as pl
import numpy as np


def clearance(fname):
    with open(fname, "r") as f: # Open the .csv raw file.
        # Declare the diferent list 
        file = []
        i_cols = []
        e_cols = []
        
        for i, file_line in enumerate(f.readlines()): # Loop through the lines of the file 
            if i!= 1: # Skip the line second line
                line = file_line.split(",") # And convert the string to a list to a list in the case of the first lien of the file
                if i == 0: # The first lien contain the future col names
                    for j, element in enumerate(line): # Loop through the elements of the line
                        # Add to a list the unique colnames and its position for filtering the cols
                        if element not in e_cols and element != "":
                            e_cols.append(element)
                            i_cols.append(j)
                    # Remove "Results" form the colnames and store the information.
                    line = [element.replace(" Results","")for element in line]
                
                file.append(line)
        # Check the integrity of the file, check the length of the colnames and the first col.
        if len(file[0]) != len(file[1]): # -1 for the extra \n for the strip 
            print("Error in the process of the file")

        else:
            with open(fname, "w") as o: # Save the data on the output file in csv format.
                # Remove the duplicated cols
                o.write("".join([",".join(np.array(line)[i_cols]) for line in file]))



# Schema clearance and null removal.
def scehmaC (fileName):
    raw_area_df = pl.read_csv(fileName)

    new_schema = {}
    for col in raw_area_df.columns:
        new_schema[col] = pl.Float64
    new_schema[raw_area_df.columns[0]] = pl.Utf8

    df = raw_area_df.cast(new_schema).fill_null(0)
    return df.clone()
    

# Remove the Areas with low representation
def min_area_R (raw_area_df, area_threshold):
    
    df =  raw_area_df.drop(
    list(np.array(raw_area_df.select(pl.col(pl.Float64)).columns)
         [np.array(((raw_area_df.fill_null(0).select(pl.col(pl.Float64)>area_threshold).sum()/raw_area_df.shape[0])<0.8).row(0))]))

    return df.clone()


# QC with high rsd drop
def QC_rsd_R (min_area_per_sample_df, rsd_area_threshold):
    
    df =  min_area_per_sample_df.drop(
    list(np.array(min_area_per_sample_df.select(pl.col(pl.Float64)).columns)
         [np.array((min_area_per_sample_df.filter(pl.col('Sample').str.starts_with('QC')).select(
    (pl.col(pl.Float64).std() / pl.col(pl.Float64).mean() * 100))>rsd_area_threshold).row(0))]))
    
    return df.clone()

# Ratio Balnk QC
def Ratio_B_QC (QC_desvest_df,bqc_threshold):
    
    bqc_df = QC_desvest_df.drop(list(np.array(QC_desvest_df.select(pl.col(pl.Float64)).columns)
                                 [np.array((((QC_desvest_df.filter(pl.col('Sample').str.starts_with('QC')).select(pl.col(pl.Float64).mean()))/(QC_desvest_df.filter(pl.col('Sample').str.starts_with('Blk')).select(pl.col(pl.Float64).mean())
     ))>bqc_threshold).row(0))]))
    
    return bqc_df.clone()


# ISTD curation
def curation_ISTD(preqc_istd_df, rsd_area_threshold):
    
    df =preqc_istd_df.drop(
    list(np.array(preqc_istd_df.select(pl.col(pl.Float64)).columns)
         [np.array((preqc_istd_df.select(
    (pl.col(pl.Float64).std() / pl.col(pl.Float64).mean() * 100))>rsd_area_threshold).row(0))]))
    
    return df.clone()