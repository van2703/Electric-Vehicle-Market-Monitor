"""Build and execute the initial descriptive EDA notebook; never edit inputs."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPS = ROOT / '.eda_dependencies'
sys.path.insert(0, str(DEPS))
os.environ['PYTHONPATH'] = str(DEPS) + os.pathsep + os.environ.get('PYTHONPATH', '')
os.environ['MPLCONFIGDIR'] = str(ROOT / 'figures' / '.mplconfig')
import nbformat as nbf
from nbclient import NotebookClient

cells = []
def md(s): cells.append(nbf.v4.new_markdown_cell(s.strip()))
def code(s): cells.append(nbf.v4.new_code_cell(s.strip()))

md('''# EDA ô tô VinFast — nguồn cung, giá chào bán và thông điệp quảng cáo

**Phạm vi:** bốn nội dung mô tả: (1) chất lượng dữ liệu, (2) cơ cấu nguồn cung,
(3) mặt bằng giá chào bán, (4) thông điệp bán hàng. Chỉ phân tích ô tô VinFast.

Không suy luận số người mua, giá giao dịch, tăng trưởng thị trường hoặc tốc độ bán từ một snapshot.
Không dùng ngày đăng hay thời gian sửa file làm `crawl_date`. Không suy tên brand/model xe máy từ văn bản.
Lọc hãng bằng `carbrand_name == VinFast` (không phân biệt hoa thường) và đối chiếu mã hãng.
Tên model lấy trực tiếp từ `carmodel_name`, không phân tích văn bản để gán model.
Notebook sử dụng bảng làm việc trong bộ nhớ; xe máy nằm ngoài phạm vi.

**Chạy lại:** Python với pandas, numpy, matplotlib, nbformat, nbclient, ipykernel.
Chạy các ô từ trên xuống từ thư mục dự án hoặc `data visualization/`. Ảnh PNG được lưu vào `figures/`.
Các CSV tham chiếu chỉ được kiểm tra chất lượng; không gộp vào tập Cho Tot để tính tỷ trọng/giá.
''')
code(r'''
from pathlib import Path
import json, hashlib, re, unicodedata
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator
from matplotlib.colors import LinearSegmentedColormap
from IPython.display import display, Markdown, Image

ROOT = Path.cwd()
if not (ROOT / 'data' / 'raw').exists(): ROOT = ROOT.parent
assert (ROOT / 'data' / 'raw').exists(), 'Run from repository or data visualization/'
FIG = ROOT / 'figures'
FIG.mkdir(exist_ok=True)
BLUE, TEAL, AMBER, INK, MUTED = '#2563EB', '#0D9488', '#D97706', '#172B4D', '#64748B'
plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':11,
    'axes.spines.top':False, 'axes.spines.right':False,
    'axes.spines.left':False, 'axes.spines.bottom':False,
    'figure.facecolor':'#F5F7FB', 'axes.facecolor':'#F5F7FB',
    'text.color':INK, 'axes.labelcolor':MUTED, 'xtick.color':MUTED, 'ytick.color':INK,
    'axes.titlesize':15, 'axes.titleweight':'bold', 'axes.titlelocation':'left',
    'axes.titlepad':20, 'axes.labelpad':12, 'xtick.major.size':0, 'ytick.major.size':0,
    'grid.color':'#DCE3EE', 'grid.linewidth':.7, 'axes.axisbelow':True,
    'legend.frameon':False, 'figure.dpi':120, 'savefig.dpi':180})
pd.set_option('display.max_columns', 20)
sources = sorted(p for d in ['raw','processed'] for p in (ROOT/'data'/d).glob('*') if p.is_file())
hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
tables = {}
for p in sources:
    tables[p.name] = pd.DataFrame(json.loads(p.read_text(encoding='utf-8-sig'))) if p.suffix == '.json' else pd.read_csv(p)
saved = []
def chart_label(value):
    text=str(value).replace('VinFast ','')
    translations={'Dòng khác':'Other models','Thiếu tên mẫu':'Unknown model',
        'Mới':'New','Đã sử dụng':'Used','Không rõ':'Unknown',
        'Nhắc kèm/mua pin':'Battery included / purchased',
        'Nhắc thuê pin':'Battery rental',
        'Nhắc trả góp/trả trước':'Financing / down payment',
        'Nhắc khuyến mãi':'Promotions',
        'Nhắc đổi xe xăng':'ICE vehicle trade-in',
        'Nhắc bảo hành/hậu mãi':'Warranty / after-sales'}
    if text in translations: return translations[text]
    text=text.replace('TP Hồ Chí Minh','Ho Chi Minh City').replace('TP Hà Nội','Hanoi')
    if text.startswith('TP '): text=text[3:]+' City'
    return ''.join(c for c in unicodedata.normalize('NFD',text.replace('Đ','D').replace('đ','d')) if unicodedata.category(c)!='Mn')
def save(fig, name):
    fig.tight_layout(rect=(0,.055,1,.98),pad=1.7)
    fig.text(.025,.014,'VINFAST  /  CARS     •     Source: Cho Tot listing sample     •     Asking prices, not transaction prices',
             fontsize=8.5,color=MUTED)
    path = FIG / (name + '.png')
    fig.savefig(path, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    saved.append(path)
    display(Image(filename=str(path)))
def note(text): display(Markdown(text))
def barh(series, title, xlabel, name, color=BLUE):
    s = series.sort_index() if name.endswith('_year') else series.sort_values()
    fig, ax = plt.subplots(figsize=(12, max(5, len(s)*.43+2)))
    labels=[chart_label(x) for x in s.index]
    bars=ax.barh(labels, s.values, color=[color if v==s.max() else '#8FB2EB' for v in s],height=.6)
    percentage='(%)' in xlabel
    ax.bar_label(bars,labels=[f'{v:.1f}%' if percentage else f'{v:,.0f}' for v in s],padding=9,fontsize=11,color=INK)
    ax.set(title=title, xlabel=xlabel)
    if name.endswith('_year'): ax.set_ylabel('Manufacturing year (YYYY)')
    ax.set_xlim(0,max(s.max()*1.17,1))
    ax.xaxis.set_major_locator(MaxNLocator(nbins=5,integer=not percentage))
    ax.grid(axis='x')
    save(fig, name)
''')
md('''## 1. Chất lượng dữ liệu và điều kiện sử dụng

Kiểm kê mọi nguồn; chỉ khử trùng bảng làm việc Cho Tot theo `list_id`, giữ lần xuất hiện đầu tiên
trong thứ tự nguồn. Đây là quy tắc tái lập, không có nghĩa bản giữ lại mới nhất.
ID thiếu không được đưa vào bảng làm việc. Không sửa file gốc. CSV B2C không có ID nên
trùng toàn dòng/tựa đề chỉ là tín hiệu lặp nội dung, không đủ căn cứ kết luận trùng listing.
''')
code(r'''
audit=[]
for name, df in tables.items():
    serialized = df.apply(lambda col: col.map(lambda v: json.dumps(v, sort_keys=True, ensure_ascii=False) if isinstance(v,(dict,list)) else v))
    has_id='list_id' in df
    audit.append({'file':name, 'rows':len(df), 'columns':len(df.columns),
                  'missing_listing_id':int(df.list_id.isna().sum()) if has_id else None,
                  'unique_listing_ids':df.list_id.nunique() if has_id else None,
                  'duplicate_id_rows':int(df.list_id.dropna().duplicated().sum()) if has_id else None,
                  'exact_duplicate_rows':int(serialized.duplicated().sum())})
audit=pd.DataFrame(audit)
display(audit)
all_cars=tables['chotot_oto_raw.json']
vinfast_mask=all_cars.carbrand_name.str.strip().str.casefold().eq('vinfast')
raws={'Ô tô VinFast':all_cars.loc[vinfast_mask].copy()}
note(f'**Phạm vi:** {len(all_cars):,} dòng ô tô → {int(vinfast_mask.sum()):,} dòng VinFast; loại {int((~vinfast_mask).sum()):,} dòng hãng khác khỏi EDA. Xe máy không tham gia.')
display(raws['Ô tô VinFast'][['carbrand','carbrand_name']].drop_duplicates())
assert raws['Ô tô VinFast'].carbrand.nunique()==1
work={}
for vehicle, raw in raws.items():
    d=raw.dropna(subset=['list_id']).drop_duplicates('list_id',keep='first').copy()
    d['brand_code']=d.carbrand.astype('Int64')
    d['model_code']=d.carmodel.astype('Int64')
    d['brand']=d.carbrand_name.fillna('Thiếu tên hãng')
    d['model']=d.brand+' '+d.carmodel_name.fillna('Thiếu tên mẫu')
    d['vehicle_year']=pd.to_numeric(d.mfdate,errors='coerce')
    for col in ['price','mileage_v2']: d[col]=pd.to_numeric(d[col],errors='coerce')
    d['condition']=d.condition_ad_name.fillna('Không rõ')
    # Consistent source v3 province/city labels; retain original in separate field.
    d['region_original']=d.region_name
    d['region']=d.region_name_v3.fillna(d.region_name).str.replace(r'^Tp\s+', 'TP ',regex=True).str.strip()
    d['body_clean']=d.body.fillna('').map(lambda x: re.sub(r'\s+', ' ', str(x)).strip())
    work[vehicle]=d
    assert d.list_id.notna().all() and d.list_id.is_unique
    assert d.groupby(['brand_code','model_code']).model.nunique().le(1).all()
    note(f'**{vehicle}:** {len(raw):,} dòng → **{len(d):,} listing** sau quy tắc ID; chưa lọc theo giá/ODO.')
    note('**10 tin ngẫu nhiên kiểm tra nhãn nguồn (seed=42):**')
    display(d.sample(min(10,len(d)),random_state=42)[['list_id','subject','brand_code','model_code','brand','model']])
fields=['price','vehicle_year','mileage_v2','brand_code','model_code','region','area_name','body','orig_list_time','list_time']
missing=pd.DataFrame({v:d.reindex(columns=fields).isna().mean().mul(100) for v,d in work.items()}).T
display(missing.round(1))
names=['Asking price','Manufacturing year','Odometer','Brand code','Model code','Province / city','District','Description','Original listing timestamp','Listing timestamp']
s=pd.Series(missing.iloc[0].values,index=names).sort_values()
fig,ax=plt.subplots(figsize=(12,6.7))
ax.barh(s.index,[100]*len(s),color='#E7EDF5',height=.55)
bars=ax.barh(s.index,s.values,color=AMBER,height=.55)
ax.bar_label(bars,labels=[f'{v:.1f}%' for v in s],padding=8,color=INK)
ax.set(xlim=(0,111),xlabel='Missing values (% of listings)',title='Data completeness | Odometer has the largest gap')
ax.set_xticks([0,25,50,75,100]); ax.grid(axis='x')
save(fig,'01_missingness')
''')
code(r'''
flags=[]
for vehicle,d in work.items():
    for col in ['price','mileage_v2']:
        s=d[col].dropna(); q1,q3=s.quantile([.25,.75]); iqr=q3-q1
        flags.append({'vehicle':vehicle,'field':col,'missing':int(d[col].isna().sum()),
          'negative':int((s<0).sum()),'zero':int((s==0).sum()),
          'IQR_outside':int(((s<q1-1.5*iqr)|(s>q3+1.5*iqr)).sum()),
          'min':s.min(),'p25':q1,'median':s.median(),'p75':q3,'max':s.max()})
display(pd.DataFrame(flags))
for vehicle,d in work.items():
    note(f'**{vehicle} — 5 mức giá thấp nhất để kiểm tra trả trước/giá mồi:**')
    display(d.nsmallest(5,'price')[['list_id','subject','price','condition','vehicle_year']])
    display(d.groupby(['brand_code','model_code']).size().describe().to_frame('số tin / cặp mã'))
note('**Diễn giải:** Ngoại lệ IQR chỉ là cờ kiểm tra, không bị xóa tự động. Giá thấp có thể là tiền trả trước; giá cao có thể là xe khác phân khúc. Thiếu ODO không được điền bằng 0. `mfdate` ô tô là năm sản xuất theo tên trường. Mã đầy đủ không đồng nghĩa nhãn người bán chọn chính xác.')
processed=tables['ev_market_cleaned.csv']
note(f'**Không dùng processed để ước lượng cơ cấu:** {len(processed):,} dòng nhưng chỉ {processed.list_id.nunique():,} ID. Ba nguồn B2C và benchmark không có cùng thiết kế mẫu với Cho Tot.')
''')
md('''## 2. Cơ cấu nguồn cung

Mỗi listing có trọng số 1; số tin không phải số xe bán được hoặc số người mua. Cùng một xe có thể
được đăng với nhiều ID và chưa được phát hiện bằng khử trùng ID.
Top 12 chỉ hiển thị một phần danh mục; số lượng đầy đủ có trong bảng.
Vùng sử dụng `region_name_v3` do nguồn cung cấp, dự phòng `region_name`; giữ nhãn cũ để đối chiếu.
Đây là phân bố trong mẫu, không phải mật độ theo dân số hay độ phủ toàn thị trường.
''')
code(r'''
for vehicle,d in work.items():
    prefix='car'
    for field,label in [('model','models'),('region','provinces / cities')]:
        counts=d[field].value_counts(dropna=False)
        display(pd.DataFrame({'n':counts,'share_pct':counts/len(d)*100}).round(2))
        barh(counts.head(12),f'Top {min(12,len(counts))} {label} by listing count | N={len(d):,} listings','Number of listings',f'02_{prefix}_{field}')
    ct=pd.crosstab(d.model,d.condition)
    order=d.model.value_counts().head(10).index
    chart=ct.reindex(order[::-1]).rename(index=chart_label,columns=chart_label)
    ax=chart.plot.barh(stacked=True,figsize=(12,7),width=.62,color=[BLUE,TEAL,'#94A3B8'])
    for container in ax.containers:
        ax.bar_label(container,labels=[str(int(v)) if v>=8 else '' for v in container.datavalues],label_type='center',color='white',fontsize=10)
    for y,total in enumerate(chart.sum(axis=1)): ax.text(total+3,y,str(total),va='center',fontsize=10)
    ax.set(title='New vs. used | Top 10 models by listing count',xlabel='Number of listings',ylabel='',xlim=(0,chart.sum(axis=1).max()*1.13))
    ax.grid(axis='x')
    ax.legend(loc='lower right',ncols=2,bbox_to_anchor=(1,1.01))
    save(ax.figure,f'02_{prefix}_condition')
    conditions=d.condition.value_counts()
    display(pd.DataFrame({'n':conditions,'share_pct':conditions/len(d)*100}).round(2))
    regions=d.region.value_counts()
    note(f'**Cơ cấu mẫu:** tình trạng phổ biến nhất là **{conditions.index[0]}** ({conditions.iloc[0]:,} tin; {conditions.iloc[0]/len(d):.1%}). Vùng nhiều tin nhất là **{regions.index[0]}** ({regions.iloc[0]:,} tin; {regions.iloc[0]/len(d):.1%}). Cả hai là cơ cấu tin đăng, không phải lựa chọn của người mua; mẫu tập trung theo địa lý có thể ảnh hưởng mặt bằng giá chung.')
    years=d.vehicle_year.value_counts().sort_index()
    barh(years,'Listing composition by manufacturing year','Number of listings',f'02_{prefix}_year')
    leader=d.model.value_counts()
    note(f'**Nhận xét {vehicle}:** model nhiều tin nhất là **{leader.index[0]}**, {leader.iloc[0]:,}/{len(d):,} tin ({leader.iloc[0]/len(d):.1%}). Top 3 model chiếm {leader.head(3).sum()/len(d):.1%}. Đây là mức tập trung nguồn cung trong mẫu, không phải thị phần doanh số.')
    display(d[['region_original','region']].drop_duplicates().sort_values(['region','region_original']))
    region_models=pd.crosstab(d.region,d.model).reindex(index=d.region.value_counts().head(8).index,columns=d.model.value_counts().head(8).index,fill_value=0)
    fig,ax=plt.subplots(figsize=(12,7))
    im=ax.imshow(region_models,cmap=LinearSegmentedColormap.from_list('market',['#EEF3FB','#A6C7EF','#174BA0']),aspect='auto')
    ax.set_xticks(range(len(region_models.columns)),[chart_label(s) for s in region_models.columns],rotation=0)
    ax.set_yticks(range(len(region_models)),[chart_label(s) for s in region_models.index])
    for i in range(len(region_models)):
        for j in range(len(region_models.columns)):
            n=region_models.iloc[i,j]
            ax.text(j,i,str(n),ha='center',va='center',color='white' if n>region_models.to_numpy().max()/2 else 'black')
    ax.set_title('Supply concentration | Top 8 regions × top 8 models')
    ax.set_xticks(np.arange(len(region_models.columns)+1)-.5,minor=True)
    ax.set_yticks(np.arange(len(region_models)+1)-.5,minor=True)
    ax.grid(which='minor',color='#F5F7FB',linewidth=3); ax.tick_params(which='minor',length=0)
    fig.colorbar(im,ax=ax,label='Number of listings',shrink=.8,pad=.03)
    save(fig,'02_car_region_model')
''')
md('''## 3. Mặt bằng giá chào bán

Giá nguồn là VND; biểu đồ chuyển sang triệu đồng. Chỉ loại giá thiếu/không dương khỏi đồ thị giá,
ghi số loại ra; không cắt ngọn phân phối và không tự xóa ngoại lệ. Báo cáo median, P25–P75 và n.
Boxplot chỉ hiển thị các model có ít nhất 10 quan sát giá, tối đa 10 model nhiều tin nhất.
Giá quảng cáo có thể là giá trả trước hoặc tùy điều kiện pin, cần đọc tin để xác minh.
Không gán tứ phân vị giá thành phân khúc nhu cầu gia đình/đô thị/phổ thông.
''')
code(r'''
price_summaries={}
for vehicle,d in work.items():
    prefix='car'
    p=d.loc[d.price.gt(0)].copy(); p['price_million']=p.price/1e6
    note(f'**{vehicle}:** dùng {len(p):,}/{len(d):,} tin có giá dương; loại khỏi đồ thị {len(d)-len(p):,} tin giá thiếu/không dương.')
    stats=p.groupby('model').price_million.agg(n='size',median='median',p25=lambda s:s.quantile(.25),p75=lambda s:s.quantile(.75),minimum='min',maximum='max').sort_values('n',ascending=False)
    price_summaries[vehicle]=stats
    display(stats.round(2))
    fig,axes=plt.subplots(1,2,figsize=(13,5.8))
    axes[0].hist(p.price_million,bins=35,color=BLUE,edgecolor='#F5F7FB',linewidth=1)
    axes[0].set(title='Full price range | Linear scale',xlabel='Asking price (million VND)',ylabel='Number of listings')
    axes[1].hist(p.price_million,bins=np.geomspace(p.price_million.min(),p.price_million.max(),36),color=TEAL,edgecolor='#F5F7FB',linewidth=1)
    axes[1].set_xscale('log')
    axes[1].set(title='Full price range | Log scale',xlabel='Asking price (million VND, log scale)',ylabel='Number of listings')
    axes[1].set_xticks([10,50,100,250,500,1000]); axes[1].xaxis.set_major_formatter(FuncFormatter(lambda v,pos:f'{v:,.0f}'))
    for ax in axes:
        ax.axvline(p.price_million.median(),color=AMBER,lw=2,ls='--',label=f'Median: {p.price_million.median():,.0f} million VND')
        ax.legend(fontsize=10); ax.grid(axis='y')
    fig.suptitle(f'Asking price distribution  /  {len(p):,} listings with positive prices',fontsize=17,fontweight='bold',x=.04,ha='left')
    save(fig,f'03_{prefix}_price_distribution')
    eligible=stats.loc[stats.n.ge(10)].head(10).sort_values('median').index
    if len(eligible):
        fig,ax=plt.subplots(figsize=(12,7.5))
        ax.boxplot([p.loc[p.model.eq(m),'price_million'] for m in eligible],vert=False,
                   tick_labels=[f'{chart_label(m)}  ·  {stats.loc[m,"n"]:.0f} listings' for m in eligible],showfliers=True,patch_artist=True,widths=.55,
                   boxprops={'facecolor':'#D8E6FB','edgecolor':BLUE,'linewidth':1.3},
                   medianprops={'color':AMBER,'linewidth':2.4},whiskerprops={'color':'#7C93B3'},capprops={'color':'#7C93B3'},
                   flierprops={'marker':'o','markersize':3.5,'markeredgecolor':'#7C93B3','alpha':.6})
        ax.grid(axis='x')
        ax.set(xlabel='Asking price (million VND)',title='Prices by model | Box: P25–P75 · Orange line: median')
        save(fig,f'03_{prefix}_model_prices')
    display(p.groupby('condition').price_million.agg(n='size',median='median',p25=lambda s:s.quantile(.25),p75=lambda s:s.quantile(.75)).round(2))
    display(p.groupby(['model','condition']).price_million.agg(n='size',median='median',p25=lambda s:s.quantile(.25),p75=lambda s:s.quantile(.75)).round(2))
    display(p.groupby('region').price_million.agg(n='size',median='median',p25=lambda s:s.quantile(.25),p75=lambda s:s.quantile(.75)).sort_values('n',ascending=False).round(2))
    # Conditional views avoid treating mixed models as a depreciation estimate.
    common=p.model.value_counts().index[0]
    m=p.loc[p.model.eq(common)]
    display(m.groupby(['vehicle_year','condition']).price_million.agg(n='size',median='median').round(2))
    od=m.loc[m.mileage_v2.ge(0)]
    note(f'**Độ phủ ODO:** toàn bộ VinFast thiếu {d.mileage_v2.isna().sum():,}/{len(d):,} giá trị ({d.mileage_v2.isna().mean():.1%}); scatter chỉ dùng {len(od)}/{len(m)} tin của {common}. Không thể giả định nhóm khai báo ODO đại diện cho nhóm không khai báo.')
    fig,axes=plt.subplots(1,2,figsize=(13,5.8),sharey=True)
    for ax in axes:
        ax.scatter(od.mileage_v2,od.price_million,alpha=.65,s=45,color=BLUE,edgecolors='white',linewidth=.6)
        ax.set(xlabel='Odometer (km)',ylabel='Asking price (million VND)')
        ax.grid(alpha=.65)
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v,pos:f'{v:,.0f}'))
    axes[0].set_title('Full odometer range | Linear scale')
    axes[0].xaxis.set_major_locator(MaxNLocator(4))
    axes[1].set_xscale('symlog',linthresh=1000)
    axes[1].set_xticks([0,1000,10000,100000])
    axes[1].set_title('Symlog scale | Includes 0 km')
    axes[1].set_xlabel('Odometer (km) · linear ≤1,000 km, log above')
    axes[1].xaxis.set_major_formatter(FuncFormatter(lambda v,pos:f'{v:,.0f}'))
    fig.suptitle(f'{chart_label(common)}  /  Asking price vs. odometer · {len(od)} listings',fontsize=17,fontweight='bold',x=.04,ha='left')
    save(fig,f'03_{prefix}_price_odo')
    q=p.price_million.quantile([.25,.5,.75])
    note(f'**Nhận xét {vehicle}:** median toàn mẫu **{q.loc[.5]:.2f} triệu VND**, khoảng giữa 50% tin **{q.loc[.25]:.2f}–{q.loc[.75]:.2f} triệu**. So sánh mới/cũ toàn mẫu chịu ảnh hưởng cơ cấu model và năm xe; scatter không chứng minh tác động khấu hao. Model nhiều tin nhất dùng ở scatter là {common}; thiếu ODO bị loại riêng khỏi scatter, không coi là 0 km.')
''')
md('''## 4. Thông điệp bán hàng

Quy tắc từ khóa chỉ áp dụng cho `subject + body`, **không dùng để suy brand/model**.
Gắn nhiều nhãn trên một tin là hợp lệ: tổng tỷ lệ có thể vượt 100%.
Những nhãn này nghĩa là “có nhắc đến”, không xác nhận ưu đãi còn hiệu lực hay tình trạng pin thực tế.
Chuẩn hóa bỏ dấu và chữ thường để tìm cụm từ. Đính kèm pattern và ví dụ để kiểm tra sai dương/sai âm.
Không gọi kết quả này là sentiment, ý định mua hay hiệu quả khuyến mãi.
''')
code(r'''
def normalize(text):
    text=unicodedata.normalize('NFD',str(text).lower().replace('đ','d'))
    return re.sub(r'\s+',' ', ''.join(c for c in text if unicodedata.category(c)!='Mn'))
patterns={
 'Nhắc kèm/mua pin':r'\b(kem pin|bao pin|gom pin|mua pin|pin mua|da mua pin)\b',
 'Nhắc thuê pin':r'\b(thue pin|pin thue)\b',
 'Nhắc trả góp/trả trước':r'\b(tra gop|tra truoc|gop 0|lai suat)\b',
 'Nhắc khuyến mãi':r'\b(khuyen mai|khuyen mai|uu dai|giam gia|ctkm|voucher|khuyen ma[iy])\b',
 'Nhắc đổi xe xăng':r'\b(doi|thu|thu cu doi moi)\b.{0,60}\bxe xang\b|\bxe xang\b.{0,60}\b(doi|voucher|ho tro|giam)\b',
 'Nhắc bảo hành/hậu mãi':r'\b(bao hanh|hau mai|bao duong|bao tri)\b'
}
display(pd.Series(patterns,name='Regex trên văn bản không dấu').to_frame())
for vehicle,d in work.items():
    prefix='car'
    text=(d.subject.fillna('')+' '+d.body.fillna('')).map(normalize)
    flags=pd.DataFrame({label:text.str.contains(pattern,regex=True) for label,pattern in patterns.items()},index=d.index)
    counts=flags.sum().sort_values(ascending=False)
    display(pd.DataFrame({'tin_co_nhac':counts,'pct_all_listings':counts/len(d)*100}).round(2))
    barh(counts/len(d)*100,f'Sales messages mentioned | N={len(d):,} listings','Share of listings (%) · labels may overlap',f'04_{prefix}_messages','#6B5B95')
    examples=[]
    for label,pattern in patterns.items():
        # First three matches per label, with matched span in normalized text.
        for ix in flags.index[flags[label]][:3]:
            match=re.search(pattern,text.loc[ix]); start,end=match.span()
            examples.append({'nhan':label,'list_id':d.loc[ix,'list_id'],'subject':d.loc[ix,'subject'],
                             'doan_khop_khong_dau':text.loc[ix][max(0,start-50):end+80]})
    display(pd.DataFrame(examples))
    both=flags['Nhắc kèm/mua pin'] & flags['Nhắc thuê pin']
    note(f'**Kiểm tra {vehicle}:** {int(both.sum())} tin cùng nhắc mua/kèm pin và thuê pin. Có thể là mô tả lựa chọn hoặc phủ định; không tự gán tình trạng pin độc quyền.')
    note(f'**Nhận xét {vehicle}:** thông điệp phổ biến nhất theo bộ quy tắc là **{counts.index[0]}**, {counts.iloc[0]} tin ({counts.iloc[0]/len(d):.1%}). Đây là kết quả của bộ từ khóa công khai, chưa phải nhãn đã kiểm định thủ công.')
''')
md('''## Tổng hợp và giới hạn sử dụng

- Dùng kết quả để mô tả **mẫu tin đăng đang có**, lựa chọn nhóm model cần khảo sát và xác định
  vùng giá chào bán để đọc sâu; không suy rộng thành thị phần doanh số.
- Ô tô VinFast có tên model từ trường nguồn; đây là nhãn người đăng chọn, chưa xác minh bằng thông số xe. Xe máy nằm ngoài phạm vi.
- Không trộn B2C/benchmark vào Cho Tot: nguồn và đơn vị quan sát khác nhau.
- Không có snapshot lặp lại/crawl timestamp đáng tin cậy: không tính tăng trưởng hoặc thanh khoản.
- Phần giá giữ cả tin có khả năng quảng cáo trả trước; đọc các tin giá thấp đã in ở mục 1
  trước khi dùng kết quả để định giá. Thiếu năm hiệu lực của benchmark cũng hạn chế so sánh.
- Các ví dụ từ khóa là mẫu kiểm tra, không đo precision/recall. Cần gán nhãn thủ công
  một mẫu độc lập nếu muốn sử dụng feature thông điệp cho mô hình tiếp theo.

**Điều kiện trước bước phân tích tiếp theo:** xác minh nhãn model ô tô, ý nghĩa năm xe,
giá toàn xe so với trả trước, và chọn phiên bản địa giới hành chính. Không cần đổi tên mã bằng phỏng đoán.
''')
code(r'''
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in hashes.items()), 'Source changed'
assert all(d.list_id.is_unique for d in work.values())
assert len(saved)==len(set(saved)) and all(p.stat().st_size>1000 for p in saved)
note(f'**Kiểm tra hoàn tất:** {len(sources)} file nguồn giữ nguyên SHA-256; ID bảng VinFast không trùng; **{len(saved)} ảnh PNG** đã lưu. Không xuất/ghi đè staging hay merge nguồn.')
display(pd.DataFrame({'figure':[p.relative_to(ROOT).as_posix() for p in saved]}))
''')

if __name__ == '__main__':
    dest=ROOT/'data visualization'/'01_eda_vinfast_oto.ipynb'
    dest.parent.mkdir(exist_ok=True)
    nb=nbf.v4.new_notebook(cells=cells, metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}})
    nbf.write(nb,dest)
    client=NotebookClient(nb,timeout=180,resources={'metadata':{'path':str(ROOT)}},kernel_name='python3')
    try:
        client.execute()
    finally:
        nbf.write(nb,dest)
    nbf.validate(nb)
    assert not any(o.output_type=='error' for c in nb.cells if c.cell_type=='code' for o in c.outputs)
    print(f'Executed notebook: {dest}')
