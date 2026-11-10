"""Minimal stand-in for the `brotli` module so fontTools can write WOFF2.
Compression is done by Node's built-in Brotli (zlib.brotliCompressSync)."""
import subprocess
MODE_GENERIC, MODE_TEXT, MODE_FONT = 0, 1, 2
__version__ = "1.1.0"
_C = ("const z=require('zlib');const c=[];process.stdin.on('data',d=>c.push(d));"
      "process.stdin.on('end',()=>{const p={};p[z.constants.BROTLI_PARAM_MODE]=%d;"
      "p[z.constants.BROTLI_PARAM_QUALITY]=%d;p[z.constants.BROTLI_PARAM_LGWIN]=%d;"
      "process.stdout.write(z.brotliCompressSync(Buffer.concat(c),{params:p}));});")
_D = ("const z=require('zlib');const c=[];process.stdin.on('data',d=>c.push(d));"
      "process.stdin.on('end',()=>{process.stdout.write(z.brotliDecompressSync(Buffer.concat(c)));});")
def compress(data, mode=MODE_GENERIC, quality=11, lgwin=22, lgblock=0):
    return subprocess.run(['node', '-e', _C % (mode, quality, lgwin)], input=bytes(data), stdout=subprocess.PIPE, check=True).stdout
def decompress(data):
    return subprocess.run(['node', '-e', _D], input=bytes(data), stdout=subprocess.PIPE, check=True).stdout
