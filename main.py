import shutil
import os
import datetime as dt
import streamlit as st
from src.secret_santa import SecretSanta

def main():
    st.write('# 🎅🏻 Secret Santa')

    # Inicializa estados (necessário para poder trabalhar com múltiplos botoões)
    if 'show_participants' not in st.session_state:
        st.session_state.show_participants = False

    if 'show_restrictions' not in st.session_state:
        st.session_state.show_restrictions = False

    if 'participants' not in st.session_state:
        st.session_state.participants = []

    if 'participants_and_restrictions' not in st.session_state:
        st.session_state.participants_and_restrictions = {}

    # Entrada de número de participantes
    ss_desc = st.text_input('Descreva o identificador do seu sorteio', placeholder='Amigo Secreto')
    if ss_desc is None: ss_desc = 'Amigo Secreto'
    ss_desc = ss_desc.title().strip().replace(' ', '')

    col1, col2 = st.columns([0.69, 0.31], vertical_alignment='bottom')
    num_participants = col1.number_input('Número de participantes', min_value=2)
    clicked_generate_list = col2.button('Gerar lista de participantes', key='base_list')

    # Quando clicar no primeiro botão
    if clicked_generate_list:
        st.session_state.show_participants = True
        st.session_state.show_restrictions = False  # Reseta para garantir que vai sumir com o menu para nova geração
        st.session_state.num_participants = num_participants
        st.session_state.participants = [''] * st.session_state.num_participants
        del st.session_state.participants_and_restrictions

    # Se deve mostrar os campos de participante
    if st.session_state.show_participants:
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
        _, center, _ = st.columns(3)
        clicked_generate_restrictions = center.button('Gerar lista de restrições de sorteio', key='restriction_list')

        if clicked_generate_restrictions:

            # Validação
            if all(p.strip() for p in st.session_state.participants):
                st.session_state.show_restrictions = True
                
                # Inicializa dicionário das restrições (apenas 1 vez)
                if "participants_and_restrictions" not in st.session_state:
                    st.session_state.participants_and_restrictions = {
                        p: [] for p in st.session_state.participants
                    }
            else:
                st.error('Para avançar é necessário fornecer o nome de todas as pessoas.')

        #  Mostrar tela de restrições (fora do botão) 
        if st.session_state.show_restrictions:
            st.write('## ❌ Lista de restrições')
            st.info('Informe quais pessoas o referido participante **NÃO** pode tirar.')

            for participant in st.session_state.participants:
                # Renderiza o multiselect sempre
                selected = st.multiselect(
                    f'Escolha as pessoas que {participant} **NÃO** pode tirar',
                    options=st.session_state.participants,
                    default=([participant]),
                    key=f'{participant}_restrictions'
                )

                # Atualiza no session_state
                st.session_state.participants_and_restrictions[participant] = selected

            with st.expander('_Sumário das restrições_'):
                for p in st.session_state.participants_and_restrictions.keys():
                    st.write(f'{p} não pode tirar {st.session_state.participants_and_restrictions[p]}')

            st.write('Se estiver tudo correto, clique abaixo para gerar os arquivos.')
            clicked_generate_secret_santa = st.button('Finalizar sorteio', key='submit_secret_santa')

            if clicked_generate_secret_santa:
                with st.spinner('Gerando sorteio...'):
                    ts = dt.datetime.now().strftime('%d-%m-%YT%H:%M:%S')
                    ss = SecretSanta(st.session_state.participants_and_restrictions, ss_desc)
                    ss.export_to_file(f'/tmp/{ss_desc}-{ts}/')  # Colocar timestamp para diferenciar...
                    shutil.make_archive(f'/tmp/{ss_desc}-{ts}', 'zip', f'/tmp/{ss_desc}-{ts}/')
                    shutil.rmtree(f'/tmp/{ss_desc}-{ts}/')

                st.success('✅ Sorteio finalizado!')
                with open(f'/tmp/{ss_desc}-{ts}.zip', 'rb') as file:
                    was_downloaded = st.download_button('Clique aqui para baixar os resultados', mime='application/zip', 
                                                        file_name=f'{ss_desc}-{ts}.zip', data=file)

                if was_downloaded:
                    os.remove(f'/tmp/{ss_desc}-{ts}.zip', 'rb')

if __name__ == '__main__':
    main()
