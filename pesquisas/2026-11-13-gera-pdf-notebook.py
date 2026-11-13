import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, KeepTogether, CondPageBreak)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

F = '/usr/share/fonts/truetype/dejavu/'
pdfmetrics.registerFont(TTFont('DV', F + 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DVB', F + 'DejaVuSans-Bold.ttf'))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily('DV', normal='DV', bold='DVB', italic='DV', boldItalic='DVB')

INK = colors.HexColor('#1f2937')
MUTED = colors.HexColor('#5b6472')
ACCENT = colors.HexColor('#0f5e9c')
GOOD = colors.HexColor('#e7f3ec')
GOODB = colors.HexColor('#2f7d4f')
BAND = colors.HexColor('#f3f5f8')
LINE = colors.HexColor('#d5dae1')
WARN = colors.HexColor('#fff6e0')

S = {}
S['title'] = ParagraphStyle('title', fontName='DVB', fontSize=20, leading=25, textColor=INK, spaceAfter=4)
S['sub'] = ParagraphStyle('sub', fontName='DV', fontSize=11, leading=15, textColor=MUTED, spaceAfter=10)
S['h1'] = ParagraphStyle('h1', fontName='DVB', fontSize=14, leading=18, textColor=ACCENT, spaceBefore=12, spaceAfter=6, keepWithNext=1)
S['h2'] = ParagraphStyle('h2', fontName='DVB', fontSize=11, leading=14.5, textColor=INK, spaceBefore=9, spaceAfter=4, keepWithNext=1)
S['p'] = ParagraphStyle('p', fontName='DV', fontSize=9.4, leading=13.6, textColor=INK, spaceAfter=5)
S['li'] = ParagraphStyle('li', parent=S['p'], leftIndent=12, bulletIndent=2, spaceAfter=3)
S['small'] = ParagraphStyle('small', fontName='DV', fontSize=8, leading=10.6, textColor=MUTED, spaceAfter=3)
S['cell'] = ParagraphStyle('cell', fontName='DV', fontSize=7.6, leading=9.8, textColor=INK)
S['cellb'] = ParagraphStyle('cellb', parent=S['cell'], fontName='DVB')
S['cellh'] = ParagraphStyle('cellh', parent=S['cell'], fontName='DVB', textColor=colors.white)
S['box'] = ParagraphStyle('box', parent=S['p'], fontSize=9.8, leading=14.2)

def P(t, s='p'): return Paragraph(t, S[s])
def L(url, text=None):
    return '<link href="%s" color="#0f5e9c"><u>%s</u></link>' % (url, text or url)
def bullets(items, s='li'):
    return [Paragraph(i, S[s], bulletText='•') for i in items]

def table(rows, widths, head=True, hl_rows=(), zebra=True, font='cell'):
    data = []
    for r_i, r in enumerate(rows):
        st = 'cellh' if (head and r_i == 0) else font
        data.append([c if not isinstance(c, str) else Paragraph(c, S[st]) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1 if head else 0)
    cmds = [('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4), ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LINEBELOW', (0, 0), (-1, -1), 0.4, LINE)]
    if head:
        cmds += [('BACKGROUND', (0, 0), (-1, 0), ACCENT)]
    if zebra:
        for i in range(1 if head else 0, len(rows)):
            if i % 2 == 0:
                cmds.append(('BACKGROUND', (0, i), (-1, i), BAND))
    for i in hl_rows:
        cmds += [('BACKGROUND', (0, i), (-1, i), GOOD), ('LINEBEFORE', (0, i), (0, i), 2.5, GOODB)]
    t.setStyle(TableStyle(cmds))
    return t

def boxed(flow, bg=GOOD, border=GOODB):
    t = Table([[flow]], colWidths=[174 * mm])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), bg), ('LINEBEFORE', (0, 0), (0, -1), 3, border),
                           ('LEFTPADDING', (0, 0), (-1, -1), 9), ('RIGHTPADDING', (0, 0), (-1, -1), 9),
                           ('TOPPADDING', (0, 0), (-1, -1), 7), ('BOTTOMPADDING', (0, 0), (-1, -1), 7)]))
    return t

def footer(c, d):
    c.saveState()
    c.setFont('DV', 7.5)
    c.setFillColor(MUTED)
    c.drawString(18 * mm, 10 * mm, 'Notebook para programação, Manim e vídeo — preços consultados em 12 e 13/11/2026')
    c.drawRightString(A4[0] - 18 * mm, 10 * mm, 'página %d' % d.page)
    c.restoreState()

