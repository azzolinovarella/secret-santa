import shutil
import os
from multiprocessing import pool
import datetime as dt
import streamlit as st
from src.secret_santa import SecretSanta


def initialize_states():
    if 'show_participants' not in st.session_state:
        st.session_state.show_participants = False

    if 'show_restrictions' not in st.session_state:
        st.session_state.show_restrictions = False

    if 'participants' not in st.session_state:
        st.session_state.participants = []

    if 'participants_and_restrictions' not in st.session_state:
        st.session_state.participants_and_restrictions = {}

    if 'enable_res_generation' not in st.session_state:
        st.session_state.enable_res_generation = False


def render_header():
    st.write('# 🎅🏻 Secret Santa')

    ss_desc = st.text_input('Descreva o identificador do seu sorteio', placeholder='Amigo Secreto')
    if ss_desc is None: ss_desc = 'Amigo Secreto'
    ss_desc = ss_desc.title().strip().replace(' ', '')

    col1, col2 = st.columns([0.69, 0.31], vertical_alignment='bottom')
    num_participants = col1.number_input('Número de participantes', min_value=2)
    clicked_generate_list = col2.button('Gerar lista de participantes', key='base_list')

    return num_participants, clicked_generate_list, ss_desc


def handle_header(num_participants):
    st.session_state.show_participants = True
    st.session_state.show_restrictions = False  # Reseta para garantir que vai sumir com o menu para nova geração
    st.session_state.num_participants = num_participants
    st.session_state.participants = [''] * st.session_state.num_participants
    del st.session_state.participants_and_restrictions
    st.session_state.enable_res_generation = False


def render_participants_form():
    st.write('## 📋 Lista de participantes')
    st.info(
        '''Informe o nome de cada participante do sorteio. 
            Se houver pessoas com o mesmo nome, inclua o sobrenome.'''
    )

    # Gera campo a campo para informar os nomes
    for i in range(st.session_state.num_participants):
        st.session_state.participants[i] = st.text_input(
            f'Insira o nome do participante {i + 1}',
            placeholder='Fulano da Silva',
            value=st.session_state.participants[i],
            key=f'participant_{i}'
        )

    # Botão para gerar restrições
    clicked_generate_restrictions = st.button('Gerar lista de restrições de sorteio', key='restriction_list')

    return clicked_generate_restrictions

def handle_participants_form():
    if all(p.strip() for p in st.session_state.participants):
        st.session_state.show_restrictions = True
        
        # Inicializa dicionário das restrições (apenas 1 vez)
        if "participants_and_restrictions" not in st.session_state:
            st.session_state.participants_and_restrictions = {
                p: [] for p in st.session_state.participants
            }
    else:
        del st.session_state.participants_and_restrictions
        st.error('Para avançar é necessário fornecer o nome de todas as pessoas.')


def render_restrictions_form():
    st.write('## ❌ Lista de restrições')
    st.info('Informe quais pessoas o referido participante **NÃO** pode tirar.')

    for participant in st.session_state.participants:
        # Renderiza o multiselect sempre
        st.session_state.participants_and_restrictions[participant] = st.multiselect(
            f'Escolha as pessoas que {participant} **NÃO** pode tirar',
            options=st.session_state.participants,
            default=([participant]),
            key=f'{participant}_restrictions'
        )

    with st.expander('_Sumário das restrições_'):
        for p in st.session_state.participants_and_restrictions.keys():
            st.write(f'{p} não pode tirar {st.session_state.participants_and_restrictions[p]}')

    st.write('Se estiver tudo correto, clique abaixo para gerar os arquivos.')
    clicked_generate_secret_santa = st.button('Finalizar sorteio', key='submit_secret_santa')

    return clicked_generate_secret_santa


def handle_restrictions_form():
    if all(
        len(st.session_state.participants_and_restrictions[p]) < len(st.session_state.participants) 
        for p in st.session_state.participants):
        st.session_state.enable_res_generation = True
        
    else:
        st.session_state.enable_res_generation = False
        st.error('Para avançar é necessário que o usuário possa tirar pelo menos uma pessoa.')


def generate_res(ss_desc):
    ts = dt.datetime.now().strftime('%d-%m-%YT%H:%M:%S')
    filename = f'/tmp/{ss_desc}-{ts}.zip'
    
    with st.spinner('Gerando sorteio...'):
        ss = SecretSanta(st.session_state.participants_and_restrictions, ss_desc)
        ss.export_to_file(f'/tmp/{ss_desc}-{ts}/')  # Colocar timestamp para diferenciar...
        shutil.make_archive(f'/tmp/{ss_desc}-{ts}', 'zip', f'/tmp/{ss_desc}-{ts}/')
        shutil.rmtree(f'/tmp/{ss_desc}-{ts}/')

    return filename


def render_download(filename):
    st.success('✅ Sorteio finalizado!')

    with open(filename, 'rb') as file:
        was_downloaded = st.download_button('Clique aqui para baixar os resultados', mime='application/zip', 
                                            file_name=filename.split('/')[-1], data=file)
        
    if was_downloaded:
        os.remove(filename, 'rb')


def main():
    # Inicializa estados (necessário para poder trabalhar com múltiplos botoões)
    initialize_states()

    # Entrada de número de participantes
    num_participants, clicked_generate_list, ss_desc = render_header()
    
    # Quando clicar no primeiro botão
    if clicked_generate_list:
        handle_header(num_participants)

    # Se deve mostrar os campos de participante
    if st.session_state.show_participants:
        clicked_generate_restrictions = render_participants_form()

        if clicked_generate_restrictions:
            handle_participants_form()

        #  Mostrar tela de restrições (fora do botão) 
        if st.session_state.show_restrictions:
            clicked_generate_secret_santa = render_restrictions_form()

            if clicked_generate_secret_santa:
                handle_restrictions_form()

            if st.session_state.enable_res_generation:
                filename = generate_res(ss_desc)
                render_download(filename)

if __name__ == '__main__':
    main()
