from pathlib import Path
import json
from html import escape
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dashboard_core import RATINGS, prepare, filter_games, summarize, monthly_popularity

st.set_page_config(page_title='Khai cuộc cờ vua',page_icon='♟️',layout='wide')
ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT/'data/games_dashboard.csv.gz'
META_FILE = ROOT/'data/dataset_info.json'
COLORS = {'Trắng thắng':'#277DA1','Hòa':'#A8ADB5','Đen thắng':'#F28E2B'}

@st.cache_data(show_spinner='Đang đọc dữ liệu…')
def load_data(path, modified, size):
    return prepare(pd.read_csv(path))

def chart(fig, key, height=440):
    fig.update_layout(template='plotly_white',height=height,
        font=dict(family='Arial, sans-serif',size=14,color='#233C46'),
        paper_bgcolor='white',plot_bgcolor='white',
        margin=dict(l=15,r=35,t=65,b=85),
        legend=dict(orientation='h',yanchor='top',y=-0.19,x=0,font=dict(size=12)),
        legend_title_text='',title_font_size=17)
    fig.update_xaxes(automargin=True,gridcolor='#E9EEF0',zeroline=False)
    fig.update_yaxes(automargin=True,gridcolor='#E9EEF0',zeroline=False)
    st.plotly_chart(fig,use_container_width=True,theme=None,key=key,
        config={'displaylogo':False,'scrollZoom':False,
        'toImageButtonOptions':{'format':'png','filename':key,'width':1400,'height':height,'scale':2}})

def note(text):
    st.markdown('<div class="reading-note">'+escape(text)+'</div>',unsafe_allow_html=True)

def month_axis(fig):
    fig.update_xaxes(type='category',categoryorder='array',categoryarray=selected_months,
        tickmode='array',tickvals=selected_months,
        ticktext=[m[5:]+'/'+m[:4] for m in selected_months],title='Tháng thi đấu')


def table_download(df,name):
    st.download_button('Tải bảng số liệu CSV',df.to_csv(index=False).encode('utf-8-sig'),
                       file_name=name+'.csv',mime='text/csv',key='dl_'+name)

def results_chart(a, label, title):
    # Explicit graph objects avoid Express offset groups splitting stacked bars.
    fig=go.Figure()
    for column,name in [('white_win_pct','Trắng thắng'),('draw_pct','Hòa'),('black_win_pct','Đen thắng')]:
        fig.add_trace(go.Bar(x=a[column],y=a[label],name=name,orientation='h',
            offsetgroup='results',alignmentgroup='results',marker_color=COLORS[name],
            text=[f'{v:.1f}%' if v>=5 else '' for v in a[column]],
            textposition='inside',insidetextanchor='middle',textfont=dict(color='white',size=13),
            customdata=a[['n_games']].to_numpy(),
            hovertemplate='%{y}<br>'+name+': %{x:.2f}%<br>Số ván: %{customdata[0]:,}<extra></extra>'))
    fig.update_layout(title=title,barmode='stack',bargap=0.28,
        xaxis_title='Tỷ lệ kết quả (%)',yaxis_title=None)
    fig.update_yaxes(categoryorder='array',categoryarray=a[label].tolist(),autorange='reversed')
    fig.update_xaxes(range=[0,100],ticksuffix='%')
    return fig

