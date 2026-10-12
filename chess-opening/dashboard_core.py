"""Hàm dữ liệu thuần pandas, dùng chung cho dashboard và kiểm tra."""
import pandas as pd

RATINGS = ['<1200', '1200–1599', '1600–1999', '≥2000']
REQUIRED = ['game_id','date','result','white_elo','black_elo','recognition_status',
            'opening_family','opening_variant']

def prepare(frame):
    missing = sorted(set(REQUIRED) - set(frame.columns))
    if missing:
        raise ValueError('Thiếu cột: ' + ', '.join(missing))
    d = frame.copy()
    if d['game_id'].isna().any() or d['game_id'].duplicated().any():
        raise ValueError('Mã ván thiếu hoặc trùng.')
    d['date'] = pd.to_datetime(d['date'], errors='raise')
    if d['date'].isna().any():
        raise ValueError('Ngày thi đấu bị thiếu.')
    for c in ['white_elo','black_elo']:
        d[c] = pd.to_numeric(d[c], errors='raise')
        if not d[c].gt(0).all():
            raise ValueError('Elo thiếu hoặc không hợp lệ.')
    if not d['result'].isin(['1-0','0-1','1/2-1/2']).all():
        raise ValueError('Kết quả thi đấu không hợp lệ.')
    if not d['recognition_status'].isin(['matched','no_catalog_match']).all():
        raise ValueError('Trạng thái nhận diện không hợp lệ.')
    known = d['recognition_status'].eq('matched')
    for c in ['opening_family','opening_variant']:
        if d.loc[known,c].fillna('').str.strip().eq('').any():
            raise ValueError('Ván đã nhận diện thiếu nhãn khai cuộc.')
    d['year_month'] = d['date'].dt.strftime('%Y-%m')
    d['avg_elo'] = (d['white_elo'] + d['black_elo']) / 2
    d['elo_diff'] = d['white_elo'] - d['black_elo']
    d['rating_group'] = pd.cut(d['avg_elo'],[0,1200,1600,2000,float('inf')],labels=RATINGS,right=False)
    d['white_win'] = d['result'].eq('1-0').astype(int)
    d['draw'] = d['result'].eq('1/2-1/2').astype(int)
    d['black_win'] = d['result'].eq('0-1').astype(int)
    d['white_score'] = d['white_win'] + 0.5 * d['draw']
    d['black_score'] = 1 - d['white_score']
    return d

def filter_games(data, months, ratings, gap=None):
    mask = data['year_month'].isin(months) & data['rating_group'].isin(ratings)
    if gap is not None:
        mask &= data['elo_diff'].abs().le(gap)
    return data.loc[mask].copy()

def summarize(data, keys, side='white'):
    if side not in ['white','black']:
        raise ValueError('Màu quân không hợp lệ')
    a = data.groupby(keys, observed=True).agg(n_games=('game_id','size'),
        white_wins=('white_win','sum'),draws=('draw','sum'),black_wins=('black_win','sum'),
        white_score_sum=('white_score','sum'),black_score_sum=('black_score','sum'),
        avg_elo=('avg_elo','mean')).reset_index()
    a['score_rate'] = 100 * a[side+'_score_sum'] / a['n_games']
    for count,rate in [('white_wins','white_win_pct'),('draws','draw_pct'),('black_wins','black_win_pct')]:
        a[rate] = 100*a[count]/a['n_games']
    return a

def popularity(data):
    a = summarize(data,['opening_family'])
    a['popularity_pct'] = 100*a['n_games']/len(data)
    return a.sort_values(['n_games','opening_family'],ascending=[False,True])

def monthly_popularity(data, families, months):
    grid = pd.MultiIndex.from_product([families,months],names=['opening_family','year_month'])
    counts = data.groupby(['opening_family','year_month'],observed=True).size()
    a = counts.reindex(grid,fill_value=0).rename('n_games').reset_index()
    totals = data.groupby('year_month').size()
    a['month_total'] = a['year_month'].map(totals)
    a['popularity_pct'] = 100*a['n_games']/a['month_total']
    return a
