import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Vendas",
    page_icon="💰",
    layout="wide",
)

# --- Carregamento dos dados ---
df = pd.read_csv("Restaurante/BD_CERTO.csv")

# --- Conversão de Datas ---

# --- Função para formatar valores em euro ---
def formatar_euro(valor):
    # Ponto como milhar e vírgula como decimal
    return f"€{valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
faturamento_diario = df.groupby('Data')['Total Venda'].mean().reset_index()


# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

# Filtro de Gerente
gerentes_disponiveis = sorted(df['Gerente'].unique())
gerentes_selecionados = st.sidebar.multiselect("Gerente", gerentes_disponiveis, default=gerentes_disponiveis)

# Filtro de Produto
produtos_disponiveis = sorted(df['Produto'].unique())
produtos_selecionados = st.sidebar.multiselect("Produto", produtos_disponiveis, default=produtos_disponiveis)

# Filtro de Tipo de Compra
tipos_disponiveis = sorted(df['Tipo de Compra'].unique())
tipos_selecionados = st.sidebar.multiselect("Tipo de Compra", tipos_disponiveis, default=tipos_disponiveis)

# Filtro de Método de Pagamento
metodos_disponiveis = sorted(df['Método de Pagamento'].unique())
metodos_selecionados = st.sidebar.multiselect("Método de Pagamento", metodos_disponiveis, default=metodos_disponiveis)

# --- Filtragem do DataFrame ---
df_filtrado = df[
    (df['Gerente'].isin(gerentes_selecionados)) &
    (df['Produto'].isin(produtos_selecionados)) &
    (df['Tipo de Compra'].isin(tipos_selecionados)) &
    (df['Método de Pagamento'].isin(metodos_selecionados))
]

# --- Conteúdo Principal ---
st.title("💰 Dashboard de Vendas")
st.markdown("Explore os dados de vendas. Utilize os filtros à esquerda para refinar sua análise.")

# --- Métricas Principais ---
st.subheader("Métricas Gerais")

if not df_filtrado.empty:
    faturamento_total = df_filtrado['Total Venda'].sum()
    quantidade_total = df_filtrado['Quantidade'].sum()
    venda_media = df_filtrado['Total Venda'].mean()
    produto_mais_vendido = df_filtrado['Produto'].mode()[0]
else:
    faturamento_total = quantidade_total = venda_media = 0
    produto_mais_vendido = ""