# ---------- URLs ----------
U = dict(
    loq='https://www.lenovo.com/br/pt/p/laptops/loq-laptops/88lq3001926/83kh0006br',
    loq_psref='https://psref.lenovo.com/Detail/LOQ_15IRX9?M=83KH0006BR',
    loq_nbc='https://www.notebookcheck.net/Lenovo-LOQ-15-review-The-FHD-gaming-laptop-with-an-RTX-4060-from-around-US-1-000.860325.0.html',
    loq_kabum='https://www.kabum.com.br/produto/746524',
    loq_busc='https://www.buscape.com.br/search?q=83KH0006BR',
    vaio16='https://www.br.vaio.com/notebook-vaio-fe16-amd-ryzen-7-5825u-linux-16gb-ram-512gb-ssd-16-ips-wuxga-antirreflexo-cinza-grafite-3344216/p',
    vaio8='https://www.br.vaio.com/notebook-vaio-fe16-amd-ryzen-7-5825u-linux-8gb-ram-512gb-ssd-16-ips-wuxga-antirreflexo-cinza-grafite-3344217/p',
    ddr4_8='https://www.kabum.com.br/produto/564690',
    ddr4_16='https://www.kabum.com.br/produto/378307',
    ddr5_8='https://www.kabum.com.br/produto/1003325',
    ddr5_16a='https://www.kabum.com.br/produto/404834',
    ddr5_16b='https://www.kabum.com.br/produto/467705',
    ddr5_32='https://www.kabum.com.br/produto/427599',
    ssd1t='https://www.kabum.com.br/produto/621162',
    ip_i7='https://www.lenovo.com/br/pt/p/laptops/ideapad/ideapad-s-series/lenovo-ideapad-slim-3i-gen-10-15-inch-intel/83nss00100',
    ip_i5='https://www.lenovo.com/br/pt/p/laptops/ideapad/ideapad-s-series/lenovo-ideapad-slim-3i-gen-10-15-inch-intel/83nss00000',
    ip_psref='https://psref.lenovo.com/Detail/IdeaPad_Slim_3_15IRH10?M=83NS0002BR',
    ip_amd='https://www.lenovo.com/br/pt/p/laptops/ideapad/ideapad-s-series/lenovo-ideapad-slim-3-gen-10-15-inch-amd/83ty000jbo',
    ip_amd_psref='https://psref.lenovo.com/Detail/IdeaPad_Slim_3_15AHP10?M=83TY000JBO',
    nitro='https://www.kabum.com.br/produto/1048035',
    nitro_lm='https://laptopmedia.com/?p=1646420',
    yoga='https://www.amazon.com.br/dp/B0DG46DS62',
    slim5='https://www.lenovo.com/br/pt/p/laptops/ideapad/ideapad-500/lenovo-ideapad-slim-5-gen-10-14-inch-amd/83nj0001br',
    ess_w='https://www.lenovo.com/br/pt/p/laptops/loq-laptops/lenovo-loq-essential-15irx11/83ux000abo',
    ess_l='https://www.lenovo.com/br/pt/p/laptops/loq-laptops/lenovo-loq-essential-15irx11/83uxs00000',
    ess_psref='https://psref.lenovo.com/Detail/LOQ_Essential_15IRX11?M=83UX000ABO',
    loq4050='https://www.lenovo.com/br/pt/p/laptops/loq-laptops/88lq3001926/83kh000mbr',
    zoom4050='https://www.zoom.com.br/notebook/notebook-gamer-lenovo-83kh000mbr-15-6-16gb-ssd-512-gb-windows-11-geforce-rtx-4050',
    promobit='https://www.promobit.com.br/oferta/notebook-gamer-lenovo-loq-i5-16gb-ssd-rtx-3050-2973555/',
    pelando='https://www.pelando.com.br/d/notebook-lenovo-loq-i5-13450hx-rtx-3050-6gb-16gb-win11-83d1',
    manim='https://docs.manim.community/en/stable/guides/deep_dive.html',
    manim019='https://docs.manim.community/en/stable/changelog/0.19.0-changelog.html',
    manimpango='https://pypi.org/project/ManimPango/#files',
    puget_res='https://www.pugetsystems.com/pugetbench/creators/davinci-resolve/',
    puget_pr='https://www.pugetsystems.com/labs/articles/puget-bench-for-premiere-pro-and-davinci-resolve-2-0-analysis/',
    resolve_req='https://www.blackmagicdesign.com/us/support/content/readme/a6e2bbb59c294d728d131fa21d18676b',
    resolve_studio='https://www.blackmagicdesign.com/products/davinciresolve/studio',
    wsl='https://learn.microsoft.com/en-us/windows/wsl/wsl-config',
    nbc_cpu='https://www.notebookcheck.net/Mobile-Processors-Benchmark-List.2436.0.html',
    nbc_gpu='https://www.notebookcheck.net/Mobile-Graphics-Cards-Benchmark-List.844.0.html',
    dual='https://www.notebookcheck.net/Dynabook-Tecra-A65-M-shows-the-importance-of-dual-channel-RAM-for-integrated-graphics-performance.1208012.0.html',
    ollama='https://ollama.com/library/qwen2.5-coder/tags',
    avell='https://avell.com.br/ion-a52-intel-i7-13620h-rtx3050',
    tuf='https://www.kabum.com.br/produto/1082302',
    aspire='https://www.kabum.com.br/produto/1075027',
    dell15='https://www.dell.com/pt-br/shop/notebooks-dell/spd/dell15laptopdc15250',
)

story = []
W = 174 * mm

# ---------- Capa / resposta ----------
story += [P('Qual notebook comprar para programar, animar com Manim e editar vídeo', 'title'),
          P('Análise de custo-benefício com ofertas reais no Brasil · preços consultados em 12 e 13/11/2026, duas semanas antes da Black Friday (27/11)', 'sub')]

story.append(boxed([
    P('<b>Resposta curta:</b> continuo recomendando o <b>Lenovo LOQ 15IRX9, código 83KH0006BR, por R$ 5.014,99 no Pix</b> '
      '(ou R$ 5.900,04 em 12x de R$ 491,67 sem juros) na ' + L(U['loq'], 'loja oficial da Lenovo') + '. '
      'Na segunda rodada procurei em mais doze lojas e comparadores e não encontrei nada que entregue o mesmo conjunto por menos. '
      'É a máquina mais barata que junta, de fábrica, 16 GB em dois pentes com espaço para 32 GB, tela calibrada com 100% sRGB, '
      'processador forte, placa de vídeo dedicada e Windows 11 incluído.', 'box'),
    P('Se o orçamento apertar, existem degraus abaixo que funcionam, e cada um tem um preço em conforto. Se sobrar dinheiro, '
      'os degraus acima só valem para quem carrega o notebook todo dia ou edita vídeo com muitos efeitos. A escada completa está na próxima tabela.', 'box'),
]))
story.append(Spacer(1, 8))

story.append(P('A escada de opções, do mais barato ao mais caro', 'h1'))
story.append(P('Cada linha é uma oferta conferida na página da loja. A coluna "subir custa" mostra quanto se paga a mais em relação ao degrau anterior da escada principal.'))
ladder = [
    ['Degrau', 'Modelo e código', 'O que vem', 'Preço no Pix', 'Subir custa', 'Em uma frase'],
    ['0 · piso', 'Vaio FE16, Ryzen 7 5825U, 16 GB / 512 GB, Linux',
     'CPU de 2022, vídeo integrado fraco, 2 slots DDR4 (até 64 GB), tela IPS 16" 1920x1200 (gamut não informado)',
     L(U['vaio16'], 'R$ 4.099,00') + '<br/>Vaio', '—',
     'O mínimo que funciona. Renderizações do Manim ~20% mais demoradas e exportações bem mais lentas que no LOQ; sem Windows.'],
    ['1 · integrado bom', 'Lenovo IdeaPad Slim 3i 15IRH10 <b>83NSS00100</b>, i7-13620H, 16 GB, Linux',
     '8 GB soldados + 8 GB no slot (máx. 24 GB), tela 15,3" IPS 45% NTSC, 2 slots M.2, ~1,6 kg',
     L(U['ip_i7'], 'R$ 4.675,99') + '<br/>Lenovo', '+ R$ 577',
     'CPU no nível do LOQ, leve, mas tela de cores pálidas e sem Windows.'],
    ['2 · <b>escolha</b>', '<b>Lenovo LOQ 15IRX9 83KH0006BR</b>, i5-13450HX, 16 GB, RTX 3050 6 GB, Windows 11',
     '2x8 GB em 2 slots (até 32 GB), 2 slots M.2, tela 15,6" IPS 144 Hz 100% sRGB, 2,38 kg',
     '<b>' + L(U['loq'], 'R$ 5.014,99') + '</b><br/>Lenovo', '+ R$ 339',
     'O melhor conjunto por real gasto. Pesado e com bateria curta.'],
    ['3 · portátil', 'Lenovo IdeaPad Slim 5 14AKP10 <b>83NJ0001BR</b>, Ryzen AI 7 350, 16 GB, Windows 11',
     '2x8 GB em 2 slots (até 32 GB), tela 14" IPS 100% sRGB, sem GPU dedicada',
     L(U['slim5'], 'R$ 6.034,99') + '<br/>Lenovo', '+ R$ 1.020',
     'CPU mais rápida da lista e fácil de carregar; perde a RTX.'],
    ['3 · mais GPU', 'Lenovo LOQ Essential 15IRX11 <b>83UX000ABO</b>, i5-13450HX, 16 GB, RTX 5050 8 GB, Windows 11',
     '1x16 GB (2 slots), tela 15,6" IPS 144 Hz 100% sRGB',
     L(U['ess_w'], 'R$ 6.459,99') + '<br/>Lenovo', '+ R$ 1.445',
     'Dobro de GPU e 8 GB de VRAM. Só vale com edição pesada ou IA local.'],
]
story.append(table(ladder, [20 * mm, 38 * mm, 42 * mm, 21 * mm, 15 * mm, 38 * mm], hl_rows=(3,)))
story.append(Spacer(1, 4))
story.append(P('Alternativas no mesmo patamar do LOQ, analisadas na seção 5: '
               '<b>Acer Nitro V15 ANV15-41-R6J0</b> com RTX 4050 (' + L(U['nitro'], 'R$ 4.994,10 na KaBuM') + ', mas com só 8 GB e Linux; '
               'com o pente que falta, cerca de R$ 5.993), <b>Lenovo Yoga Slim 7i 83GM0003BR</b> com tela OLED (' + L(U['yoga'], 'R$ 5.039,16 na Amazon') + ', memória soldada) '
               'e <b>IdeaPad Slim 3 83TY000JBO</b> com Ryzen 7 8840HS (' + L(U['ip_amd'], 'R$ 4.759,99') + ', limitado a 16 GB em um único pente).', 'small'))

