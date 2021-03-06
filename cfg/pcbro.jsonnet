// WCT configuration support for PCB readout components
local wc = import "wirecell.jsonnet";
local g = import 'pgraph.jsonnet';

local params = import "params.jsonnet";
local tools_maker = import "pgrapher/common/tools.jsonnet";
local tools = tools_maker(params);

local sp_maker = import "sp.jsonnet";
local sp = sp_maker(params, tools);

{

    plugins: ["WireCellPcbro", "WireCellSio", "WireCellAux", "WireCellGen", "WireCellSigProc"],

    // Return a raw source configuration node to read in a .bin file
    // and produce tensors with given tag.
    rawsource(name, filename, tag="") :: g.pnode({
        type: 'PcbroRawSource',
        name: name,
        data: {
            filename: filename,
            tag: tag
        }}, nin=0, nout=1),

    // Return a tensor (sub)configuration
    tensor(tag) :: {
        tag: tag
    },

    // default is to convert only the empty string tag.
    tentoframe(name, tensors = [{}]) :: g.pnode({
        type: 'TaggedTensorSetFrame',
        name: name,
        data: {
            tensors: tensors,
        }}, nin=1, nout=1),

    // Return a numpy frame saver configuration.
    npzsink(name, filename, digitize=true, tags=[]) :: g.pnode({
        type: 'NumpyFrameSaver',
        name: name,
        data: {
            filename: filename,
            digitize: digitize,
            frame_tags: tags,
        }}, nin=1, nout=1),

    dumpframes(name) :: g.pnode({
        type: "DumpFrames",
        name: name,
    }, nin=1, nout=0),

    // Return graph to convert from pcbro .bin to .npz
    bin_npz(infile, outfile, tag="") ::
    g.pipeline([$.rawsource("input", infile, tag),
                $.tentoframe("tensor-to-frame", tensors=[$.tensor(tag)]),
                $.npzsink("output", outfile, tags=[tag]),
                $.dumpframes("dumpframes")]),


    bin_sp_npz(infile, outfile, tag="") ::
    g.pipeline([
        $.rawsource("input", infile, tag),
        $.tentoframe("tensor-to-frame", tensors=[$.tensor(tag)]),
        sp.make_sigproc(tools.anodes[0]),
        $.npzsink("output", outfile, false, tags=["gauss0", "wiener0", "threshold0"]),
        $.dumpframes("dumpframes")]),
}

