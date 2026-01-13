import pandas as pd

# This to allow people to modify the Sponsor or Title for better formatting etc...
def merge_keep_old_columns(df_new, df_old, cols_from_old=[]):
    # Join old columns onto new dataframe by index
    df_merged = df_new.join(df_old[list(cols_from_old)], how="left", rsuffix="_old")

    # Overwrite new columns with old values where available
    for col in cols_from_old:
        if col in df_merged:
            df_merged[col] = df_merged[f"{col}_old"].combine_first(df_merged[col])
            df_merged.drop(columns=f"{col}_old", inplace=True)
    return df_merged
        

def merge_and_dedup(df1, df2, ignore_cols, keep="first"):
    """
    Merge two DataFrames by stacking rows and drop duplicates,
    ignoring columns in ignore_cols when determining duplicates.

    Parameters
    ----------
    df1, df2 : pandas.DataFrame
        DataFrames to combine
    ignore_cols : list of str
        Columns to ignore when identifying duplicates
    keep : {"first", "last", False}
        Which duplicate to keep (passed to drop_duplicates)

    Returns
    -------
    pandas.DataFrame
    """
    # Filter out empty or all-NA DataFrames before concatenation to avoid
    # pandas FutureWarning about dtype inference changing in future versions.
    def _is_empty_or_all_na(df):
        if df is None:
            return True
        # No rows or no columns -> treat as empty
        if df.shape[0] == 0 or df.shape[1] == 0:
            return True
        # All values are NA
        try:
            return bool(df.isna().all().all())
        except Exception:
            return False

    frames = [df for df in (df1, df2) if not _is_empty_or_all_na(df)]

    if len(frames) == 0:
        # Return an empty DataFrame with the union of columns from inputs
        cols = pd.Index([])
        if hasattr(df1, 'columns'):
            cols = cols.union(df1.columns)
        if hasattr(df2, 'columns'):
            cols = cols.union(df2.columns)
        combined = pd.DataFrame(columns=cols)
    elif len(frames) == 1:
        combined = frames[0].copy().reset_index(drop=True)
    else:
        combined = pd.concat(frames, ignore_index=True)

    # Columns to use for duplicate detection
    subset_cols = [c for c in combined.columns if c not in ignore_cols]

    deduped = combined.drop_duplicates(subset=subset_cols, keep=keep)

    return deduped