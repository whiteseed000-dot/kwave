import streamlit as st
import plotly.graph_objects as go
from data import load_data
from kondratieff import preprocess, bandpass_filter, detect_phase


st.set_page_config(layout='wide')
st.title('📈 台股康波模型（Kondratieff Wave）')


df = load_data()
df = preprocess(df)


df['cycle'] = bandpass_filter(df['log_price'])
df['phase'] = detect_phase(df['cycle'])


fig = go.Figure()
fig.add_trace(go.Scatter(
x=df.index,
y=df['Close'],
name='TAIEX'
))


fig.add_trace(go.Scatter(
x=df.index,
y=np.exp(df['cycle']),
name='K-wave',
yaxis='y2'
))


fig.update_layout(
yaxis2=dict(overlaying='y', side='right')
)


st.plotly_chart(fig, use_container_width=True)