# ---------- 1. Seu uso ----------
story.append(PageBreak())
story.append(P('1. O que o seu uso exige do notebook', 'h1'))
story.append(P('O ponto de partida foi o seu dia de referência: navegador com muitas abas, editor de código, alguns terminais, mais de uma ferramenta '
               'de IA aberta, e no meio disso pré-visualizar uma animação do Manim ou exportar um vídeo em 1080p. Cada uma dessas tarefas pesa '
               'sobre uma peça diferente do computador. Entender qual peça cada tarefa usa é o que permite economizar no lugar certo.'))
uso = [
    ['Tarefa', 'Peça que decide', 'O que isso significa na compra'],
    ['Claude Code e IA na nuvem (ChatGPT, Gemini etc.)', 'Internet e memória RAM',
     'O modelo roda nos servidores. O notebook só precisa segurar o terminal e as abas do navegador, que consomem RAM. A placa de vídeo não participa.'],
    ['Navegador com muitas abas, VS Code, terminais, Git', 'RAM e processador',
     '16 GB é o ponto confortável. Com 8 GB o sistema começa a usar o SSD como memória e tudo fica lento.'],
    ['Python e código local', 'Processador (vários núcleos) e SSD',
     'Instalar pacotes, rodar testes e scripts usa vários núcleos. SSD NVMe de 512 GB basta para começar.'],
    ['Manim (pré-visualização e renderização)', 'Processador, desempenho por núcleo',
     'O renderizador padrão (Cairo) desenha quadro a quadro em Python, na CPU (' + L(U['manim'], 'documentação do Manim') + '). '
     'A codificação usa o ffmpeg embutido via PyAV desde a versão 0.19 (' + L(U['manim019'], 'changelog') + '). A placa de vídeo não acelera esse caminho.'],
    ['Edição de vídeo 1080p: linha do tempo', 'GPU e RAM',
     'Efeitos, correção de cor e redução de ruído usam a GPU. O DaVinci Resolve pede 16 GB de RAM e GPU integrada ou dedicada com 4 GB de VRAM (' + L(U['resolve_req'], 'requisitos oficiais') + ').'],
    ['Edição de vídeo 1080p: exportação', 'Depende do programa',
     'No Resolve gratuito no Windows, a exportação H.264/H.265 é feita pela CPU, com ou sem placa de vídeo (' + L(U['puget_res'], 'Puget Systems') + '). '
     'A versão Studio e o Premiere usam o codificador de hardware (Quick Sync da Intel ou NVENC da NVIDIA) (' + L(U['puget_pr'], 'Puget') + ').'],
    ['Modelos de IA locais (futuro)', 'VRAM da placa de vídeo ou muita RAM',
     'Um modelo de 7B quantizado ocupa ~4,7 GB; um de 14B, ~9 GB (' + L(U['ollama'], 'Ollama') + '). Placas de 6 a 8 GB rodam só os pequenos.'],
]
story.append(table(uso, [38 * mm, 32 * mm, 104 * mm]))
story.append(Spacer(1, 6))
story.append(P('A consequência prática: <b>o processador é a peça que você mais vai sentir</b> (Manim, Python, exportação no Resolve gratuito). '
               'Em seguida vêm <b>16 GB de RAM em dois pentes</b> e uma <b>tela com cores corretas</b> para editar vídeo. '
               'A placa de vídeo dedicada ajuda na linha do tempo e em efeitos, mas não é o que acelera seu trabalho do dia a dia.'))

# ---------- 2. Critérios ----------
story.append(P('2. Os critérios de corte e por que eles importam', 'h1'))
story.append(P('Processador', 'h2'))
story.append(P('A tabela compara os processadores dos finalistas pelas medianas do ' + L(U['nbc_cpu'], 'Notebookcheck') + '. '
               'O "single" mede um núcleo (o que o Manim sente); o "multi" mede todos (exportação, testes, compilação). '
               'Defini como piso sensato algo perto de 2.200 pontos single e 8.000 multi no Geekbench 6.'))