st.markdown("""<style>
.stApp {background:#F5F7F9; color:#18333D;}
[data-testid="stMainBlockContainer"] {max-width:1380px;padding-top:2rem;}
[data-testid="stSidebar"] {background:#EDF2F4;}
[data-testid="stMetric"] {background:white;border:1px solid #DDE6EA;border-top:3px solid #148078;
border-radius:12px;padding:16px 20px;}
[data-testid="stMetricValue"] {color:#125C59;}
[data-testid="stPlotlyChart"] {border:1px solid #E0E7EB;border-radius:12px;overflow:hidden;}
[data-baseweb="tab-list"] {gap:14px;}
[data-baseweb="tab"] {font-size:16px;}
h3 {padding-top:1.2rem !important;}
.hero {background:#143E48;border-radius:16px;padding:26px 30px;margin-bottom:20px;color:white;}
.hero h1 {color:white;font-size:32px;padding:5px 0 10px;}
.hero p {color:#D5E7E9;margin:0;}
.eyebrow {color:#91D7CD;font-size:12px;font-weight:700;letter-spacing:2px;}
.reading-note {background:#E9F3F1;border-left:4px solid #148078;padding:12px 16px;
border-radius:6px;margin:4px 0 18px;line-height:1.6;color:#244741;}
</style>
<div class="hero"><div class="eyebrow">LICHESS • RATED BLITZ • 2015</div>
<h1>Khám phá khai cuộc cờ vua</h1>
<p>Mức độ phổ biến, kết quả thực chiến và sự thay đổi theo thời gian</p></div>
""",unsafe_allow_html=True)

if not DATA_FILE.exists():
    st.error('Thiếu data/games_dashboard.csv.gz. Hãy tải đủ thư mục data từ bộ ZIP đã tạo trên Colab.')
    st.stop()
try:
    stat=DATA_FILE.stat()
    data=load_data(str(DATA_FILE),stat.st_mtime_ns,stat.st_size)
except Exception as error:
    st.error(f'Không đọc được dữ liệu: {error}')
    st.stop()
if data.empty:
    st.info('Tệp dữ liệu chưa có ván đấu.')
    st.stop()
info={}
if META_FILE.exists():
    try:
        info=json.loads(META_FILE.read_text(encoding='utf-8'))
    except (ValueError,OSError):
        st.warning('Không đọc được thông tin phiên bản dữ liệu.')
months=sorted(data['year_month'].unique())
with st.sidebar:
    st.header('♟ Bộ lọc phân tích')
    st.caption('Chọn phạm vi trước khi đọc hoặc chụp biểu đồ.')
    if len(months)>1:
        first,last=st.select_slider('Khoảng tháng',options=months,value=(months[0],months[-1]))
        selected_months=[m for m in months if first<=m<=last]
    else:
        selected_months=months
        st.caption('Tháng: '+months[0])
    selected_ratings=st.multiselect('Nhóm Elo trung bình',RATINGS,default=RATINGS)
    side_label=st.radio('Tỷ lệ điểm theo bên', ['Trắng','Đen'],horizontal=True,help='Thắng = 1 điểm; hòa = 0,5; thua = 0. Tỷ lệ điểm khác tỷ lệ thắng.')
    side='white' if side_label=='Trắng' else 'black'
    min_n=int(st.number_input('Số ván tối thiểu để so sánh',min_value=1,max_value=10000,value=200,step=50))
    gap=None
    if st.checkbox('Giới hạn chênh lệch Elo'):
        gap=int(st.number_input('|Elo Trắng − Elo Đen| tối đa',min_value=0,max_value=3000,value=100,step=50))
    st.caption('Bộ lọc áp dụng cho toàn bộ ứng dụng. Lựa chọn khai cuộc trong từng biểu đồ chỉ đổi phần hiển thị.')
    if st.button('Đọc lại dữ liệu'):
        load_data.clear()
        st.rerun()
    st.caption('Nút này đọc lại tệp đã cung cấp, không tải thêm ván từ Lichess.')

base=filter_games(data,selected_months,selected_ratings,gap)
if base.empty:
    st.info('Không có ván phù hợp. Hãy chọn thêm nhóm Elo hoặc mở rộng bộ lọc.')
    st.stop()
known=base.loc[base['recognition_status'].eq('matched')].copy()
a,b,c,d=st.columns(4)
a.metric('Ván sau lọc',f'{len(base):,}')
b.metric('Nhận diện được',f'{len(known):,}',help='Độ bao phủ, không phải độ chính xác phân loại.')
c.metric('Nhóm khai cuộc',f'{known["opening_family"].nunique():,}')
d.metric('Tỷ lệ hòa',f'{100*base["draw"].mean():.2f}%')
st.caption(f'{selected_months[0]} đến {selected_months[-1]} • '+', '.join(selected_ratings)+
           f' • Tỷ lệ điểm {side_label} • Bao phủ {100*len(known)/len(base):.2f}%')
