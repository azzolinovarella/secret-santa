from secret_santa import SecretSanta

# PARTICIPANTS_N_RESTICTIONS = {
#     'Carol':    ['Carol'],
#     'Felipe':   ['Felipe'],
#     'Fernando': ['Fernando'],
#     'Gabriela': ['Gabriela'],
#     'Lucas':    ['Lucas'],
#     'Nanci':    ['Nanci'],
#     'Natália':  ['Natália'],
#     'Nilce':    ['Nilce', 'Nanci'],
#     'Nilson':   ['Nilson', 'Nanci'],
#     'Nilton':   ['Nilton']
# }

PARTICIPANTS_N_RESTICTIONS = {
    'Bárbara': ['Bárbara', 'Felipe'],
    'Beatriz': ['Beatriz', 'Marcello'],
    'Bianca': ['Bianca', 'Matheus'],
    'Camila': ['Camila', 'Guilherme'],
    'Felipe': ['Felipe', 'Bárbara'],
    'Guilherme': ['Guilherme', 'Camila'],
    'Luana': ['Luana', 'Lucas'],
    'Lucas': ['Lucas', 'Luana'],
    'Marcello': ['Marcello', 'Beatriz'],
    'Matheus': ['Matheus', 'Bianca']
}

ss_as = SecretSanta(PARTICIPANTS_N_RESTICTIONS, 'amigo secreto')
ss_as.export_to_file('./results')

# ss_is = SecretSanta(PARTICIPANTS_N_RESTICTIONS, 'inimigo secreto')
# ss_is.export_to_file('./results')

# SE QUISER VALIDAR - Comentar na versao final
# print(ss_as.results)
# print(ss_is.results)