cpu = [
    ['Processador', 'Onde aparece', 'Cinebench R23 single', 'Cinebench R23 multi', 'Geekbench 6 single', 'Geekbench 6 multi'],
    ['Ryzen 7 5825U (2022)', 'Vaio FE16 (degrau 0)', '1.452', '10.152', '1.988', '8.644'],
    ['Ryzen 7 7735HS', 'Acer Nitro V15', '1.546', '13.106', '2.098', '9.970'],
    ['Core i7-13620H', 'IdeaPad Slim 3i (degrau 1)', '1.833', '15.176', '2.568', '11.723'],
    ['Ryzen 7 8840HS', 'IdeaPad Slim 3 AMD', '1.737', '13.082', '2.552', '11.279'],
    ['<b>Core i5-13450HX</b>', '<b>LOQ 15IRX9 (escolha)</b> e LOQ Essential', '<b>1.746</b>', '<b>16.797</b>', '<b>2.417</b>', '<b>12.684</b>'],
    ['Core Ultra 5 125H', 'Yoga Slim 7i', '1.647', '12.804', '2.279', '11.268'],
    ['Ryzen AI 7 350', 'IdeaPad Slim 5 (degrau 3)', '1.958', '16.014', '2.853', '12.835'],
]
story.append(table(cpu, [33 * mm, 45 * mm, 24 * mm, 24 * mm, 24 * mm, 24 * mm], hl_rows=(5,)))
story.append(P('Leitura: o i5-13450HX do LOQ está entre os dois melhores em vários núcleos e no grupo bom em núcleo único. '
               'O Ryzen 7 5825U do degrau 0 fica cerca de 18% atrás em núcleo único e 30% a 40% atrás em vários núcleos. '
               'É usável, mas cada renderização demora mais. Processadores como Ryzen 5 7520U, Core 3 e Core 5 320, comuns nos anúncios mais baratos, '
               'ficam abaixo do piso e foram descartados. Snapdragon também foi descartado: o Manim depende de pacotes (ManimPango) '
               'sem versão para Windows em ARM (' + L(U['manimpango'], 'PyPI') + ').', 'small'))

story.append(P('Placa de vídeo', 'h2'))
gpu = [
    ['GPU', 'Onde aparece', '3DMark Time Spy (gráficos)', 'Relativo à RTX 3050'],
    ['AMD Radeon Vega 8 (integrada)', 'Vaio FE16', '1.163', '25%'],
    ['Intel UHD (integrada, referência 64 EU)', 'IdeaPad Slim 3i', '1.110', '24%'],
    ['Intel Arc 7 núcleos (integrada)', 'Yoga Slim 7i', '2.941', '64%'],
    ['AMD Radeon 860M (integrada)', 'IdeaPad Slim 5', '2.565', '56%'],
    ['AMD Radeon 780M (integrada)', 'IdeaPad Slim 3 AMD', '2.808', '61%'],
    ['<b>NVIDIA RTX 3050 6 GB</b>', '<b>LOQ 15IRX9 (escolha)</b>', '<b>4.571</b>', '<b>100%</b>'],
    ['NVIDIA RTX 4050 6 GB', 'Acer Nitro V15', '8.125', '178%'],
    ['NVIDIA RTX 5050 8 GB', 'LOQ Essential', '8.941', '196%'],
]
story.append(table(gpu, [58 * mm, 46 * mm, 38 * mm, 32 * mm], hl_rows=(6,)))
story.append(P('Fonte: medianas do ' + L(U['nbc_gpu'], 'Notebookcheck') + '. Time Spy mede força gráfica bruta, que não se traduz direto em velocidade de edição. '
               'O valor da UHD é o da geração anterior (Alder Lake), usado como aproximação. As integradas da AMD perdem de 40% a 50% '
               'quando a memória roda em um único pente (' + L(U['dual'], 'Notebookcheck') + '), o que afeta o IdeaPad Slim 3 AMD e o LOQ Essential.', 'small'))

story.append(P('Memória, armazenamento, tela e sistema', 'h2'))
story += bullets([
    '<b>RAM:</b> 16 GB de fábrica, de preferência em dois pentes (dual-channel), e com caminho para chegar a 32 GB. O WSL2 do Windows reserva por padrão até metade da RAM (' + L(U['wsl'], 'Microsoft') + '), e a GPU integrada também tira a memória de vídeo da RAM.',
    '<b>SSD:</b> 512 GB no mínimo. Cache do editor, projetos do Manim e ambientes Python crescem rápido. Um segundo slot M.2 permite somar mais um SSD depois.',
    '<b>Tela:</b> IPS com ~100% sRGB para editar vídeo com cores confiáveis. Telas de 45% NTSC (cerca de 60% sRGB) mostram cores pálidas. Telas TN foram descartadas.',
    '<b>Sistema:</b> modelos com Linux custam menos, mas não rodam CapCut nem Premiere. O Manim, o Python e o Kdenlive funcionam bem no Linux. '
    'O Resolve gratuito para Linux tem restrições conhecidas com H.264/H.265; confira antes de depender dele (não verifiquei esse ponto nesta pesquisa). '
    'A licença do Windows não vem nesses modelos.',
])

# ---------- 3. Memória cara ----------
story.append(P('3. A memória está cara em 2026, e isso muda a estratégia', 'h1'))
story.append(P('O caminho clássico para economizar era comprar a versão de 8 GB e ampliar depois. Com os preços de hoje, isso só compensa em notebooks com memória DDR4. '
               'Para DDR5, que é o padrão dos modelos atuais, um pente de 8 GB custa quase R$ 1.000.'))
ram = [
    ['Peça (preço à vista na KaBuM)', 'Preço', 'Serve em'],
    ['DDR4 3200 8 GB Kingston KVR32S22S8/8', L(U['ddr4_8'], 'R$ 453,14'), 'Vaio FE16'],
    ['DDR4 3200 16 GB Kingston Fury (vendedor parceiro)', L(U['ddr4_16'], 'R$ 788,66'), 'Vaio FE16'],
    ['DDR5 5600 8 GB Samsung', L(U['ddr5_8'], 'R$ 999,00'), 'Nitro V15, IdeaPad, LOQ'],
    ['DDR5 4800 16 GB Kingston Fury', L(U['ddr5_16a'], 'R$ 1.738,99'), 'LOQ, IdeaPad, Nitro'],
    ['DDR5 5600 16 GB Crucial (vendedor parceiro)', L(U['ddr5_16b'], 'R$ 1.749,99'), 'LOQ, IdeaPad, Nitro'],
    ['DDR5 5600 32 GB Kingston Fury (um pente)', L(U['ddr5_32'], 'R$ 4.751,38'), 'Referência (o LOQ aceita oficialmente até 32 GB)'],
]
story.append(table(ram, [86 * mm, 28 * mm, 60 * mm]))
story.append(Spacer(1, 4))
story.append(P('Dois exemplos de como isso pesa:'))
story += bullets([
    'IdeaPad Slim 3i com i5-13420H e 8 GB (' + L(U['ip_i5'], 'R$ 3.315,99') + ') + pente DDR5 de 8 GB (R$ 999) = <b>R$ 4.315</b>. A versão com i7-13620H e 16 GB de fábrica sai por R$ 4.675,99, só R$ 361 a mais, com processador melhor e sem abrir a máquina.',
    'Acer Nitro V15 com RTX 4050 e 8 GB (R$ 4.994,10) + pente DDR5 de 8 GB (R$ 999) = <b>R$ 5.993</b>, quase R$ 1.000 acima do LOQ.',
    'No Vaio FE16, que usa DDR4, a conta fecha: a versão de 8 GB (' + L(U['vaio8'], 'R$ 3.399') + ') + um pente de 8 GB DDR4 (R$ 453) = <b>R$ 3.852</b> para 16 GB, contra R$ 4.099 da versão de 16 GB de fábrica.',
])
story.append(P('Conclusão: <b>compre já com 16 GB</b>. Ampliar para 32 GB faz sentido mais tarde, se o preço da memória cair.'))

