import os
from unidecode import unidecode
import shutil
import pypandoc

VAULT_PATH = '/home/luajaz/vault'
WHITELIST = ['/matematica', '/computacao', '/estatistica']

def sub_imgs(markdown_content):
    for i in range(len(markdown_content)):
        if '.png]]' in markdown_content[i]:
            x = unidecode(markdown_content[i][3:markdown_content[i].find('.png')+4].lower().replace(' ', '_'))
            markdown_content[i] = f'<img src="/notas/images/{x}" style="center">\n'
    
    return markdown_content

def busca_path(link_page):
    for (dirpath, dirnames, filenames) in os.walk(VAULT_PATH):
        for filename in filenames:
            if filename.lower() == link_page.lower() + '.md':
                if filename[0] == "-":
                    
                    out = dirpath.replace('\\','/') + '/index.md'
                    ''
                else:
                    out = dirpath.replace('\\','/') + '/' + filename

                return(unidecode(out.lower().replace(' ', '_')))
    return None

def sub_links(markdown_content):
    i=0

    for line in markdown_content:
        inicio = 0
        fim = 0
        
        while '[[' in line:

            # isolar link
            inicio = line.find('[[')
            fim = line.find(']]') + 2

            obsidian_link = line[inicio : fim]

            # caso haja texto alternativo
            if '|' in obsidian_link:
                link_text = obsidian_link[obsidian_link.find('|') +1 : -2]
                link_page = obsidian_link[2 : obsidian_link.find('|')]

                if '^' in link_page or '#' in link_page:
                    if '^' in link_page:
                        link_page = link_page[:link_page.find('^')]
                    if '#' in link_page:
                        link_page = link_page[:link_page.find('#')]

                path_link_page = busca_path(link_page)

                if path_link_page == None:
                    line = line[:inicio] + link_page + line[fim:]

                else:
                    line = line[:inicio] + f'[{link_text}](https://luajaz.nekoweb.org/notas/{path_link_page[18:-3]}.html)' + line[fim:]

            # caso não haja texto alternativo
            else:
                link_page = obsidian_link[2:-2]

                # casos com links para seções ou parágrafos
                if '^' in link_page or '#' in link_page:
                    if '^' in link_page:
                        link_page = link_page[:link_page.find('^')]
                    if '#' in link_page:
                        link_page = link_page[:link_page.find('#')]

                path_link_page = busca_path(link_page)

                if path_link_page == None:
                    line = line[:inicio] + link_page + line[fim:]

                else:
                    line = line[:inicio] + f'[{link_page}](https://luajaz.nekoweb.org/notas/{path_link_page[18:-3]}.html)' + line[fim:]
        markdown_content[i] = line
        i+=1

    return markdown_content

def markdown_html(markdown_str, filename):
    html_template = open('template.html', 'r').read()

    # remover '-' do titulo em caso de pagina indice
    if filename[0] == '-':
        filename = filename[1:]

    html_str = pypandoc.convert_text(markdown_str, format='markdown-blank_before_header', to='html', extra_args=['--mathjax'])

    return html_template.replace('NOTE_NAME_GOES_HERE', filename[:-3].replace('_', ' ').upper()).replace('NOTE_GOES_HERE', html_str)

def generate_html():
    img_paths = {}

    for (dirpath, dirnames, filenames) in os.walk(VAULT_PATH):
        whitelisted = False
        for item in WHITELIST:
            if item in dirpath:
                whitelisted = True

        if whitelisted:
            # obter paths das imagens primeiro
            for filename in filenames:
                if '.png' in filename or '.jpg' in filename or '.jpeg' in filename:
                    filepath = dirpath + '/' + filename
                    
                    img_paths[filename] = filepath

            # obter notas
            for filename in filenames:
                if '.md' in filename:
                    # obter conteúdo em string
                    filepath = dirpath + '/' + filename
                    
                    f = open(filepath, encoding='utf-8')
                    content = f.readlines()
                    f.close()

                    if '---' in content[0]:
                        content.pop(0)
                        while '---' not in content[0]:
                            content.pop(0)
                        content.pop(0)

                    content = sub_imgs(content)
                    content = sub_links(content)

                    content_str = ''

                    for i in content:
                        content_str += i

                    # content_str = content_str.replace('<', '&lt;')
                    
                    # Fazer diretório (se não existe)
                    html_dir_path = 'notas/' + dirpath[18:].replace(' ', '_')
                    html_dir_path = unidecode(html_dir_path.lower())
                    os.makedirs(html_dir_path.lower(), exist_ok=True)

                    # criar .html
                    if filename[0] == '-':
                        html_path  =html_dir_path + '/' + 'index.html'
                    else:
                        html_path = html_dir_path + '/' + unidecode(filename[:-3].replace(' ', '_').lower()) + '.html'
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(markdown_html(content_str, filename))

    # copy images to html directories
    os.makedirs('./notas/images', exist_ok=True)

    for imgname in img_paths:
        name = unidecode(imgname.lower().replace(' ', '_'))
        shutil.copy(img_paths[imgname], f'./notas/images/{name}')
        


def main():
    generate_html()
    

if __name__ == '__main__':
    main()