if known.empty:
    st.info('Các ván trong phạm vi hiện tại chưa nhận diện được khai cuộc.')
    table_download(base,'van_chua_nhan_dien')
    st.stop()

with st.expander('Tỷ lệ điểm (%) nghĩa là gì?',expanded=True):
    st.markdown(f'**Đang xem bên {side_label}.** Tỷ lệ điểm = **(số ván thắng + 0,5 × số ván hòa) / tổng số ván × 100%**.')
    st.caption('Ví dụ: 45 thắng, 10 hòa, 45 thua → tỷ lệ thắng 45%, tỷ lệ điểm 50%. Đây là kết quả cả ván, không phải điểm đánh giá thế cờ.')

PALETTE=['#147D92','#C16B2F','#7663A6','#2D9575','#CE5268','#A18B25','#4377BA','#805741','#58777E','#AC4F99']
all_families=data.loc[data['recognition_status'].eq('matched'),'opening_family'].value_counts().index.tolist()
family_colors={name:PALETTE[i%len(PALETTE)] for i,name in enumerate(all_families)}

overall=summarize(known,['opening_family'],side).sort_values(['n_games','opening_family'],ascending=[False,True])
overall['popularity_pct']=100*overall['n_games']/len(known)
families=overall['opening_family'].tolist()
tabs=st.tabs(['Tổng quan','Xu hướng','So sánh hiệu quả','Dữ liệu và phương pháp'])

with tabs[0]:
    st.subheader('C1 · Khai cuộc phổ biến')
    control,_=st.columns([1,2])
    with control:
        top_n=st.select_slider('Số nhóm hiển thị',options=[5,10,15,20],value=10)
    top=overall.head(top_n)
    fig=px.bar(top.sort_values('n_games'),x='popularity_pct',y='opening_family',orientation='h',
        text_auto='.2f',hover_data=['n_games'],labels={'popularity_pct':'Tỷ trọng (%)','opening_family':'Nhóm khai cuộc','n_games':'Số ván'},
        title=f'Top {top_n} theo số ván trong phạm vi lọc')
    fig.update_traces(marker_color='#147D92',texttemplate='%{x:.2f}%',textposition='outside',cliponaxis=False)
    fig.update_xaxes(range=[0,top['popularity_pct'].max()*1.17])
    chart(fig,'C1_dashboard',max(360,top_n*29+140))
    leader=top.iloc[0]
    note(f"{leader['opening_family']} đứng đầu với {leader['n_games']:,} ván ({leader['popularity_pct']:.2f}%). Các nhóm đang hiển thị chiếm {top['popularity_pct'].sum():.2f}% số ván nhận diện được.")
    st.caption('Mẫu số: tất cả ván nhận diện được sau lọc, kể cả các nhóm ngoài Top N.')
    st.subheader('C3 · Thắng, hòa và thua')
    outcomes=overall.loc[overall['n_games'].ge(min_n)].head(top_n)
    if outcomes.empty:
        st.info('Chưa có nhóm đủ số ván tối thiểu.')
    else:
        chart(results_chart(outcomes,'opening_family',f'Cơ cấu kết quả · n ≥ {min_n}'),'C3_dashboard',max(350,len(outcomes)*33+150))
        note('Mỗi thanh cộng lại bằng 100%. Ba màu thể hiện kết quả của Trắng, hòa và Đen; lựa chọn màu quân chỉ thay đổi chỉ số tỷ lệ điểm.')
        st.dataframe(outcomes[['opening_family','n_games','score_rate']].rename(columns={
            'opening_family':'Khai cuộc','n_games':'Số ván','score_rate':f'Tỷ lệ điểm {side_label} (%)'}).round(2),hide_index=True,use_container_width=True)

