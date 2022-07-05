import requests


def to_str(i):
    if i<10:
        return '00'+str(i)
    if i<100:
        return '0'+str(i)
    return str(i)


def get_loop(template):
    loop = []
    with open(template,'r') as f:
        for line in f:
            if line.startswith('>>'):
                loop.append(line[2:])
    return loop


def mk_sub(i, loop, files):
    idx = to_str(i)
    subtituted = False
    with open("script/qsub_sim_template.sh",'r') as f:
        with open("data/sim_script/qsub_"+idx+".sh",'wt') as out:
            for line in f:
                if line.startswith('>>'):
                    if not subtituted:
                        for file in files:
                            for loop_line in loop:
                                #print(loop_line.replace('{000}',idx).replace('{file}',file))
                                out.write(loop_line.replace('{000}',idx).replace('{file}',file))
                    subtituted = True
                else:
                    #print(line.replace('{000}',idx).replace('{001}',idx1))
                    out.write(line.replace('{000}',idx))


def get_files():
    files = []
    for i in range(0,165):
        files.append([])
    url = "https://ftp.ncbi.nlm.nih.gov/pubchem/RDF/compound/nbr2d/"
    response = requests.get(url, stream=True)
    for ln in response.iter_lines():
        line = ln.decode('utf-8')
        if line.startswith('<a href="pc2dNbr_'):
            file = line.split('"')[1]
            index = int(file[8:11])
            files[index].append(file[:-3])
    return files


def main():
    loop = get_loop("script/qsub_sim_template.sh")
    files = get_files()
    with open("data/sim_script/qsub_all.sh",'wt') as out:
        for i in range(0,163):
            print(i, len(files[i]), sep='\t')
            mk_sub(i, loop, files[i])
            out.write("qsub data/sim_script/qsub_"+to_str(i)+".sh\n")
            out.write("sleep 15\n")


if __name__ == '__main__':
    main()