# ---------- 4. Escolha detalhada ----------
story.append(CondPageBreak(70 * mm))
story.append(P('4. Por que o LOQ 83KH0006BR é a escolha', 'h1'))
loqspec = [
    ['Item', 'Configuração confirmada', 'Fonte'],
    ['Processador', 'Intel Core i5-13450HX, 10 núcleos (6P + 4E), 16 threads, até 4,6 GHz', L(U['loq_psref'], 'PSREF Lenovo')],
    ['Memória', '2x 8 GB DDR5-4800, dois slots SO-DIMM, dual-channel, até 32 GB', 'PSREF'],
    ['Armazenamento', 'SSD 512 GB NVMe PCIe 4.0, dois slots M.2 (um livre)', 'PSREF'],
    ['Placa de vídeo', 'NVIDIA GeForce RTX 3050 6 GB GDDR6, 95 W', 'PSREF'],
    ['Tela', '15,6" Full HD IPS, 300 nits, 100% sRGB, 144 Hz, antirreflexo', 'PSREF'],
    ['Sistema e garantia', 'Windows 11 Home, 1 ano (balcão ou coleta)', 'PSREF e loja Lenovo'],
    ['Oferta', 'R$ 5.014,99 no Pix (15% de desconto da campanha Lenovo Friday) ou R$ 5.900,04 em 12x de R$ 491,67; em estoque; entrega estimada 19 a 23/11', L(U['loq'], 'loja Lenovo')],
]
story.append(table(loqspec, [30 * mm, 112 * mm, 32 * mm]))
story.append(Spacer(1, 6))
story.append(P('O que o teste independente diz', 'h2'))
story.append(P('O ' + L(U['loq_nbc'], 'Notebookcheck testou o LOQ 15IRX9') + ' com o mesmo processador e a mesma tela, mas com RTX 4060 (outra variante). '
               'Os pontos que não dependem da placa de vídeo valem para o seu modelo:'))
story += bullets([
    '<b>Tela:</b> 99,1% sRGB medido, brilho médio de 287 nits, contraste de 1.457:1, sem cintilação (PWM) e erro de cor de 2,25 já de fábrica, abaixo do limite de 3 que se usa para trabalho com cor. É a melhor tela entre as opções abaixo de R$ 6.000, exceto a OLED do Yoga.',
    '<b>Bateria:</b> 5h20 navegando por Wi-Fi. É um notebook para usar perto da tomada.',
    '<b>Ruído:</b> 48 dB no modo equilibrado e 54 dB no desempenho, sob carga de jogo. O teste critica as ventoinhas, que ficam ligando e desligando mesmo em repouso. O modo silencioso reduz o barulho com perda de desempenho.',
    '<b>Peso:</b> 2,38 kg, contra cerca de 1,6 kg do IdeaPad e 1,39 kg do Yoga.',
])
story.append(P('Por que ele vence cada alternativa', 'h2'))
vs = [
    ['Comparado com', 'Diferença de preço', 'O que o LOQ dá a mais', 'O que o LOQ dá a menos'],
    ['Vaio FE16 (degrau 0)', '+ R$ 916', 'CPU ~22% mais rápida em núcleo único e ~47% em multinúcleo; RTX 3050; tela 100% sRGB; Windows', 'Peso (2,38 contra 1,85 kg); o Vaio aceita até 64 GB de DDR4 barata'],
    ['IdeaPad Slim 3i 83NSS00100', '+ R$ 339', 'Tela 100% sRGB contra 45% NTSC; RTX 3050; Windows; dois pentes reais e 32 GB de teto', 'Portabilidade e bateria'],
    ['IdeaPad Slim 3 AMD 83TY000JBO', '+ R$ 255', 'Dual-channel e até 32 GB (o AMD tem um único slot e teto de 16 GB); tela muito melhor; RTX 3050', 'Portabilidade'],
    ['Acer Nitro V15 R6J0 + 8 GB', '− R$ 978', 'CPU ~15% mais rápida em núcleo único (Manim); Windows; nada a montar', 'GPU ~44% mais fraca que a RTX 4050'],
    ['Yoga Slim 7i OLED', '− R$ 24', 'RTX 3050; RAM ampliável (a do Yoga é soldada); multinúcleo 13% a 31% maior', 'Tela OLED; 1 kg a menos; bateria'],
]
story.append(table(vs, [38 * mm, 24 * mm, 64 * mm, 48 * mm]))
story.append(P('As porcentagens de CPU vêm do Geekbench 6 e as de GPU do Time Spy (tabelas da seção 2).', 'small'))

# ---------- 5. Degraus detalhados ----------
story.append(CondPageBreak(70 * mm))
story.append(P('5. Cada degrau em detalhe', 'h1'))

def card(title, price_line, specs, good, bad, verdict):
    items = [P(title, 'h2'), P(price_line)]
    items.append(table([['Configuração', specs]], [30 * mm, 144 * mm], head=False, zebra=False))
    items.append(Spacer(1, 3))
    items += bullets(['<b>A favor:</b> ' + good, '<b>Contra:</b> ' + bad, '<b>Veredito:</b> ' + verdict])
    return [KeepTogether(items)]

story += card('Degrau 0 · Vaio FE16 com Ryzen 7 5825U, a opção mais barata que ainda faz sentido',
              '<b>R$ 4.099,00 no Pix</b> na ' + L(U['vaio16'], 'loja Vaio') + ' (16 GB / 512 GB, Linux) ou R$ 4.822,35 em 10x. '
              'Montando você mesmo: ' + L(U['vaio8'], 'versão de 8 GB por R$ 3.399') + ' + ' + L(U['ddr4_8'], 'pente Kingston DDR4 de 8 GB por R$ 453,14') + ' = <b>R$ 3.852</b>. Cupom BLACKVAIO visível na página.',
              'Ryzen 7 5825U (8 núcleos, Zen 3), vídeo integrado Radeon Vega 8, 2 slots DDR4 não soldados (até 64 GB), SSD NVMe, tela IPS de 16" 1920x1200 antirreflexo, 1,85 kg, Linux. '
              'A loja não informa brilho nem gamut da tela, nem a garantia na página.',
              'é a única opção barata com memória DDR4 em dois slots, então chegar a 32 GB custa ~R$ 1.580 (dois pentes de 16 GB) em vez de ~R$ 3.500 em DDR5. Tela grande, em formato 16:10, boa para código.',
              'processador de 2022, ~18% mais lento em núcleo único que o do LOQ: o preview do Manim e a exportação demoram mais. Vídeo integrado fraco para a linha do tempo com efeitos. Sem Windows (CapCut e Premiere não rodam). Tela provavelmente sem cores amplas.',
              'compraria só se o limite for R$ 4.100. Ele dá conta de estudar, programar e animar; você vai esperar mais nas renderizações e editar com menos folga.')