with tabs[1]:
    st.subheader('C2 · Xu hướng sử dụng')
    selected=st.multiselect('Khai cuộc hiển thị trên C2',families,default=families[:5],key='c2_families')
    if selected:
        trend=monthly_popularity(known,selected,selected_months)
        fig=px.line(trend,x='year_month',y='popularity_pct',color='opening_family',color_discrete_map=family_colors,markers=True,
            hover_data=['n_games','month_total'],labels={'year_month':'Tháng','popularity_pct':'Tỷ trọng (%)','n_games':'Số ván'},
            title='Tỷ trọng theo tháng · Mẫu số gồm mọi khai cuộc')
        fig.update_traces(connectgaps=False,line_width=3,marker_size=7)
        month_axis(fig)
        chart(fig,'C2_dashboard')
        ends=trend.pivot(index='opening_family',columns='year_month',values='popularity_pct')
        if len(selected_months)>1:
            delta=(ends[selected_months[-1]]-ends[selected_months[0]]).dropna()
            if not delta.empty:
                biggest=delta.abs().idxmax()
                note(f'{biggest} thay đổi {delta[biggest]:+.2f} điểm phần trăm giữa tháng đầu và cuối trong phạm vi lọc. Đây là thay đổi tỷ trọng, không phải thay đổi số ván tuyệt đối.')
        table_download(trend,'C2_xu_huong')
    else:
        st.info('Chọn ít nhất một khai cuộc.')
    st.subheader('C7 · Hiệu quả theo tháng')
    focus_options=[r for r in RATINGS if r in selected_ratings]
    focus7=st.selectbox('Nhóm Elo dùng cho C7',focus_options,index=focus_options.index('1600–1999') if '1600–1999' in focus_options else 0)
    month_min=int(st.number_input('Số ván tối thiểu mỗi ô khai cuộc × tháng của C7',min_value=1,max_value=10000,value=50,step=50))
    focus=known.loc[known['rating_group'].eq(focus7)]
    stats=summarize(focus,['opening_family','year_month'],side)
    eligibility=stats.assign(enough=stats['n_games'].ge(month_min)).groupby('opening_family').agg(months_enough=('enough','sum'),total=('n_games','sum'))
    candidates=eligibility.loc[eligibility['months_enough'].ge(4)].sort_values('total',ascending=False).index.tolist()
    if len(selected_months)<4 or not candidates:
        st.info('C7 cần ít nhất 4 tháng và một khai cuộc đủ mẫu trong ít nhất 4 tháng. Hãy mở rộng phạm vi nếu cần.')
    else:
        chosen=st.multiselect('Khai cuộc so sánh trên C7',candidates,default=candidates[:5],key='c7_families')
        if chosen:
            grid=pd.MultiIndex.from_product([chosen,selected_months],names=['opening_family','year_month'])
            c7=stats.set_index(['opening_family','year_month']).reindex(grid).reset_index()
            c7['n_games']=c7['n_games'].fillna(0).astype(int)
            c7['display_score']=c7['score_rate'].where(c7['n_games'].ge(month_min))
            fig=px.line(c7,x='year_month',y='display_score',color='opening_family',color_discrete_map=family_colors,markers=True,
                hover_data=['n_games'],labels={'year_month':'Tháng','display_score':f'Tỷ lệ điểm {side_label} (%)'},
                title=f'Elo {focus7} · n ≥ {month_min} mỗi ô')
            fig.update_traces(connectgaps=False,line_width=3,marker_size=7)
            month_axis(fig)
            zoom7=st.checkbox('Phóng to vùng tỷ lệ điểm để đọc biến động',value=False,key='zoom7')
            values=c7['display_score'].dropna()
            bounds=[max(0,float(values.min())-5),min(100,float(values.max())+5)] if zoom7 and not values.empty else [0,100]
            fig.update_yaxes(range=bounds)
            fig.add_hline(y=50,line_dash='dot',line_color='#687A83')
            if zoom7:
                st.caption('Trục tung đang thu hẹp; xem nhãn trục khi so sánh mức biến động.')
            chart(fig,'C7_dashboard')
            st.caption('Ô thiếu mẫu để trống. Ngưỡng hiển thị không bảo đảm độ tin cậy thống kê.')
            common=c7.pivot(index='year_month',columns='opening_family',values='display_score').dropna()
            if len(common)>=4:
                stability=common.std(ddof=0).rename('Độ lệch chuẩn (điểm phần trăm)').reset_index()
                st.caption(f'So sánh độ lệch chuẩn trên cùng {len(common)} tháng đủ mẫu.')
                st.dataframe(stability.round(2),hide_index=True,use_container_width=True)
                best=stability.iloc[:,1].idxmin()
                note(f"{stability.loc[best,'opening_family']} có độ lệch chuẩn thấp nhất trong các nhóm được chọn: {stability.iloc[best,1]:.2f} điểm phần trăm trên {len(common)} tháng chung. Kết quả mô tả mẫu, không bảo đảm sự ổn định trong tương lai.")
            else:
                st.info('Không đủ 4 tháng chung để so sánh độ ổn định giữa các nhóm đã chọn.')

