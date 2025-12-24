import shutil
import os
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

    if 'restrictions' not in st.session_state:
        st.session_state.restrictions = {}

    if 'enable_res_generation' not in st.session_state:
        st.session_state.enable_res_generation = False


def render_header():
    st.write('# 🎅🏻 Secret Santa')

    ss_desc = st.text_input('Descreva o identificador do seu sorteio', value='Amigo Secreto')
    if ss_desc is None: ss_desc = 'Amigo Secreto'

    col1, col2 = st.columns([0.69, 0.31], vertical_alignment='bottom')
    num_participants = col1.number_input('Número de participantes', min_value=2)
    clicked_generate_list = col2.button('Gerar lista de participantes', key='base_list')

    return num_participants, clicked_generate_list, ss_desc


def handle_header(num_participants):
    st.session_state.show_participants = True
    st.session_state.show_restrictions = False  # Reseta para garantir que vai sumir com o menu para nova geração
    st.session_state.num_participants = num_participants
    st.session_state.participants = [''] * st.session_state.num_participants
    del st.session_state.restrictions
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
    clicked_generate_restrictions = st.button('Gerar lista de restrições de sorteio', key='restriction_list',
                                                 use_container_width=True)

    return clicked_generate_restrictions

def handle_participants_form():
    if all(p.strip() for p in st.session_state.participants):
        st.session_state.show_restrictions = True
        
        # Inicializa dicionário das restrições (apenas 1 vez)
        if "restrictions" not in st.session_state:
            st.session_state.restrictions = {
                p: [] for p in st.session_state.participants
            }
    else:
        del st.session_state.restrictions
        st.error('Para avançar é necessário fornecer o nome de todas as pessoas.')


def render_restrictions_form():
    st.write('## ❌ Lista de restrições')
    st.info('Informe quais pessoas o referido participante **NÃO** pode tirar (além dele próprio).')

    for participant in st.session_state.participants:
        # Renderiza o multiselect sempre
        participant_opts = st.session_state.participants.copy()
        participant_opts.remove(participant)
        st.session_state.restrictions[participant] = st.multiselect(
            f'Escolha as pessoas que {participant} **NÃO** pode tirar (além dele próprio)',
            options=participant_opts,
            default=None,
            key=f'{participant}_restrictions'
        )

    with st.expander('_Sumário das restrições_'):
        for p in st.session_state.restrictions.keys():
            restrictions = st.session_state.restrictions[p]
            if restrictions == []:
                st.write(f'{p} não tem restrições')
            else:
                st.write(f'{p} não pode tirar {restrictions}')


    st.write('Se estiver tudo correto, clique abaixo para gerar os arquivos.')
    clicked_generate_secret_santa = st.button('Finalizar sorteio', key='submit_secret_santa',
                                                 use_container_width=True)

    return clicked_generate_secret_santa


def handle_restrictions_form():
    if all(
        len(st.session_state.restrictions[p]) < len(st.session_state.participants) 
        for p in st.session_state.participants):
        st.session_state.enable_res_generation = True
        
    else:
        st.session_state.enable_res_generation = False
        st.error('Para avançar é necessário que o usuário possa tirar pelo menos uma pessoa.')


def generate_res(ss_desc):
    ts = dt.datetime.now().strftime('%d-%m-%YT%H:%M:%S')
    filename = f'/tmp/{ss_desc}-{ts}.zip'
    
    ss = SecretSanta(st.session_state.participants, st.session_state.restrictions, ss_desc)
    with st.spinner('🎲 Gerando sorteio...'):
        try:
            ss.generate_drawing()
            ss.export_to_file(f'/tmp/{ss_desc}-{ts}/')  # Colocar timestamp para diferenciar...
            shutil.make_archive(f'/tmp/{ss_desc}-{ts}', 'zip', f'/tmp/{ss_desc}-{ts}/')
            shutil.rmtree(f'/tmp/{ss_desc}-{ts}/')

            return filename

        except TimeoutError:
            st.error('Não foi possível gerar o sorteio em tempo hábil. É possível que exista uma restrição impossível de ser resolvida. Tente novamente.')


def render_download(filename):
    st.success('✅ Sorteio finalizado!')

    with open(filename, 'rb') as file:
        was_downloaded = st.download_button('Clique aqui para baixar os resultados', mime='application/zip', 
                                               file_name=filename.split('/')[-1], data=file, use_container_width=True)
        
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
                if filename is not None: render_download(filename)


if __name__ == '__main__':
    main()
