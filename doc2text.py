#doc2text module:
"""
This is Python implementation of C# algorithm proposed in:
http://b2xtranslator.sourceforge.net/howtos/How_to_retrieve_text_from_a_binary_doc_file.pdf

Python implementation author is Dalen Bernaca.
Code needs refining and probably bug fixing!
As I am not a C# expert I would like some code rechecks by one.
Parts of which I am uncertain are:
    * Did the author of original algorithm used uint32 and int32 when unpacking correctly?
      I copied each occurence as in original algo.
    * Is the FIB length for MS Word 97 1472 bytes as in MS Word 2000, and would it make any difference if it is not?
    * Did I interpret each C# command correctly?
      I think I did!
"""

from compoundfiles import CompoundFileReader, CompoundFileError
from struct import unpack

__all__ = ["doc2text"]

def doc2text (path):
    text = u""
    cr = CompoundFileReader(path)
    # Load WordDocument stream:
    try:
        f = cr.open("WordDocument")
        doc = f.read()
        f.close()
    except: 
        cr.close()
        raise CompoundFileError("The file is corrupted or it is not a Word document at all.")
    # Extract file information block and piece table stream informations from it:
    fib = doc[:1472]
    fcClx  = unpack("L", fib[0x01a2:0x01a6])[0]
    lcbClx = unpack("L", fib[0x01a6:0x01a6+4])[0]
    tableFlag = unpack("L", fib[0x000a:0x000a+4])[0] & 0x0200 == 0x0200
    tableName = ("0Table", "1Table")[tableFlag]
    # Load piece table stream:
    try:
        f = cr.open(tableName)
        table = f.read()
        f.close()
    except: 
        cr.close()
        raise CompoundFileError("The file is corrupt. '%s' piece table stream is missing." % tableName)
    cr.close()
    # Find piece table inside a table stream:
    clx = table[fcClx:fcClx+lcbClx]
    pos = 0
    pieceTable = ""
    lcbPieceTable = 0
    while True:
        if clx[pos]=="\x02":
            # This is piece table, we store it:
            lcbPieceTable = unpack("l", clx[pos+1:pos+5])[0]
            pieceTable = clx[pos+5:pos+5+lcbPieceTable]
            break
        elif clx[pos]=="\x01":
            # This is beggining of some other substructure, we skip it:
            pos = pos+1+1+ord(clx[pos+1])
        else: 
            break
    if not pieceTable: 
        raise CompoundFileError("The file is corrupt. Cannot locate a piece table.")
    # Read info from pieceTable, about each piece and extract it from WordDocument stream:
    pieceCount = (lcbPieceTable-4)/12
    for x in xrange(pieceCount):
        cpStart = unpack("l", pieceTable[x*4:x*4+4])[0]
        cpEnd   = unpack("l", pieceTable[(x+1)*4:(x+1)*4+4])[0]
        ofsetDescriptor = ((pieceCount+1)*4)+(x*8)
        pieceDescriptor = pieceTable[ofsetDescriptor:ofsetDescriptor+8]
        fcValue = unpack("L", pieceDescriptor[2:6])[0]
        isANSII = (fcValue & 0x40000000) == 0x40000000
        fc      = fcValue & 0xbfffffff
        cb = cpEnd-cpStart
        enc = ("utf-16", "cp1252")[isANSII]
        cb = (cb*2, cb)[isANSII]
        text += doc[fc:fc+cb].decode(enc, "ignore")
    return "\n".join(text.splitlines())