with tabs[2]:
    st.subheader('C4 · Hiệu quả theo trình độ')
    heat_names=overall.head(10)['opening_family'].tolist()
    heat=summarize(known,['opening_family','rating_group'],side)
    heat=heat.loc[heat['opening_family'].isin(heat_names)].copy()
    heat['display_score']=heat['score_rate'].where(heat['n_games'].ge(min_n))
    z=heat.pivot(index='opening_family',columns='rating_group',values='display_score').reindex(index=heat_names,columns=selected_ratings)
    n=heat.pivot(index='opening_family',columns='rating_group',values='n_games').reindex(index=heat_names,columns=selected_ratings).fillna(0)
    labels=z.map(lambda v:'' if pd.isna(v) else f'{v:.1f}%')
    fig=go.Figure(go.Heatmap(z=z.to_numpy(),x=selected_ratings,y=heat_names,text=labels.to_numpy(),texttemplate='%{text}',
        customdata=n.to_numpy(),zmin=0,zmax=100,colorscale='RdBu',hoverongaps=False,colorbar_title=f'Điểm {side_label}<br>(%)',
        hovertemplate='%{y}<br>Elo %{x}<br>Tỷ lệ điểm %{z:.2f}%<br>Số ván %{customdata}<extra></extra>'))
    fig.update_layout(title=f'Tỷ lệ điểm {side_label} · n ≥ {min_n}')
    fig.update_yaxes(autorange='reversed')
    chart(fig,'C4_dashboard',590)
    note(f'Đang xem tỷ lệ điểm của bên {side_label}. Màu xanh: trên 50%; màu đỏ: dưới 50%. Ô trống chưa đủ số ván hoặc không có quan sát, không phải 0%.')

    st.subheader('C5 · Độ phổ biến và hiệu quả')
    scatter=overall.loc[overall['n_games'].ge(min_n)]
    if scatter.empty:
        st.info('Không có nhóm đủ mẫu để so sánh.')
    else:
        fig=px.scatter(scatter,x='popularity_pct',y='score_rate',hover_name='opening_family',hover_data=['n_games','avg_elo'],
            labels={'popularity_pct':'Độ phổ biến (%)','score_rate':f'Tỷ lệ điểm {side_label} (%)'},title='Mỗi điểm là một nhóm khai cuộc đủ mẫu')
        fig.update_traces(marker=dict(size=10,color='#147D92',opacity=0.8,line=dict(width=1,color='white')))
        fig.add_hline(y=50,line_dash='dot',line_color='gray')
        chart(fig,'C5_dashboard')
        note(f'Có {len(scatter)} nhóm đạt ngưỡng {min_n} ván. Điểm càng sang phải: càng phổ biến; càng cao: bên {side_label} thu được nhiều điểm hơn. Chưa điều chỉnh cơ cấu Elo hay lợi thế màu quân.')

    st.subheader('C6 · So sánh các biến thể')
    focus6=st.selectbox('Nhóm Elo dùng cho C6',focus_options,index=focus_options.index('1600–1999') if '1600–1999' in focus_options else 0)
    variant_data=known.loc[known['rating_group'].eq(focus6) & known['opening_variant'].ne(known['opening_family'])]
    variants=summarize(variant_data,['opening_family','opening_variant'],side)
    eligible=variants.loc[variants['n_games'].ge(min_n)]
    families6=eligible.groupby('opening_family').agg(n_variants=('opening_variant','size'),total=('n_games','sum'))
    families6=families6.loc[families6['n_variants'].ge(2)].sort_values('total',ascending=False).index.tolist()
    if not families6:
        st.info('Không có nhóm với ít nhất 2 biến thể đủ mẫu trong phạm vi hiện tại.')
    else:
        family6=st.selectbox('Nhóm khai cuộc dùng cho C6',families6)
        c6=eligible.loc[eligible['opening_family'].eq(family6)].sort_values('n_games',ascending=False).head(8).copy()
        c6['variant_label']=c6['opening_variant'].str.replace(family6+':','',regex=False).str.strip()
        chart(results_chart(c6,'variant_label',f'{family6} · Elo {focus6} · n ≥ {min_n}'),'C6_dashboard',max(350,len(c6)*42+150))
        note(f'Đang so sánh {len(c6)} nhãn biến thể của {family6} trong nhóm Elo {focus6}; mỗi nhãn có ít nhất {min_n} ván.')
        st.caption('Mỗi ván được gán nhãn khớp sau cùng; một nhãn tổng quát không tự bao gồm mọi nhánh con đã gán nhãn khác.')
        st.dataframe(c6[['opening_variant','n_games','score_rate']].rename(columns={'opening_variant':'Biến thể','n_games':'Số ván','score_rate':f'Tỷ lệ điểm {side_label} (%)'}).round(2),hide_index=True,use_container_width=True)

