'''
Main CLI to moo
'''
import os
import sys
import json
import click

@click.group()
@click.pass_context
def cli(ctx):
    '''
    wirecell-pcbro command line interface
    '''
    ctx.ensure_object(dict)

@cli.command("gen-wires")
@click.argument("output-file")
def gen_wires(output_file):
    '''Generate a "oneside wires" file.  Use "wirecell-util
    convert-oneside-wires" to turn into .json.bz2 file.

    columns:
        channel plane wire sx sy sz ex ey ez
    '''
    # 320mm x 320mm active area with 64x64 strips
    # 1.25mm hole at 2mm pitch, 2.5mm hole at 3.33 mm pitch
    # for now, we assume whole thing is the former.
    pitch = 0.2                 # cm
    

    # "physical" channels match strips and are:
    # - 1-64 for collection
    # - 65-128 for induction
    print("warning: using ideal wire spacing")
    lines = list()
    
    plane=0                     # induction
    # put collection strips pointing along Y-axis and just negative in X.
    sx = ex = +0.1              # cm, and totally bogus
    sz = -32*pitch
    ez = +32*pitch
    sy = ey = -32*pitch + 0.5*pitch
    for iwire in range(64,128):
        chan = iwire+1
        l = f'{chan:3d} {plane:1d} {iwire:3d} {sx:8.2f} {sy:8.2f} {sz:8.2f} {ex:8.2f} {ey:8.2f} {ez:8.2f}'
        lines.append(l)
        sy += pitch
        ey += pitch
        
    plane=1                     # induction
    # put collection strips pointing along Y-axis and just negative in X.
    sx = ex = +0.1              # cm, and totally bogus
    sz = -32*pitch
    ez = +32*pitch
    sy = ey = -32*pitch + 0.5*pitch
    for iwire in range(64,128):
        chan = 1000+iwire+1
        l = f'{chan:3d} {plane:1d} {iwire:3d} {sx:8.2f} {sy:8.2f} {sz:8.2f} {ex:8.2f} {ey:8.2f} {ez:8.2f}'
        lines.append(l)
        sy += pitch
        ey += pitch

    plane=2                     # collection
    # put collection strips pointing along Y-axis and just negative in X.
    sx = ex = -0.1              # cm, and totally bogus
    sy = -32*pitch
    ey = +32*pitch
    sz = ez = -32*pitch + 0.5*pitch
    for iwire in range(0,64):
        chan = iwire+1
        l = f'{chan:3d} {plane:1d} {iwire:3d} {sx:8.2f} {sy:8.2f} {sz:8.2f} {ex:8.2f} {ey:8.2f} {ez:8.2f}'
        lines.append(l)
        sz += pitch
        ez += pitch

    text = '\n'.join(lines)
    text += '\n'
    open(output_file,"wb").write(text.encode('ascii'))
    


@cli.command("plot-one")
@click.option("-T", "--tag", default="gauss0",
             help="Tag name")
@click.option("-t", "--trigger", default=31,
             help="Trigger number")
@click.option("-a","--aspect", default=1.0,
              help="Aspect ratio")
@click.option("-o","--output",default="plot.pdf",
              help="Output file")
@click.argument("npzfile")
def plot_one(tag, trigger, aspect, output, npzfile):
    '''
    Plot waveforms of a trigger from file
    '''
    import numpy
    import matplotlib.pyplot as plt 
    fp = numpy.load(npzfile)
    a = fp[f'frame_{tag}_{trigger}']
    rows, cols = a.shape;
    # a = numpy.flip(a,0)
    plt.imshow(a, aspect=aspect, interpolation=None)
    plt.plot((cols//2, cols//2), (0, rows-1), linewidth=0.1, color='red')
    c = plt.colorbar()
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(output, bbox_inches='tight')

@cli.command("plot-many")
@click.option("-a","--aspect", default=1.0,
              help="Aspect ratio")
@click.option("-o","--output",default="plot.pdf",
              help="Output file")
@click.argument("npzfile")
def plot_many(aspect, output, npzfile):
    '''
    Plot waveforms of a trigger from file
    '''
    import numpy
    import matplotlib.pyplot as plt 
    from matplotlib.backends.backend_pdf import PdfPages
    fp = numpy.load(npzfile)
    print (list(fp.keys()))

    with PdfPages(output) as pdf:
        for k in fp.keys():
            print (k)
            if not k.startswith("frame_"):
                continue;
            a = fp[k]
            rows, cols = a.shape;
            # a = numpy.flip(a,0)
            fig, ax = plt.subplots(nrows=1, ncols=1)
            plt.imshow(a, aspect=aspect, interpolation=None)
            plt.plot((cols//2, cols//2), (0, rows-1), linewidth=0.1, color='red')
            c = plt.colorbar()
            plt.gca().invert_yaxis()
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()


@cli.command("activity")
@click.option("-t", "--threshold", default=5000,
             help="Threshold on the sum of values above minimum")
@click.option("-m", "--minimum", default=5,
             help="Minimum sample value to be included in sum")
@click.argument("npzfile")
@click.argument("npzout")
def activity(tag, trigger, npzfile, npzout):
    import numpy
    fp = numpy.load(npzfile)
    arrays = dict()
    for k in fp.keys():
        if not k.startswith("frame_"):
            continue
        a = fp[k]
        rows,cols = a.shape
        c = a[:,:cols//2]
        cn = numpy.array(c - numpy.median(c, axis=0))
        act = numpy.sum(cn[cn>5])
        if act < 5000.0:
            continue
        arrays[k] = a
        print (f'save {k}')
    numpy.savez(npzout, **arrays)
        

def main():
    cli(obj=dict())

if '__main__' == __name__:
    main()
    