story += card('Degrau 1 · IdeaPad Slim 3i 83NSS00100 com Core i7-13620H',
              '<b>R$ 4.675,99 no Pix</b> na ' + L(U['ip_i7'], 'loja Lenovo') + ' ou R$ 5.501,16 em 12x de R$ 458,43. Aviso de "poucas unidades". A versão com Windows (83NS0000BR) aparecia por R$ 4.930,99 em 12/11.',
              'i7-13620H (10 núcleos), Intel UHD, 16 GB DDR5 (8 GB soldados + 8 GB no slot, até 24 GB trocando o pente), SSD 512 GB com dois slots M.2 2242, tela 15,3" 1920x1200 IPS 300 nits 45% NTSC, ~1,6 kg, Linux. '
              'Dados do código irmão no ' + L(U['ip_psref'], 'PSREF') + ', porque o código com "S" não consta na ficha.',
              'processador no mesmo nível do LOQ para o Manim, mais leve e fácil de carregar.',
              'tela de cores pálidas, vídeo integrado básico, teto de 24 GB, sem Windows. A versão com Windows custa só R$ 84 menos que o LOQ.',
              'faz sentido se você não precisa de Windows e valoriza peso. Com Windows, o LOQ é melhor negócio.')

story += card('Alternativa · IdeaPad Slim 3 83TY000JBO com Ryzen 7 8840HS',
              '<b>R$ 4.759,99 no Pix</b> na ' + L(U['ip_amd'], 'loja Lenovo') + ' (R$ 4.927,12 na KaBuM, vendido pela Lenovo).',
              'Ryzen 7 8840HS, Radeon 780M, <b>1x 16 GB em slot único, teto oficial de 16 GB</b>, SSD 512 GB com dois slots M.2 2242, tela 15,3" IPS 45% NTSC, Windows 11 (' + L(U['ip_amd_psref'], 'PSREF') + ').',
              'bom processador e a melhor GPU integrada entre os baratos.',
              'memória em um único pente reduz o desempenho da 780M e não há como passar de 16 GB. Tela fraca.',
              'descartado como recomendação: custa R$ 255 menos que o LOQ e entrega bem menos.')

story += card('Degrau 2 · Lenovo LOQ 15IRX9 83KH0006BR (a escolha)',
              '<b>R$ 5.014,99 no Pix</b> na ' + L(U['loq'], 'loja Lenovo') + '. O mesmo código custa ' + L(U['loq_busc'], 'R$ 5.191,12 na Americanas, R$ 5.309,10 na KaBuM e R$ 5.899 na Fast Shop') + '.',
              'Ver seção 4.',
              'é o único abaixo de R$ 6.000 que junta CPU forte, dual-channel com teto de 32 GB, tela 100% sRGB, GPU dedicada e Windows.',
              'pesado, bateria curta, ventoinhas audíveis.',
              'compra recomendada.')

story += card('Alternativa · Acer Nitro V15 ANV15-41-R6J0 com RTX 4050',
              '<b>R$ 4.994,10 no Pix</b> na ' + L(U['nitro'], 'KaBuM (vendido pela Acer)') + ', R$ 5.140,03 na Fast Shop e R$ 5.198,99 na Amazon. Com o pente de 8 GB que falta: ~R$ 5.993.',
              'Ryzen 7 7735HS, RTX 4050 6 GB, <b>8 GB DDR5 em um pente</b> (2 slots, até 32 GB pelo anúncio), SSD 512 GB, tela 15,6" IPS 165 Hz, Linux, PN NH.U20AL.004. '
              'O painel de 165 Hz dessa família mediu 97% sRGB no ' + L(U['nitro_lm'], 'LaptopMedia') + ' (o painel pode variar por lote).',
              'RTX 4050 com quase o dobro da força da RTX 3050, pelo mesmo preço de etiqueta.',
              'com 8 GB ele não serve para o seu cenário; somado o pente, fica ~R$ 1.000 acima do LOQ. CPU mais fraca em núcleo único (pior para o Manim). Sem Windows.',
              'só vale se a GPU for a prioridade. Para você, não é.')

story += card('Alternativa · Lenovo Yoga Slim 7i 14IMH9 83GM0003BR com tela OLED',
              '<b>R$ 5.039,16 no Pix</b> na ' + L(U['yoga'], 'Amazon (vendido pela Fast Shop)') + ' ou 12x de R$ 499,99.',
              'Core Ultra 5 125H, Intel Arc integrada, 16 GB LPDDR5X soldados (sem slot), SSD 512 GB, tela 14" 1920x1200 OLED 400 nits 100% DCI-P3, Windows 11, 1,39 kg. A garantia não aparece no anúncio.',
              'a tela mais bonita da lista e o mais leve.',
              'memória fixa em 16 GB para sempre, sem GPU dedicada, CPU multinúcleo 11% a 24% abaixo do LOQ.',
              'só para quem carrega o notebook todos os dias.')

story += card('Degrau 3 · IdeaPad Slim 5 83NJ0001BR (portabilidade) ou LOQ Essential 83UX000ABO (mais GPU)',
              'Slim 5: <b>R$ 6.034,99</b> na ' + L(U['slim5'], 'loja Lenovo') + '. LOQ Essential: <b>R$ 6.459,99</b> com Windows (' + L(U['ess_w'], 'loja Lenovo') + ') ou R$ 6.204,99 com Linux (' + L(U['ess_l'], '83UXS00000') + '). Ambos com "poucas unidades".',
              'Slim 5: Ryzen AI 7 350, Radeon 860M, 2x 8 GB DDR5-5600 em 2 slots (até 32 GB), tela 14" IPS 100% sRGB, Windows 11. '
              'LOQ Essential: i5-13450HX, RTX 5050 8 GB (65 W), 1x 16 GB em 2 slots (o ' + L(U['ess_psref'], 'PSREF') + ' lista teto de 16 GB), tela 15,6" IPS 100% sRGB 144 Hz.',
              'o Slim 5 tem a CPU mais rápida em núcleo único da lista (+18% sobre o LOQ) num corpo de 14". O LOQ Essential dobra a GPU e traz 8 GB de VRAM.',
              'o Slim 5 perde a GPU dedicada. O LOQ Essential vem com um único pente e custa R$ 1.445 a mais.',
              'só se você for carregar o notebook (Slim 5) ou fizer edição pesada e IA local (LOQ Essential). O LOQ com RTX 4050 (83KH000MBR, R$ 6.374,99) esgotou na loja Lenovo durante a pesquisa.')

