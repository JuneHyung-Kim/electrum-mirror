# Copyright (C) Dnspython Contributors, see LICENSE for text of ISC license

# Copyright (C) 2003-2007, 2009-2011 Nominum, Inc.
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose with or without fee is hereby granted,
# provided that the above copyright notice and this permission notice
# appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND NOMINUM DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL NOMINUM BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import struct

import dns.exception
import dns.rdata
import dns.tokenizer


class ISDN(dns.rdata.Rdata):

    """ISDN record"""

    # see: RFC 1183

    __slots__ = ['address', 'subaddress']

    def __init__(self, rdclass, rdtype, address, subaddress):
        super().__init__(rdclass, rdtype)
        if isinstance(address, str):
            object.__setattr__(self, 'address', address.encode())
        else:
            object.__setattr__(self, 'address', address)
        if isinstance(address, str):
            object.__setattr__(self, 'subaddress', subaddress.encode())
        else:
            object.__setattr__(self, 'subaddress', subaddress)

    def to_text(self, origin=None, relativize=True, **kw):
        if self.subaddress:
            return '"{}" "{}"'.format(dns.rdata._escapify(self.address),
                                      dns.rdata._escapify(self.subaddress))
        else:
            return '"%s"' % dns.rdata._escapify(self.address)

    @classmethod
    def from_text(cls, rdclass, rdtype, tok, origin=None, relativize=True,
                  relativize_to=None):
        address = tok.get_string()
        t = tok.get()
        if not t.is_eol_or_eof():
            tok.unget(t)
            subaddress = tok.get_string()
        else:
            tok.unget(t)
            subaddress = ''
        tok.get_eol()
        return cls(rdclass, rdtype, address, subaddress)

    def _to_wire(self, file, compress=None, origin=None, canonicalize=False):
        l = len(self.address)
        assert l < 256
        file.write(struct.pack('!B', l))
        file.write(self.address)
        l = len(self.subaddress)
        if l > 0:
            assert l < 256
            file.write(struct.pack('!B', l))
            file.write(self.subaddress)

    @classmethod
    def from_wire_parser(cls, rdclass, rdtype, parser, origin=None):
        address = parser.get_counted_bytes()
        if parser.remaining() > 0:
            subaddress = parser.get_counted_bytes()
        else:
            subaddress = b''
        return cls(rdclass, rdtype, address, subaddress)