col1, col2, col3, col4 = st.columns(4)
col1.metric("Faturamento Total", formatar_euro(faturamento_total))
col2.metric("Quantidade Total", f"{int(quantidade_total):,}".replace(',', '.'))  # inteiro com ponto como milhar
col3.metric("Venda Média", formatar_euro(venda_media))
col4.metric("Produto Mais Vendido", produto_mais_vendido)

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")
col_graf1, col_graf2 = st.columns(2)
with col_graf1:
    if not df_filtrado.empty:
        # Calcular o total vendido por gerente e pegar top 5
        vendas_por_gerente = df_filtrado.groupby('Gerente')['Total Venda'].sum().sort_values(ascending=False).reset_index()
        vendas_top5 = vendas_por_gerente.head(5)

        # Criar gráfico de barras com gradiente rosa/roxo
        fig = px.bar(
            vendas_top5,
            x='Gerente',
            y='Total Venda',
            title='Total Vendido por Gerente',
            labels={'Gerente': 'Gerente', 'Total Venda': 'Valor Total Vendido (€)'},
            text=vendas_top5['Total Venda'].apply(lambda x: f"€{x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')),  # formato europeu
            color='Total Venda',
            color_continuous_scale='Purples'  # gradiente roxo
        )

        # Formatar eixo Y apenas com vírgula decimal
        fig.update_yaxes(tickprefix="€", separatethousands=False, tickformat=".2f")

        # Aumentar tamanho dos labels e título
        fig.update_layout(
            xaxis_title_font=dict(size=16),
            yaxis_title_font=dict(size=16),
            title_font=dict(size=20)
        )
        fig.update_traces(textfont_size=14)

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Nenhum dado para exibir no gráfico de gerentes.")
with col_graf2:
    if not df_filtrado.empty:
        # Calcular a quantidade total por produto usando o DataFrame filtrado
        quantidade_por_produto = df_filtrado.groupby('Produto')['Quantidade'].sum().sort_values(ascending=False).reset_index()

        # Criar gráfico de barras com gradiente rosa/roxo
        fig = px.bar(
            quantidade_por_produto,
            x='Produto',
            y='Quantidade',
            title='Quantidade Total de Produto Vendido',
            labels={'Produto': 'Produto', 'Quantidade': 'Quantidade'},
            text=quantidade_por_produto['Quantidade'].apply(lambda x: f"{int(x)}"),  # valor no topo sem casas decimais
            color='Quantidade',
            color_continuous_scale='Purples'
        )

        # Aumentar tamanho dos labels e título
        fig.update_layout(
            xaxis_title_font=dict(size=16),
            yaxis_title_font=dict(size=16),
            title_font=dict(size=20)
        )

        # Aumentar o texto no topo das barras
        fig.update_traces(textfont_size=14)

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")
col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        # Calcular o total vendido por método de pagamento usando o DataFrame filtrado
        vendas_valor_por_pagamento = df_filtrado.groupby('Método de Pagamento')['Total Venda'].sum().sort_values(ascending=False).reset_index()

        # Criar gráfico de barras com gradiente rosa/roxo
        fig = px.bar(
            vendas_valor_por_pagamento,
            x='Método de Pagamento',
            y='Total Venda',
            title='Total Vendido por Método de Pagamento',
            labels={'Método de Pagamento': 'Método de Pagamento', 'Total Venda': 'Valor Total Vendido (€)'},
            text=vendas_valor_por_pagamento['Total Venda'].apply(lambda x: f"€{x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')),  # vírgula decimal e ponto milhar
            color='Total Venda',
            color_continuous_scale='Purples'
        )

        # Formatar eixo Y apenas com vírgula decimal
        fig.update_yaxes(tickprefix="€", separatethousands=False, tickformat=".2f")

        # Aumentar tamanho dos labels e título
        fig.update_layout(
            xaxis_title_font=dict(size=16),
            yaxis_title_font=dict(size=16),
            title_font=dict(size=20)
        )

        # Aumentar o texto no topo das barras
        fig.update_traces(textfont_size=14)

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de vendas por método de pagamento.")
with col_graf4:
    if not df_filtrado.empty:
        # Contar número de vendas por método de pagamento usando o DataFrame filtrado
        vendas_por_pagamento = df_filtrado['Método de Pagamento'].value_counts().reset_index()
        vendas_por_pagamento.columns = ['Método de Pagamento', 'Número de Vendas']

        # Criar gráfico de rosca com gradiente roxo
        fig = px.pie(
            vendas_por_pagamento,
            names='Método de Pagamento',
            values='Número de Vendas',
            title='Número de Vendas por Método de Pagamento',
            hole=0.6,  # transforma em rosca
            color='Método de Pagamento',  # usar categórico
            color_discrete_sequence=px.colors.qualitative.Dark2  # gradiente roxo
        )


        # Adicionar valores no gráfico com vírgula se necessário
        fig.update_traces(
            textposition='inside',
            text=vendas_por_pagamento['Número de Vendas'].apply(lambda x: f"{x}"),
            textfont_size=14
        )

        # Aumentar tamanho do título
        fig.update_layout(title_font=dict(size=20))

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de número de vendas por método de pagamento.")

col_graf5 = st.columns(1)[0]

with col_graf5:
    if not df_filtrado.empty:
        # Criar coluna de valor total por venda
        df_filtrado['Total Venda'] = df_filtrado['Preço'] * df_filtrado['Quantidade']

                # Converter datas (ISO, seguro)
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')

        # Remover linhas inválidas
        df = df.dropna(subset=['Data'])

        # Calcular faturamento diário médio
        df['Total Venda'] = df['Preço'] * df['Quantidade']
        faturamento_diario = df.groupby('Data')['Total Venda'].mean().reset_index()

        # Ordenar por data
        faturamento_diario = faturamento_diario.sort_values('Data')

        # Calcular faturamento médio por dia
        faturamento_diario = df_filtrado.groupby('Data')['Total Venda'].mean().reset_index()

        df_filtrado['Data'] = pd.to_datetime(df_filtrado['Data'])


        # Criar gráfico de linha
        fig = px.line(
            faturamento_diario,
            x='Data',
            y='Total Venda',
            title='Faturamento Médio Diário',
            labels={'Data': 'Data', 'Total Venda': 'Faturamento Médio (€)'},
            markers=True
        )

        # Formatar eixo Y com vírgula decimal
        fig.update_yaxes(tickprefix="€", separatethousands=False, tickformat=".2f")

        # Aumentar tamanho dos labels e título
        fig.update_layout(
            xaxis_title_font=dict(size=16),
            yaxis_title_font=dict(size=16),
            title_font=dict(size=20)
        )

        # Adicionar valores no topo dos pontos com vírgula
        fig.update_traces(
            text=faturamento_diario['Total Venda'].apply(lambda x: f"€{x:.2f}".replace('.', ',')),
            textposition="top center",
            textfont_size=12
        )

        # Exibir no Streamlit
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Nenhum dado para exibir no gráfico de faturamento médio diário.")
# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")

st.dataframe(df_filtrado)