# ---------- 6. GPU ----------
story.append(CondPageBreak(70 * mm))
story.append(P('6. Quanto vale pagar por uma placa de vídeo dedicada', 'h1'))
story.append(P('A pergunta certa não é "preciso de placa de vídeo?", e sim "em quais das minhas tarefas ela muda alguma coisa?".'))
gpu_tasks = [
    ['Tarefa', 'Vídeo integrado bom', 'RTX 3050 (LOQ)', 'RTX 4050 / 5050'],
    ['Claude Code, IA na nuvem, navegador', 'Igual', 'Igual', 'Igual'],
    ['Manim (Cairo)', 'Igual: depende da CPU', 'Igual', 'Igual'],
    ['Linha do tempo 1080p sem efeitos', 'Fluida', 'Fluida', 'Fluida'],
    ['Linha do tempo com cor, efeitos, redução de ruído (Resolve)', 'Trava em efeitos pesados', 'Bem melhor', 'Mais folga ainda'],
    ['Exportação no Resolve gratuito (Windows)', 'CPU faz o trabalho', 'CPU faz o trabalho', 'CPU faz o trabalho'],
    ['Exportação no Premiere ou no Resolve Studio', 'Quick Sync (Intel) acelera', 'NVENC acelera', 'NVENC acelera'],
    ['IA local (futuro)', 'Lento, usa a RAM', 'Modelos de até ~7B', 'Até ~7B (6 GB) ou 8B (8 GB)'],
]
story.append(table(gpu_tasks, [58 * mm, 40 * mm, 36 * mm, 40 * mm]))
story.append(Spacer(1, 5))
story.append(P('Leitura: para Claude Code, IA na nuvem e Manim, a placa não faz diferença nenhuma. Ela aparece na edição de vídeo, na linha do tempo com efeitos, '
               'e nos programas que usam NVENC para exportar. Para IA local, 6 GB só comportam modelos pequenos; 14B não cabem inteiros nem em 8 GB.'))
story.append(P('No LOQ, a RTX 3050 custa pouco porque o pacote todo é barato: ele sai por R$ 255 a R$ 339 a mais que os IdeaPad de vídeo integrado, '
               'e essa diferença também paga a tela 100% sRGB, o dual-channel e o Windows. Por isso a placa entra quase de graça. '
               'Pagar mais R$ 1.000 a R$ 1.450 por uma RTX 4050 ou 5050 só se justifica se edição com efeitos virar o centro do seu trabalho ou se a IA local deixar de ser hipótese.'))
story.append(P('Ressalva: não achei teste que compare diretamente vídeo integrado e RTX 3050 dentro do Resolve. O ganho em efeitos é uma inferência a partir da força bruta das GPUs e do que o Resolve acelera na GPU.', 'small'))

# ---------- 7. RAM ----------
story.append(P('7. 16 ou 32 GB, e o plano de ampliação', 'h1'))
story += bullets([
    '<b>16 GB atendem seu cenário de referência.</b> É o mínimo pedido pelo Resolve, e no LOQ a placa de vídeo tem memória própria, então os 16 GB ficam inteiros para o sistema.',
    '<b>32 GB passam a fazer diferença</b> se você somar WSL2 ou Docker, Resolve com Fusion e muitas abas ao mesmo tempo, ou se quiser rodar modelos de IA maiores na CPU.',
    '<b>No LOQ, chegar a 32 GB exige trocar os dois pentes</b> por 2x 16 GB DDR5, hoje cerca de R$ 3.480. Não vale agora. Se a memória baratear, a troca passa a compensar.',
    'Antes da RAM, a ampliação mais útil tende a ser um <b>segundo SSD</b> no slot M.2 livre (SSD NVMe de 1 TB a partir de ' + L(U['ssd1t'], 'R$ 1.149,99') + '). Confira o tamanho do slot livre antes de comprar.',
])

# ---------- 8. Comprar agora ou esperar ----------
story.append(P('8. Comprar agora ou esperar a Black Friday', 'h1'))
story.append(P('Não há histórico público do código 83KH0006BR no Zoom nem no Buscapé, que só listam as ofertas atuais. Encontrei três referências:'))
story += bullets([
    '<b>O irmão com RTX 4050 (83KH000MBR)</b> custou em mediana R$ 7.742 em outubro no ' + L(U['zoom4050'], 'histórico do Zoom') + ', caiu para R$ 6.350 em 4/11 e estava em R$ 6.449 em 12/11. Ou seja, a campanha atual da Lenovo já derrubou o preço da linha em cerca de 18%. Esse modelo esgotou na loja Lenovo durante a pesquisa.',
    '<b>Ofertas passadas do LOQ com RTX 3050 e 16 GB:</b> R$ 4.531 no Magazine Luiza (' + L(U['promobit'], 'Promobit') + ', publicada em 10 de agosto, ano e código não informados) e R$ 4.751 no Pix na Lenovo (' + L(U['pelando'], 'Pelando') + ', data não confirmada).',
    '<b>Hoje, a loja Lenovo tem o menor preço</b> entre as que vendem o código: ' + L(U['loq_busc'], 'Americanas R$ 5.191,12, KaBuM R$ 5.309,10, Fast Shop R$ 5.899') + '.',
])
story.append(P('Minha leitura: R$ 5.014,99 é um preço bom, mas não o menor já visto. Na Black Friday pode aparecer algo entre R$ 4.500 e R$ 4.750, '
               'como nas ofertas passadas. O risco de esperar é a configuração esgotar, como aconteceu com a de RTX 4050. '
               'Se você precisa do notebook agora, comprar por R$ 5.014,99 é razoável. Se pode esperar até 27/11, crie alertas no Pelando e no Promobit '
               'para o código 83KH0006BR e compre de imediato se o preço chegar perto de R$ 4.750. A confiança nesta previsão é baixa, '
               'porque as ofertas antigas não têm data e código confirmados.'))