with tabs[3]:
    st.subheader('Dữ liệu trong phạm vi lọc')
    st.caption('Bảng và CSV dưới đây gồm cả các ván chưa nhận diện, khớp bộ lọc tháng, Elo và chênh lệch Elo ở thanh bên.')
    cols=['game_id','date','rating_group','white_elo','black_elo','result','recognition_status','opening_family','opening_variant']
    for optional in ['eco_original','opening_original','matched_ply']:
        if optional in base.columns:
            cols.append(optional)
    st.dataframe(base[cols].head(1000),hide_index=True,use_container_width=True)
    st.caption(f'Hiển thị tối đa 1.000 dòng; CSV tải xuống chứa đủ {len(base):,} ván sau lọc.')
    table_download(base[cols],'du_lieu_sau_loc')
    st.subheader('Cách tính và giới hạn')
    st.markdown('''- **Tỷ trọng:** số ván của nhóm chia cho toàn bộ ván nhận diện được trong cùng phạm vi lọc.
- **Tỷ lệ điểm:** (số thắng + 0,5 × số hòa) / số ván × 100%, tính riêng cho màu quân đã chọn.
- **Elo:** dùng trung bình Elo Trắng và Đen để phân nhóm.
- **Nhận diện:** vị trí có tên khớp sau cùng trong 36 ply đầu theo danh mục đã lưu. Không dùng Stockfish.
- **Lấy mẫu:** khoảng 5% Rated Blitz theo hàm băm mã định danh và seed cố định; không chọn theo kết quả.
- Dữ liệu mô tả mẫu lịch sử năm 2015. Không suy ra tác động nhân quả hay xu hướng hiện tại.
- Nhãn khớp sớm có thể chỉ là nhóm tổng quát. Độ bao phủ không phải độ chính xác.
- Chênh lệch giữa nhóm có thể liên quan đến trình độ, cơ cấu người chơi và dao động lấy mẫu.''')
    st.markdown('[Nguồn ván đấu](https://database.lichess.org/) · [Danh mục khai cuộc](https://github.com/lichess-org/chess-openings)')
    if info:
        st.caption('Thời điểm tạo bộ dữ liệu ứng dụng (UTC): '+str(info.get('generated_at_utc','Chưa có')))
        with st.expander('Thông tin phiên bản dữ liệu'):
            st.json(info)
