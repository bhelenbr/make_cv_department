import pandas as pd

# This to allow people to modify the Sponsor or Title for better formatting etc...
def merge_keep_old_columns(df_new, df_old, cols_from_old=[]):
    # Join old columns onto new dataframe by index
    df_merged = df_new.join(df_old[list(cols_from_old)], how="left", rsuffix="_old")

    # Overwrite new columns with old values where available
    for col in cols_from_old:
        if f"{col}_old" in df_merged:
            df_merged[col] = df_merged[f"{col}_old"].combine_first(df_merged[col])
            df_merged.drop(columns=f"{col}_old", inplace=True)
    return df_merged


def _unique_keys(index):
    # Index values as strings, with an occurrence counter so repeated IDs stay distinct
    ids = pd.Series(pd.Index(index).astype(str))
    counts = ids.groupby(ids).cumcount()
    return [f"{i}#{n}" for i, n in zip(ids, counts)]


def update_keep_old(df_new, df_old, cols_from_old=()):
    """Update an existing indexed table with a new report.

    Rows in df_new replace matching rows in df_old (matched by index, compared as
    strings so numeric and text IDs line up), except that the columns listed in
    cols_from_old keep the value already in df_old (so user edits survive).
    Rows that are only in df_old are kept rather than dropped.
    """
    name = df_new.index.name or df_old.index.name
    new = df_new.copy()
    old = df_old.copy()
    new.index = _unique_keys(new.index)
    old.index = _unique_keys(old.index)
    cols = [c for c in cols_from_old if c in old.columns]
    merged = merge_keep_old_columns(new, old, cols)
    old_only = old.loc[~old.index.isin(merged.index)]
    if not old_only.empty:
        merged = pd.concat([merged, old_only])
    merged.index = pd.Index([k.rsplit("#", 1)[0] for k in merged.index], name=name)
    return merged
        

def merge_and_dedup(dfs, ignore_cols=None, keep="first", keep_only_first_cols=False):
    """
    Combine an iterable/list of DataFrames by stacking rows and drop duplicates.

    Parameters
    ----------
    dfs : iterable of pandas.DataFrame
        Iterable (list/tuple/generator) of DataFrames to combine.
    ignore_cols : list of str
        Columns to ignore when identifying duplicates
    keep : {"first", "last", False}
        Which duplicate to keep (passed to drop_duplicates)
    keep_only_first_cols : bool
        If True, only keep columns that appear in the first non-empty dataframe
        from `dfs` (preserves their order). This is useful when later frames
        add extra columns you don't want included in the combined result.

    Returns
    -------
    pandas.DataFrame
    """
    if ignore_cols is None:
        ignore_cols = []
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

    # Build candidate frames from the provided iterable
    try:
        candidate_frames = list(dfs)
    except TypeError:
        raise TypeError("merge_and_dedup expects an iterable of DataFrames as 'dfs'")

    frames = [df for df in candidate_frames if not _is_empty_or_all_na(df)]

    if len(frames) == 0:
        # Return an empty DataFrame with the union of columns from inputs
        cols = pd.Index([])
        for cand in candidate_frames:
            if hasattr(cand, 'columns'):
                cols = cols.union(cand.columns)
        combined = pd.DataFrame(columns=cols)
    elif len(frames) == 1:
        combined = frames[0].copy().reset_index(drop=True)
    else:
        combined = pd.concat(frames, ignore_index=True)

    # Optionally restrict to columns present in the first (non-empty) frame
    if keep_only_first_cols and len(frames) >= 1:
        first_cols = list(frames[0].columns)
        cols_to_keep = [c for c in first_cols if c in combined.columns]
        combined = combined.loc[:, cols_to_keep].copy()

    # Columns to use for duplicate detection
    subset_cols = [c for c in combined.columns if c not in ignore_cols]

    deduped = combined.drop_duplicates(subset=subset_cols, keep=keep)

    return deduped