# ---------- 9. Varredura ----------
story.append(P('9. O que mais foi avaliado e por que ficou de fora', 'h1'))
scan = [
    ['Loja ou modelo', 'O que apareceu', 'Por que não entrou'],
    ['Acer Aspire Go 15 (AG15-71P)', 'i5-13420H ou i7-13620H com 16 GB, R$ 3.900 a R$ 4.850', 'Tela TN de 220 nits e 45% NTSC na ' + L(U['aspire'], 'ficha do AG15-71P-53D9') + '. Não confirmei o painel de cada variante.'],
    ['Loja Acer', 'Nitro V16 com RTX 5050 a partir de R$ 8.999', 'Muito acima.'],
    ['ASUS TUF Gaming F16 FX607VJB', 'Core 5 210H, RTX 3050, 8 GB, KeepOS, ' + L(U['tuf'], 'R$ 5.099,15'), 'Mais caro que o LOQ com metade da RAM, tela 45% NTSC e sem Windows.'],
    ['Loja ASUS', 'TUF F16 com RTX 3050 e 16 GB por R$ 5.669; TUF A15 Ryzen 7 7445HS com RTX 3050 por R$ 6.299', 'Mais caros que o LOQ.'],
    ['Avell ION A52 / STORM 350', 'i7-13620H com RTX 3050 4 GB ' + L(U['avell'], 'a partir de R$ 4.999 no Pix'), 'O preço inicial vem com 8 GB DDR4, SSD de 256 GB, sem sistema e tela de 250 nits e 65% sRGB. Com 16 GB e 512 GB, R$ 6.399.'],
    ['Dell', L(U['dell15'], 'Dell 15') + ' a partir de R$ 4.898,67 com 8 GB e vídeo UHD', 'Mais caro e mais fraco.'],
    ['Samsung', 'Galaxy Book4 com Core 5 por R$ 5.759,10', 'Mais caro e mais fraco.'],
    ['Vaio', 'FE16 com Ryzen 7 5825U', 'Entrou como degrau 0.'],
    ['Fast Shop', 'IdeaPad Slim 3 83NS0008BR com i7-13620H e 24 GB por R$ 5.269', 'Vendedor e condição não verificados. Mesma tela de 45% NTSC, sem GPU.'],
    ['HP', 'Linha 200/250 com 8 GB', 'Nada competitivo na parte acessível; parte do site bloqueou o acesso.'],
    ['Magazine Luiza, Casas Bahia, Pichau, Terabyte, Pelando', '—', 'Bloquearam o acesso automatizado (403). Mercado Livre pediu verificação de conta.'],
]
story.append(table(scan, [40 * mm, 64 * mm, 70 * mm]))

# ---------- 10. Checklist ----------
story.append(CondPageBreak(60 * mm))
story.append(P('10. Antes de pagar', 'h1'))
story += bullets([
    'Confira no carrinho o código <b>83KH0006BR</b>. Os códigos 83KHS00000 e 83KHS00200 são versões com Linux; a primeira vem com só 8 GB.',
    'Confirme que o valor de R$ 5.014,99 é o do Pix: o desconto de 15% da campanha só vale nessa forma de pagamento.',
    'Veja o frete para o seu CEP e a data de entrega (19 a 23/11 na consulta). Não testei frete nem cupons.',
    'O cadastro gratuito no My Lenovo Rewards oferece R$ 100 em recompensas para compras futuras; não é desconto nesta compra.',
    'Na entrega, confira a tela (sem pixels mortos), o número de série e a garantia de 1 ano no site da Lenovo.',
    'Se escolher um modelo com Linux, lembre que CapCut e Premiere não rodam nele e que a licença do Windows é custo extra.',
])

# ---------- 11. Limitações ----------
story.append(P('11. O que ficou em aberto', 'h1'))
story += bullets([
    'O teste independente do LOQ é da variante com RTX 4060; ruído e temperatura com a RTX 3050 podem ser um pouco menores.',
    'Não há teste direto de vídeo integrado contra RTX 3050 no DaVinci Resolve.',
    'Não medi o consumo real de RAM do seu cenário completo; a recomendação de 16 GB vem dos requisitos oficiais.',
    'Tela e garantia do Vaio FE16 não estão na página da loja.',
    'Os preços são de campanha e mudam rápido. O IdeaPad i7, o Slim 5 e o LOQ Essential estavam com aviso de "poucas unidades".',
])

# ---------- Fontes ----------
story.append(P('Fontes principais', 'h1'))
src = [
    ('Lojas', [L(U['loq'], 'Lenovo LOQ 83KH0006BR'), L(U['ip_i7'], 'IdeaPad 83NSS00100'), L(U['ip_amd'], 'IdeaPad 83TY000JBO'), L(U['slim5'], 'IdeaPad Slim 5 83NJ0001BR'),
               L(U['ess_w'], 'LOQ Essential 83UX000ABO'), L(U['vaio16'], 'Vaio FE16 16 GB'), L(U['nitro'], 'Nitro V15 R6J0 (KaBuM)'), L(U['yoga'], 'Yoga Slim 7i (Amazon)'), L(U['loq_busc'], 'Buscapé 83KH0006BR')]),
    ('Fichas oficiais', [L(U['loq_psref'], 'PSREF LOQ 15IRX9'), L(U['ip_psref'], 'PSREF IdeaPad 15IRH10'), L(U['ip_amd_psref'], 'PSREF IdeaPad 15AHP10'), L(U['ess_psref'], 'PSREF LOQ Essential')]),
    ('Testes e benchmarks', [L(U['loq_nbc'], 'Notebookcheck: teste do LOQ 15'), L(U['nbc_cpu'], 'Notebookcheck: processadores'), L(U['nbc_gpu'], 'Notebookcheck: GPUs'), L(U['dual'], 'Notebookcheck: dual-channel'), L(U['nitro_lm'], 'LaptopMedia: tela do Nitro V15')]),
    ('Software', [L(U['manim'], 'Manim: renderização'), L(U['manim019'], 'Manim 0.19'), L(U['resolve_req'], 'Resolve: requisitos'), L(U['puget_res'], 'Puget: Resolve'), L(U['puget_pr'], 'Puget: Premiere e Resolve'), L(U['wsl'], 'WSL: memória'), L(U['ollama'], 'Ollama: tamanhos de modelos')]),
    ('Preços e histórico', [L(U['zoom4050'], 'Zoom: histórico do LOQ RTX 4050'), L(U['promobit'], 'Promobit'), L(U['pelando'], 'Pelando'), L(U['ddr4_8'], 'DDR4 8 GB'), L(U['ddr5_8'], 'DDR5 8 GB'), L(U['ddr5_16a'], 'DDR5 16 GB')]),
]
for k, v in src:
    story.append(P('<b>%s:</b> %s' % (k, ' · '.join(v)), 'small'))


def build(out):
    doc = BaseDocTemplate(out, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=17 * mm,
                          title='Notebook para programação, Manim e vídeo — análise de custo-benefício',
                          author='Assistente de pesquisa', subject='Recomendação de compra de notebook, novembro de 2026')
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='f')
    doc.addPageTemplates([PageTemplate(id='p', frames=[frame], onPage=footer)])
    doc.build(story)

build(sys.argv[1])
